"""Default tags used by the template system, available to all templates."""

import sys
import re
from itertools import groupby, cycle as itertools_cycle

from django.template.base import Node, NodeList, Template, Context, Variable
from django.template.base import TemplateSyntaxError, VariableDoesNotExist, BLOCK_TAG_START, BLOCK_TAG_END, VARIABLE_TAG_START, VARIABLE_TAG_END, SINGLE_BRACE_START, SINGLE_BRACE_END, COMMENT_TAG_START, COMMENT_TAG_END
from django.template.base import get_library, Library, InvalidTemplateLibrary
from django.template.smartif import IfParser, Literal
from django.conf import settings
from django.utils.encoding import smart_str, smart_unicode
from django.utils.safestring import mark_safe
from localeurl import utils as localeurl_utils

register = Library()
# Regex for token keyword arguments
kwarg_re = re.compile(r"(?:(\w+)=)?(.+)")

def token_kwargs(bits, parser, support_legacy=False):
    """
    A utility method for parsing token keyword arguments.

    :param bits: A list containing remainder of the token (split by spaces)
        that is to be checked for arguments. Valid arguments will be removed
        from this list.

    :param support_legacy: If set to true ``True``, the legacy format
        ``1 as foo`` will be accepted. Otherwise, only the standard ``foo=1``
        format is allowed.

    :returns: A dictionary of the arguments retrieved from the ``bits`` token
        list.

    There is no requirement for all remaining token ``bits`` to be keyword
    arguments, so the dictionary will be returned as soon as an invalid
    argument format is reached.
    """
    if not bits:
        return {}
    match = kwarg_re.match(bits[0])
    kwarg_format = match and match.group(1)
    if not kwarg_format:
        if not support_legacy:
            return {}
        if len(bits) < 3 or bits[1] != 'as':
            return {}

    kwargs = {}
    while bits:
        if kwarg_format:
            match = kwarg_re.match(bits[0])
            if not match or not match.group(1):
                return kwargs
            key, value = match.groups()
            del bits[:1]
        else:
            if len(bits) < 3 or bits[1] != 'as':
                return kwargs
            key, value = bits[2], bits[0]
            del bits[:3]
        kwargs[key] = parser.compile_filter(value)
        if bits and not kwarg_format:
            if bits[0] != 'and':
                return kwargs
            del bits[:1]
    return kwargs

class URLNode(Node):
    def __init__(self, view_name, args, kwargs, asvar, legacy_view_name=True):
        self.view_name = view_name
        self.legacy_view_name = legacy_view_name
        self.args = args
        self.kwargs = kwargs
        self.asvar = asvar

    def render(self, context):
        from django.core.urlresolvers import reverse, NoReverseMatch
        args = [arg.resolve(context) for arg in self.args]
        kwargs = dict([(smart_str(k, 'ascii'), v.resolve(context))
                       for k, v in self.kwargs.items()])

        view_name = self.view_name
        if not self.legacy_view_name:
            view_name = view_name.resolve(context)

        # Try to look up the URL twice: once given the view name, and again
        # relative to what we guess is the "main" app. If they both fail,
        # re-raise the NoReverseMatch unless we're using the
        # {% url ... as var %} construct in which cause return nothing.
        url = ''
        try:
            url = reverse(view_name, args=args, kwargs=kwargs, current_app=context.current_app)
        except NoReverseMatch, e:
            if settings.SETTINGS_MODULE:
                project_name = settings.SETTINGS_MODULE.split('.')[0]
                try:
                    url = reverse(project_name + '.' + view_name,
                              args=args, kwargs=kwargs,
                              current_app=context.current_app)
                except NoReverseMatch:
                    if self.asvar is None:
                        # Re-raise the original exception, not the one with
                        # the path relative to the project. This makes a
                        # better error message.
                        raise e
            else:
                if self.asvar is None:
                    raise e

        language, stripped_url = localeurl_utils.strip_path(url)
        if stripped_url.startswith('/app/'):
            stripped_url = stripped_url[len('/app/'):]
        if len(stripped_url) > 0 and stripped_url[0] != '/':
            stripped_url = '/' + stripped_url

        url = localeurl_utils.locale_url(stripped_url, language)

        if self.asvar:
            context[self.asvar] = url
            return ''
        else:
            return url


def app_url(parser, token):
    """
    Returns an absolute URL matching given view with its parameters.

    This is a way to define links that aren't tied to a particular URL
    configuration::

        {% url path.to.some_view arg1 arg2 %}

        or

        {% url path.to.some_view name1=value1 name2=value2 %}

    The first argument is a path to a view. It can be an absolute python path
    or just ``app_name.view_name`` without the project name if the view is
    located inside the project.  Other arguments are comma-separated values
    that will be filled in place of positional and keyword arguments in the
    URL. All arguments for the URL should be present.

    For example if you have a view ``app_name.client`` taking client's id and
    the corresponding line in a URLconf looks like this::

        ('^client/(\d+)/$', 'app_name.client')

    and this app's URLconf is included into the project's URLconf under some
    path::

        ('^clients/', include('project_name.app_name.urls'))

    then in a template you can create a link for a certain client like this::

        {% url app_name.client client.id %}

    The URL will look like ``/clients/client/123/``.
    """

    import warnings
    warnings.warn('The syntax for the url template tag is changing. Load the `url` tag from the `future` tag library to start using the new behavior.',
                  category=PendingDeprecationWarning)

    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument"
                                  " (path to a view)" % bits[0])
    viewname = bits[1]
    args = []
    kwargs = {}
    asvar = None
    bits = bits[2:]
    if len(bits) >= 2 and bits[-2] == 'as':
        asvar = bits[-1]
        bits = bits[:-2]

    # Backwards compatibility: check for the old comma separated format
    # {% url urlname arg1,arg2 %}
    # Initial check - that the first space separated bit has a comma in it
    if bits and ',' in bits[0]:
        check_old_format = True
        # In order to *really* be old format, there must be a comma
        # in *every* space separated bit, except the last.
        for bit in bits[1:-1]:
            if ',' not in bit:
                # No comma in this bit. Either the comma we found
                # in bit 1 was a false positive (e.g., comma in a string),
                # or there is a syntax problem with missing commas
                check_old_format = False
                break
    else:
        # No comma found - must be new format.
        check_old_format = False

    if check_old_format:
        # Confirm that this is old format by trying to parse the first
        # argument. An exception will be raised if the comma is
        # unexpected (i.e. outside of a static string).
        match = kwarg_re.match(bits[0])
        if match:
            value = match.groups()[1]
            try:
                parser.compile_filter(value)
            except TemplateSyntaxError:
                bits = ''.join(bits).split(',')

    # Now all the bits are parsed into new format,
    # process them as template vars
    if len(bits):
        for bit in bits:
            match = kwarg_re.match(bit)
            if not match:
                raise TemplateSyntaxError("Malformed arguments to url tag")
            name, value = match.groups()
            if name:
                kwargs[name] = parser.compile_filter(value)
            else:
                args.append(parser.compile_filter(value))

    return URLNode(viewname, args, kwargs, asvar, legacy_view_name=True)
app_url = register.tag(app_url)

