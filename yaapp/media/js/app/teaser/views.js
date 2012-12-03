/*
 * jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true,
 * evil: true, undef: true, white: true, newcap: true
 */
/* extern Ext, $ */

Namespace('Yasound.Views');

Yasound.Views.Teaser = Backbone.View.extend({
    el: '.teaser',
    events: {
        'click a.teaser-close': 'slideUp',
        'mouseover .paginate a': 'onArgumentChanged',
        'click .paginate a': 'onArgumentChanged'
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
    },

    onArgumentChanged: function(e) {
        e.preventDefault();

        var paginateLinks = this.$('.paginate a'),
            args = this.$('.argument'),
            newIndex = $(e.currentTarget).text(),
            oldIndex = paginateLinks.filter('.active').text();

        if(newIndex === oldIndex) {
            return;
        }

        $(paginateLinks[oldIndex-1]).removeClass('active');
        $(paginateLinks[newIndex-1]).addClass('active');
        $(args[newIndex-1]).addClass('show');
        $(args[oldIndex-1]).removeClass('show');
        
    }

});