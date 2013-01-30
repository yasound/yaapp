/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Views');

Yasound.Views.LoginPage = Backbone.View.extend({
    events: {
        'submit #login-form': 'submit',
        'click #signup-now': 'onSignup',
        'click #lost-password': 'onPassReset'
    },

    initialize: function() {
        _.bindAll(this, 'render', 'submit');
    },

    onClose: function() {},

    reset: function() {},

    render: function() {
        this.reset();
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
                window.location = Yasound.App.root;
            }
        }).error(function() {
            colibri(gettext('Error while login in'), 'colibri-error');
        });
    },

    onSignup: function (e) {
        e.preventDefault();
        Yasound.App.Router.navigate("signup/", {
            trigger: true
        });
    },

    onPassReset: function (e) {
        e.preventDefault();
        Yasound.App.Router.navigate("lostpassword/", {
            trigger: true
        });
    }
});
