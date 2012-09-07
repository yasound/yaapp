/*
 * jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true,
 * evil: true, undef: true, white: true, newcap: true
 */
/* extern Ext, $ */

Namespace('Yasound.Views');

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