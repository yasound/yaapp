/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Views');

Yasound.Views.SignupPage = Backbone.View.extend({
    events: {
        'submit #signup-form': 'submit'
    },

    initialize: function() {
        _.bindAll(this, 'render', 'templateLoaded', 'submit');
    },

    onClose: function() {},

    reset: function() {},

    render: function() {
        this.reset();
        ich.loadRemoteTemplate('signup/signup.mustache', 'signupPageTemplate', this.templateLoaded);
        return this;
    },

    templateLoaded: function() {
        $(this.el).html(ich.signupPageTemplate());
    },

    submit: function(e) {
        e.preventDefault();
        var form = $('#signup-form', this.el);
        $('.error-msg', form).remove();
        $('input').removeClass('error');

        var url = window.location.href;
        $.post(url, form.serializeArray(), function(data) {
            var success = data.success;
            if (!data.success) {
                colibri(gettext('Registration error'));
                var errors = data.errors;
                if (errors) {
                    _.each(errors, function(value, key) {
                        var $input = $('input[name=' + key + ']', form);
                        $input.addClass('error');
                        $input.after('<div class="error-msg">' + value + '</div>');
                    })
                }
            } else {
                $('#modal-after-signup').modal('show');
                $('#modal-after-signup').one('hidden', function () {
                    window.location = '/app/';
                });
            }
        }).error(function() {
            colibri(gettext('Error while creating account', 'colibri-error'));
        });
    }
});