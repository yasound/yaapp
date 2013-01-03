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
        _.bindAll(this, 'render', 'cycle', 'stopCycle', 'startCycle');
    },

    onClose: function () {
        this.stopCycle();
    },

    render: function() {
        if (Yasound.App.isMobile) {
            return;
        }
        this.$el.show();

        this.cycleIntervalId = setInterval(this.cycle, 5*1000);

        return this;
    },

    slideUp: function (e) {
        if (e) {
            e.preventDefault();
            cookies.set('hideteaser', true);
        }
        this.$el.slideUp();

        this.close();
    },

    onArgumentChanged: function(e) {
        e.preventDefault();

        this.stopCycle();

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

        setTimeout(this.startCycle, 10*1000);
    },

    cycle: function () {
        var paginateLinks = this.$('.paginate a');
        var args = this.$('.argument');

        var newIndex = paginateLinks.filter('.active').parent().next();

        if (newIndex.length === 0) {
            newIndex = this.$('.paginate a').first();
        }

        newIndex = newIndex.text();
        var oldIndex = paginateLinks.filter('.active').text();

        if(newIndex === oldIndex) {
            return;
        }

        $(paginateLinks[oldIndex-1]).removeClass('active');
        $(paginateLinks[newIndex-1]).addClass('active');
        $(args[newIndex-1]).addClass('show');
        $(args[oldIndex-1]).removeClass('show');

    },

    startCycle: function () {
        this.stopCycle();
        this.cycleIntervalId = setInterval(this.cycle, 5*1000);
    },

    stopCycle: function () {
        if (this.cycleIntervalId) {
            clearInterval(this.cycleIntervalId);
            this.cycleIntervalId = undefined;
        }
    }
});