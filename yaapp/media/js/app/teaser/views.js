/*
 * jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true,
 * evil: true, undef: true, white: true, newcap: true
 */
/* extern Ext, $ */

Namespace('Yasound.Views');

Yasound.Views.Teaser = Backbone.View.extend({
    el: '.teaser',
    events: {
        'click a.teaser-close': 'slideUp'
    },

    initialize: function() {
        _.bindAll(this, 'render');
    },

    render: function() {
        if (Yasound.App.isMobile) {
            return;
        }
        this.$el.show();
        return this;
    },

    slideUp: function (e) {
        if (e) {
            e.preventDefault();
            cookies.set('hideteaser', true);
        }
        this.$el.slideUp();
    }
});