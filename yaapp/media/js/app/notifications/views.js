"use strict";
/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Views');

Yasound.Views.Notification = Backbone.View.extend({
    tagName: 'li',
    className: 'notification',
    events: {
    },

    initialize: function () {
        this.model.bind('change', this.render, this);
    },

    onClose: function () {
        this.model.unbind('change', this.render);
    },

    render: function () {
        var data = this.model.toJSON();
        var timeZone = '+01:00';
        if (moment().isDST()) {
            timeZone = '+02:00';
        }
        // if start_date contains microsecond precision, we remove it
        var start_date = this.model.get('date').substr(0, 19);
        var date = moment(start_date + timeZone);
        data.formatted_start_date = date.format('LLLL');

        $(this.el).hide().html(ich.notificationTemplate(data)).fadeIn(200);
        return this;
    }
});

Yasound.Views.Notifications = Backbone.View.extend({
    initialize: function () {
        _.bindAll(this, 'addOne', 'addAll');

        this.collection.bind('add', this.addOne, this);
        this.collection.bind('reset', this.addAll, this);
        this.views = [];
    },

    onClose: function () {
        this.collection.unbind('add', this.addOne);
        this.collection.unbind('reset', this.addAll);
    },

    addAll: function () {
        $('.loading-mask', this.el).remove();
        this.collection.each(this.addOne);
    },

    clear: function () {
        _.map(this.views, function (view) {
            view.close();
        });
        this.views = [];
    },

    addOne: function (notification) {
        var currentId = notification.id;

        var found = _.find(this.views, function (view) {
            if (view.model.id == notification.id) {
                return true;
            }
        });
        if (found) {
            // do not insert duplicated content
            return;
        }

        var view = new Yasound.Views.Notification({
            model: notification
        });
        
        var insertOnTop = false;
        if (this.views.length > 0) {
            var lastId = parseInt(this.views[0].model.get('id'));
            var currentId = parseInt(notification.id);
            if (currentId > lastId) {
                insertOnTop = true;
            }
        }
        
        if (insertOnTop) {
            $(this.el).prepend(view.render().el);
            // in case of prepend, it means that the wall has been refreshed
            // with new item
            // so we remove the last one in order to avoid infinite addition to
            // the wall
            if (this.views.length >= this.collection.perPage) {
                var lastView = this.views.pop();
                lastView.close();
            }
            this.views.splice(0,0, view);
        } else {
            $(this.el).append(view.render().el);
            this.views.push(view);
        }
    }
});

/**
 * Profile page
 */
Yasound.Views.NotificationsPage = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this, 'render');
    },

    onClose: function() {
    },

    reset: function() {
    },

    render: function() {
        this.reset();
        $(this.el).html(ich.notificationsPageTemplate());

        this.notifications = new Yasound.Data.Models.Notifications({});
        this.notificationsView = new Yasound.Views.Notifications({
            collection: this.notifications,
            el: $('#notifications', this.el)
        });
        this.paginationView = new Yasound.Views.Pagination({
            collection: this.notifications,
            el: $('#pagination', this.el)
        });

        this.notifications.fetch();
        return this;
    }
});