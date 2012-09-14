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
    el: '#mobile-menu',
    events: {
        "click #mobile-menu-btn": "toggleMenu"
    },

    initialize: function() {
        _.bindAll(this, 'render');
    },

    onClose: function() {
    },

    render: function() {
        return this;
    },

    toggleMenu: function (e) {
        e.preventDefault();
        var menu = $("#mobile-menu-content");
        $('html, body').animate({scrollTop: 0}, 400);
        if (menu.is(':visible')) {
            $('#webapp-content').show();
        } else {
            menu.siblings().hide();
        }
        menu.toggle();
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

    onClose: function() {
    },

    render: function() {
        return this;
    },

    toggleMenu: function (e) {
        e.preventDefault();
        var menu = $("#mobile-menu-content-logo");
        $('html, body').animate({scrollTop: 0}, 400);
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

    onClose: function() {
    },

    render: function() {
        return this;
    },

    toggleMenu: function (e) {
        e.preventDefault();
        $('html, body').animate({scrollTop: 0}, 400);
        var menu = $("#mobile-menu-content-share");
        if (menu.is(':visible')) {
            $('#webapp-content').show();
        } else {
            menu.siblings().hide();
        }
        menu.toggle();
    }
});


