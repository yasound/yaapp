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
        $("#mobile-menu-content").toggle();
        $("#mobile-menu-content").siblings().toggle();
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
        $("#mobile-menu-content-logo").toggle();
        $("#mobile-menu-content-logo").siblings().toggle();
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

    toggleMenuLogo: function (e) {
        e.preventDefault();
        $("#mobile-menu-content").toggle();
        $("#mobile-menu-content").siblings().toggle();
    }
});


