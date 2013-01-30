/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Views');

Yasound.Views.PassResetPage = Backbone.View.extend({
    events: {
        'submit #passreset-form': 'submit',
        'click #signup-now': 'onSignup'
    },

    initialize: function() {
        _.bindAll(this,
            'render',
            'templateUrl',
            'templateName',
            'templateLoaded',
            'submit'
        );
    },

    onClose: function() {},

    reset: function() {},

    templateUrl: function (page) {
        return 'passreset/' + page + '.mustache';
    },

    templateName: function (page) {
        return 'static' + page + 'Template';
    },

    render: function() {
        this.reset();
        ich.loadRemoteTemplate(this.templateUrl('passreset'), this.templateName('passreset'), this.templateLoaded);
        return this;
    },

    templateLoaded: function() {
        var page = this.page;
        $(this.el).html(ich[this.templateName('passreset')]());
    },

    submit: function (e) {
        e.preventDefault();
        var form = $('#passreset-form', this.el);
        $('.error-msg', form).remove();
        $('input').removeClass('error');

        var button = $("input[type='submit']", form);
        button.attr('disabled', 'disabled');

        var url = window.location.href;
        $.post(url, form.serializeArray(), function(data) {
            var success = data.success;
            if (!data.success) {
                var text = gettext('Error');
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
                $('#modal-after-passreset').modal('show');
                $('#modal-after-passreset').one('hidden', function () {
                    Yasound.App.Router.navigate("login/", {
                        trigger: true
                    });
                });
            }
        }).error(function() {
            colibri(gettext('Error', 'colibri-error'));
            button.removeAttr('disabled');
        });
    },

    onSignup: function (e) {
        e.preventDefault();
        Yasound.App.Router.navigate("signup/", {
            trigger: true
        });
    }
});
