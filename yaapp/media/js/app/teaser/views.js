/*
 * jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true,
 * evil: true, undef: true, white: true, newcap: true
 */
/* extern Ext, $ */

Namespace('Yasound.Views');

Yasound.Views.Teaser = Backbone.View.extend({
    el: '#hommage',
    events: {
        // 'click #teaser-signup-later-btn'    : 'slideUp',
        // 'click #teaser-signup-now-btn'      : 'signup',
        // 'click #teaser-listen p a'          : 'listen',
        // 'click #teaser-create p a'          : 'create',
        // 'click #teaser-share p a'           : 'share'
    },

    initialize: function() {
        _.bindAll(this, 'render');
    },

    render: function() {
        if (Yasound.App.isMobile) {
            return;
        }

        $('#teaser-bg').show();
        $('#teaser').show();
        return this;
    },

    slideUp: function (e) {
        if (e) {
            e.preventDefault();
            cookies.set('hideteaser', true);
        }
        $('#hommage-bg').hide();
        this.$el.hide();
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
    },

    signup: function (e) {
        e.preventDefault();
        Yasound.App.Router.navigate('signup/', {
            trigger: true
        });
    }
});