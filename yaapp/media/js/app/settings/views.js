"use strict";
/*
 * jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true,
 * evil: true, undef: true, white: true, newcap: true
 */
/* extern Ext, $ */
Namespace('Yasound.Data.Views');

/**
 * Home page
 */
Yasound.Views.SettingsPage = Backbone.View.extend({
    events: {
        'click #btn-remove-facebook': 'removeFacebook',
        'click #btn-remove-twitter': 'removeTwitter',
    },
    initialize: function () {
        _.bindAll(this, 'render');
    },

    onClose: function () {
    },

    reset: function () {
    },

    render: function () {
        this.reset();
        $(this.el).html(ich.settingsPageTemplate());
        return this;
    },
    removeFacebook: function (e) {
        e.preventDefault();
        $('#modal-remove-facebook').modal('show');
        $('#modal-remove-facebook .btn-primary').on('click', function () {
            $('#modal-remove-facebook').modal('hide');
            $('#btn-remove-facebook').attr('id', 'foo').trigger('click');
        });
        return false;
    },
    
    removeTwitter: function (e) {
        e.preventDefault();
        $('#modal-remove-twitter').modal('show');
        $('#modal-remove-twitter .btn-primary').on('click', function () {
            $('#modal-remove-twitter').modal('hide');
            $('#btn-remove-twitter').attr('id', 'foo').trigger('click');
        });
        return false;
    }
});