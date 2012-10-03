/*
 * jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true,
 * evil: true, undef: true, white: true, newcap: true
 */
/* extern Ext, $ */

Namespace('Yasound.Views');

Yasound.Views.Teaser = Backbone.View.extend({
    el: '#teaser',
    events: {
        'click #close-btn'           : 'slideUp',
        'click #teaser-listen p a'    : 'listen',
        'click #teaser-create p a'    : 'create',
        'click #teaser-share p a'     : 'share'
    },

    initialize: function() {
        _.bindAll(this, 'render');
    },

    render: function() {
        if (!Yasound.App.isMobile) {
            $('#close-btn-container', this.el).addClass('auto-hide');
        }
        return this;
    },

    slideUp: function (e) {
        if (e) {
            e.preventDefault();
        }
        this.$el.slideUp();
    },

    listen: function (e) {
        e.preventDefault();
        Yasound.App.Router.navigate('top/', {
            trigger: true
        });
    },

    create: function (e) {
        e.preventDefault();
        Yasound.App.Router.navigate('radios/', {
            trigger: true
        });
    },

    share: function (e) {
        e.preventDefault();
        Yasound.App.Router.navigate('friends/', {
            trigger: true
        });
    }
});