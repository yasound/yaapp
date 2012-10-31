from django.core.mail import EmailMultiAlternatives
from django.utils.translation import ugettext as _
from django.template.defaultfilters import striptags


def send_mail(from_email, to, subject, content, content_html=None, include_yasound_footer=True):
    """Convenient function to send email in text & html and with additional footer promoting Yasound
    """

    if content == '':
        return

    content = striptags(content)

    if content_html is None:
        content_html = content

    if include_yasound_footer:
        content = content + '\n\n' + _("With Yasound (https://yasound.com), there's no need to listen to music alone anymore. Create your own radio station instantly and share with your friends in real time online and on your phone.")
        content_html = content_html + '<br/><br/>' + _("With <a href='https://yasound.com'>Yasound</a>, there's no need to listen to music alone anymore. Create your own radio station instantly and share with your friends in real time online and on your phone.")
    msg = EmailMultiAlternatives(subject, content, from_email, [to])
    msg.attach_alternative(content_html, "text/html")
    msg.send()
