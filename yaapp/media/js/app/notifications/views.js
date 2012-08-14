/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Views');

Yasound.Views.Notification = Backbone.View.extend({
    tagName: 'li',
    className: 'notification',
    events: {
        "click .close": "onRemove"
    },

    initialize: function () {
        this.model.bind('change', this.render, this);
    },

    onClose: function () {
        this.model.unbind('change', this.render);
    },

    render: function () {
        var data = this.model.toJSON();
        data.formatted_date = this.model.getFormattedDate();

        $(this.el).hide().html(ich.notificationTemplate(data)).fadeIn(200);
        return this;
    },

    onRemove: function() {
        if (this.model.get('read') === false ) {
            this.model.markAsRead();
            colibri(gettext('Notification marked as read'));
        } else {
            colibri(gettext('Notification deleted'));
            this.model.remove();
        }
    }
});

Yasound.Views.Notifications = Backbone.View.extend({
    initialize: function () {
        _.bindAll(this, 'addOne', 'addAll');

        this.collection.bind('add', this.addOne, this);
        this.collection.bind('reset', this.addAll, this);
        this.mode = 'unread';
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
        view.mode = this.mode;

        var insertOnTop = false;
        if (this.views.length > 0) {
            var lastDate = this.views[0].model.getDate();
            var currentDate = moment(notification.getDate());
            var diff = lastDate.diff(currentDate, 'seconds');
            if (diff < 0) {
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
 * Notifications page
 */
Yasound.Views.NotificationsPage = Backbone.View.extend({
    events: {
        "click #mark-all-read-btn": "markAllAsRead"
    },

    initialize: function() {
        _.bindAll(this, 'render');
    },

    onClose: function() {
        Yasound.App.Router.pushManager.off('notification', this.onNotification, this);
        this.notificationsView.close();
        this.paginationView.close();
    },

    reset: function() {
    },

    onNotification: function(notification) {
        console.log(this.notificationsView.mode);
        if (this.notificationsView.mode == 'unread' && !notification.read) {
            this.notifications.reset(notification);
        }
        else if (this.notificationsView.mode != 'unread' && notification.read) {
            this.notifications.reset(notification);
        }
        else if (this.notificationsView.mode == 'all') {
            this.notifications.reset(notification);
        }
    },

    render: function() {
        this.reset();
        $(this.el).html(ich.notificationsPageTemplate());

        this.notifications = new Yasound.Data.Models.Notifications({
            type: 'unread'
        });
        this.notificationsView = new Yasound.Views.Notifications({
            collection: this.notifications,
            el: $('#notifications', this.el)
        });
        this.paginationView = new Yasound.Views.Pagination({
            collection: this.notifications,
            el: $('#pagination', this.el)
        });

        this.notifications.fetch();

        if (Yasound.App.Router.pushManager.enablePush) {
            Yasound.App.Router.pushManager.on('notification', this.onNotification, this);
        }
        return this;
    },

    markAllAsRead: function (e) {
        e.preventDefault();
        var that = this;
        var url = '/api/v1/notifications/mark_all_as_read/';
        $.ajax({
           url: url,
           type: 'POST',
           dataType: 'json',
           success: function() {
               that.notificationsView.clear();
               that.notifications.goTo(0);
           }
        });
    }
});
