/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Views');

Yasound.Views.SignupPage = Backbone.View.extend({
    events: {
        'submit #signup-form': 'submit',
        'click .login': 'onLogin'
    },

    initialize: function() {
        _.bindAll(this, 'render', 'submit');
    },

    onClose: function() {},

    reset: function() {},

    render: function() {
        this.reset();
        $(this.el).html(ich.signupPageTemplate());
    },

    submit: function(e) {
        e.preventDefault();
        var form = $('#signup-form', this.el);
        $('.error-msg', form).remove();
        $('input').removeClass('error');

        var button = $("input[type='submit']", form);
        button.attr('disabled', 'disabled');

        var url = window.location.href;
        $.post(url, form.serializeArray(), function(data) {
            var success = data.success;
            if (!data.success) {
                var text = gettext('Registration error');
                var errors = data.errors;
                if (errors) {
                    _.each(errors, function(value, key) {
                        var $input = $('input[name=' + key + ']', form);
                        $input.addClass('error');
                        text =  text + '<br/><br/>' + '<strong>' + value + '</strong>';
                    });
                }
                colibri(text);
                button.removeAttr('disabled');
            } else {
                button.removeAttr('disabled');
                $('#modal-after-signup').modal('show');
                $('#modal-after-signup').one('hidden', function () {
                    Yasound.App.Router.navigate("login/", {
                        trigger: true
                    });
                });
            }
        }).error(function() {
            colibri(gettext('Error while creating account', 'colibri-error'));
            button.removeAttr('disabled');
        });
    },

    onLogin: function (e) {
        e.preventDefault();
        Yasound.App.Router.navigate("login/", {
            trigger: true
        });
    }
});