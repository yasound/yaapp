/*
 * jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true,
 * evil: true, undef: true, white: true, newcap: true
 */
/* extern Ext, $ */
Namespace('Yasound.Views');

/**
 * Home page
 */
Yasound.Views.SettingsPage = Backbone.View.extend({
    events: {
        'click #btn-remove-facebook': 'removeFacebook',
        'click #btn-remove-twitter': 'removeTwitter',
        'submit #settings-facebook-form': 'submitFacebook',
        'submit #settings-twitter-form': 'submitTwitter',
        'click #my-informations-menu': 'onInformationsMenu',
        'click #my-accounts-menu': 'onAccountsMenu',
        'click #my-notifications-menu': 'onNotificationsMenu',

        "submit #my-informations-form": "onSubmitMyInformations",
        "submit #my-accounts-form": "onSubmitMyAccounts"

    },
    initialize: function () {
        _.bindAll(this, 'render', 'templateLoaded');
    },

    onClose: function () {
    },

    reset: function () {
    },

    render: function () {
        this.reset();
        // the {} attribute makes the template not cacheable
        ich.loadRemoteTemplate('settings/settingsPage.mustache', 'settingsPageTemplate', this.templateLoaded, {});
        return this;
    },

    templateLoaded: function() {
        $(this.el).html(ich.settingsPageTemplate());
        $("select", this.el).uniform({});
        $('#id_birthday').datepicker({
            format: gettext('mm/dd/yyyy'),
            language: Yasound.App.LanguageCode
        });



        var that = this;
        var $progress = $('#progress .bar', this.el);
        $progress.parent().hide();
        $('#file-upload').fileupload({
            dataType: 'json',
            add: function (e, data) {
                $progress.parent().show();
                data.submit();
            },
            progressall: function (e, data) {
                var progress = parseInt( (data.loaded*100) / data.total, 10);
                $progress.css('width', progress + '%');
            },

            done: function (e, data) {
                var result = data.result[0];
                if (result.error) {
                    var error = result.error;
                    $('#modal-upload-error .modal-body p', that.el).html(error);
                    $('#modal-upload-error', that.el).modal('show');
                } else {
                    var url = result.url;
                    var now = moment();
                    url = url + '?' + now.unix();
                    $('#user-picture-image', that.el).attr('src', url);
                }
                $progress.css('width', '0%');
                $progress.parent().hide();
            },
            fail: function (e, data) {
            }
        });



        return this;
    },
    removeFacebook: function (e) {
        e.preventDefault();
        $('#modal-remove-facebook').modal('show');
        $('#modal-remove-facebook .btn-primary').one('click', function () {
            $('#modal-remove-facebook').modal('hide');
            $('#btn-remove-facebook').attr('id', 'foo').trigger('click');
        });
        return false;
    },

    removeTwitter: function (e) {
        e.preventDefault();
        $('#modal-remove-twitter').modal('show');
        $('#modal-remove-twitter .btn-primary').one('click', function () {
            $('#modal-remove-twitter').modal('hide');
            $('#btn-remove-twitter').attr('id', 'foo').trigger('click');
        });
        return false;
    },
    submitFacebook: function(e) {
        e.preventDefault();
        var form = $('#settings-facebook-form', this.el);
        var url = window.location.href;
        $.post(url, form.serializeArray(), function() {
            colibri(gettext('Facebook settings saved'));
        }).error(function() {
            colibri(gettext('Error while saving Facebook settings'), 'colibri-error');
        });
    },
    submitTwitter: function(e) {
        e.preventDefault();
        var form = $('#settings-twitter-form', this.el);
        var url = window.location.href;
        $.post(url, form.serializeArray(), function() {
            colibri(gettext('Twitter settings saved'));
        }).error(function() {
            colibri(gettext('Error while saving Twitter settings'), 'colibri-error');
        });
    },

    onInformationsMenu: function (e) {
        e.preventDefault();

        $('#settings-nav li', this.el).removeClass('checked');
        $('#settings-nav #my-informations-menu', this.el).addClass('checked');

        $('#my-notifications', this.el).hide();
        $('#my-accounts', this.el).hide();

        if (Yasound.App.enableFX) {
            $('#my-informations', this.el).fadeIn(200);
        } else {
            $('#my-informations', this.el).show();
        }
    },

    onAccountsMenu: function (e) {
        e.preventDefault();
        $('#settings-nav li', this.el).removeClass('checked');
        $('#settings-nav #my-accounts-menu', this.el).addClass('checked');

        $('#my-notifications', this.el).hide();
        $('#my-informations', this.el).hide();
        if (Yasound.App.enableFX) {
            $('#my-accounts', this.el).fadeIn(200);
        } else {
            $('#my-accounts', this.el).show();
        }
    },

    onNotificationsMenu: function (e) {
        e.preventDefault();
        $('#settings-nav li', this.el).removeClass('checked');
        $('#settings-nav #my-notifications-menu', this.el).addClass('checked');

        $('#my-informations', this.el).hide();
        $('#my-accounts', this.el).hide();
        if (Yasound.App.enableFX) {
            $('#my-notifications', this.el).fadeIn(200);
        } else {
            $('#my-notifications', this.el).show();
        }
    },

    onSubmitMyInformations: function (e) {
        e.preventDefault();
        var form = $('#my-informations-form', this.el);
        Yasound.Utils.submitForm({
            form: form,
            successMessage: gettext('Settings updated'),
            errorMessage: gettext('Error while saving settings')
        });
    },

    onSubmitMyAccounts: function (e) {
        e.preventDefault();
        var form = $('#my-accounts-form', this.el);
        Yasound.Utils.submitForm({
            form: form,
            successMessage: gettext('Settings updated'),
            errorMessage: gettext('Error while saving settings')
        });
    },

    onSubmitMyNotifications: function (e) {
        e.preventDefault();
        var form = $('#my-notifications-form', this.el);
        Yasound.Utils.submitForm({
            form: form,
            successMessage: gettext('Settings updated'),
            errorMessage: gettext('Error while saving settings')
        });
    }


});