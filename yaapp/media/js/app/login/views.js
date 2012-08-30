/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Views');

Yasound.Views.LoginPage = Backbone.View.extend({
    events: {
        'submit #login-form': 'submit'
    },

    initialize: function() {
        _.bindAll(this, 'render', 'templateLoaded', 'submit');
    },

    onClose: function() {},

    reset: function() {},

    render: function() {
        this.reset();
        ich.loadRemoteTemplate('login/login.mustache', 'loginPageTemplate', this.templateLoaded);
        return this;
    },

    templateLoaded: function() {
        $(this.el).html(ich.loginPageTemplate());
        $("select", this.el).uniform({});
    },

    submit: function(e) {
        e.preventDefault();
        var form = $('#login-form', this.el);
        $('.error-msg', form).remove();
        $('input').removeClass('error');

        var url = window.location.href;
        $.post(url, form.serializeArray(), function(data) {
            var success = data.success;
            if (!data.success) {
                colibri(gettext('Login error'));
                var errors = data.errors;
                if (errors) {
                    _.each(errors, function(value, key) {
                        var $input = $('input[name=' + key + ']', form);
                        $input.addClass('error');
                        $input.after('<div class="error-msg">' + value + '</div>');
                    });
                }
            } else {
                window.location = '/app/';
            }
        }).error(function() {
            colibri(gettext('Error while login in'), 'colibri-error');
        });
    }
});
