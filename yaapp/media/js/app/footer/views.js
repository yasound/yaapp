/*
 * jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true,
 * evil: true, undef: true, white: true, newcap: true
 */
/* extern Ext, $ */

Namespace('Yasound.Views');

Yasound.Views.Footer = Backbone.View.extend({
    el: '.footer-player',

    events: {
        'click .toggler': 'toggleMiniPlayer'
    },

    initialize: function () {
    },

    onClose: function () {
    },

    render: function () {
        return this;
    },

    toggleMiniPlayer: function (e) {
        e.preventDefault();
        this.$el.toggleClass('mini');
    }
});
