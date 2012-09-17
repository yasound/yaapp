/*
 * jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true,
 * evil: true, undef: true, white: true, newcap: true
 */
/* extern Ext, $ */

Namespace('Yasound.Views');


/**
 * Settings Menu
 */

Yasound.Views.MobileMenu = Backbone.View.extend({
    el: '#mobile-menu-content',
    events: {
        "click #phone-menu-profile": "myProfile",
        "click #phone-menu-myradios": "myRadios",
        "click #phone-menu-notifications": "notifications",
        "click #phone-menu-gifts": "gifts",
        "click #phone-menu-mysettings": "mySettings",
        "click #phone-menu-signout": "logout"
    },

    initialize: function() {
        _.bindAll(this, 'render', 'toggleMenu');
    },

    onClose: function() {},

    render: function() {
        $('#mobile-menu-btn').on('click', this.toggleMenu);
        return this;
    },

    toggleMenu: function(e) {
        e.preventDefault();
        var menu = $("#mobile-menu-content");
        $('html, body').animate({
            scrollTop: 0
        }, 400);
        if (menu.is(':visible')) {
            $('#webapp-content').show();
        } else {
            menu.siblings().hide();
        }
        menu.toggle();
    },

    goTo: function(e, url) {
        e.preventDefault();
        Yasound.App.Router.navigate(url, {
            trigger: true
        });
        this.$el.hide();
    },

    myRadios: function(e) {
        this.goTo(e, 'radios/');
    },

    myProfile: function(e) {
        this.goTo(e, 'profile/' + Yasound.App.username + '/');
    },

    mySettings: function(e) {
        this.goTo(e, 'settings/');
    },

    notifications: function(e) {
        this.goTo(e, 'notifications/');
    },

    gifts: function(e) {
        this.goTo(e, 'gifts/');
    },

    logout: function(e) {
        window.location = '/logout';
    }
});

/**
 * Logo Menu
 */

Yasound.Views.MobileMenuLogo = Backbone.View.extend({
    el: '#mobile-menu-logo',
    events: {
        "click #mobile-menu-btn-logo": "toggleMenu"
    },

    initialize: function() {
        _.bindAll(this, 'render');
    },

    onClose: function() {},

    render: function() {
        return this;
    },

    toggleMenu: function(e) {
        e.preventDefault();
        var menu = $("#mobile-menu-content-logo");
        $('html, body').animate({
            scrollTop: 0
        }, 400);
        if (menu.is(':visible')) {
            $('#webapp-content').show();
        } else {
            menu.siblings().hide();
        }
        menu.toggle();
    }
});

/**
 * Share Menu
 */

Yasound.Views.MobileMenuShare = Backbone.View.extend({
    el: '#mobile-menu-share',
    events: {
        "click #responsive-share-btn": "toggleMenu"
    },

    initialize: function() {
        _.bindAll(this, 'render');
    },

    onClose: function() {},

    render: function() {
        return this;
    },

    toggleMenu: function(e) {
        e.preventDefault();
        $('html, body').animate({
            scrollTop: 0
        }, 400);
        var menu = $("#mobile-menu-content-share");
        if (menu.is(':visible')) {
            $('#webapp-content').show();
        } else {
            menu.siblings().hide();
        }
        menu.toggle();
    }
});