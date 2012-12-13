/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Views');

Yasound.Views.Notification = Backbone.View.extend({
    tagName: 'li',
    className: 'notification',
    events: {
        "click .close-icon": "onRemove",
        "click .profile": "onProfile",
        "click a.radio-link": "onRadio",
        "click .radio": "onRadio"
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

        if (Yasound.App.enableFX) {
            $(this.el).hide().html(ich.notificationTemplate(data)).fadeIn(200);
        } else {
            $(this.el).html(ich.notificationTemplate(data));
        }

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
    },

    onProfile: function (e) {
        e.preventDefault();
        var username = $(e.target).attr('data-username');
        Yasound.App.Router.navigate("profile/" + username + '/', {
            trigger: true
        });
    },

    onRadio: function (e) {
        e.preventDefault();
        var uuid = $(e.target).attr('data-uuid');
        Yasound.App.Router.navigate("radio/" + uuid + '/', {
            trigger: true
        });
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

        if (this.collection.length === 0) {
            $('.empty', this.el).show();
        } else {
            $('.empty', this.el).hide();
        }

        $('li', this.el).filter(':odd').removeClass('notification-even').addClass('notification-odd');
        $('li', this.el).filter(':even').removeClass('notification-even').addClass('notification-even');

        var f = jQuery("a.popup").fancybox({
            'speedIn' : 200,
            'speedOut' : 200,
            'padding': 0,
            'margin': 0,
            'scrolling': 'yes',
            'overlayShow' : true,
            'type': 'iframe'
        });

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

Yasound.Views.NotificationDigest = Backbone.View.extend({
    tagName: 'li',
    className: 'list-block',
    events: {
        "click .close-icon": "onRemove",
        "click .profile": "onProfile",
        "click a.radio-link": "onRadio",
        "click .radio": "onRadio"
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
        console.log(data);
        if (data.type === 'type_notif_friend_online') {
            $(this.el).html(ich.notificationFriendOnlineDigestTemplate(data));
        } else if (data.type == 'type_notif_message_in_wall') {
            $(this.el).html(ich.notificationMessageInWallDigestTemplate(data));
        } else if (data.type == 'type_notif_radio_in_favorites') {
            $(this.el).html(ich.notificationAddedFavoriteDigestTemplate(data));
        } else if (data.type == 'type_notif_song_liked') {
            $(this.el).html(ich.notificationSongLikedDigestTemplate(data));
        } else {
            $(this.el).html(ich.notificationDigestTemplate(data));
        }

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
    },

    onProfile: function (e) {
        e.preventDefault();
        var username = $(e.target).attr('data-username');
        Yasound.App.Router.navigate("profile/" + username + '/', {
            trigger: true
        });
    },

    onRadio: function (e) {
        e.preventDefault();
        var uuid = $(e.target).attr('data-uuid');
        Yasound.App.Router.navigate("radio/" + uuid + '/', {
            trigger: true
        });
    }
});

Yasound.Views.NotificationsDigest = Backbone.View.extend({
    collection: new Yasound.Data.Models.NotificationsDigest({}),

    initialize: function () {
        _.bindAll(this, 'addOne', 'addAll', 'render');

        this.collection.bind('add', this.addOne, this);
        this.collection.bind('reset', this.addAll, this);
        this.mode = 'unread';
        this.views = [];
    },

    onClose: function () {
        this.collection.unbind('add', this.addOne);
        this.collection.unbind('reset', this.addAll);
    },

    render: function () {
        this.collection.fetch();
        return this;
    },

    addAll: function () {
        $('.loading-mask', this.el).remove();
        this.clear();
        this.collection.each(this.addOne);

        if (this.collection.length === 0) {
            $('.empty', this.el).show();
        } else {
            $('.empty', this.el).hide();
        }

        var totalCount = this.collection.totalCount;
        var remaining = totalCount - this.collection.length;
        if (remaining < 0) {
            remaining = 0;
        }

        $(this.el).append(ich.notificationDigestLastTemplate({'remaining': remaining}));
    },

    clear: function () {
        _.map(this.views, function (view) {
            view.close();
        });
        this.views = [];
        $('li', this.el).remove();
    },

    addOne: function (notification) {
        var view = new Yasound.Views.NotificationDigest({
            model: notification
        });
        view.mode = this.mode;
        $(this.el).append(view.render().el);
        this.views.push(view);
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
        }).setTitle(gettext('Next notifications'));

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
