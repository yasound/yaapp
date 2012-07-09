"use strict";
/*
 * jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true,
 * evil: true, undef: true, white: true, newcap: true
 */
/* extern Ext, $ */

Namespace('Yasound.Views');

/**
 * RadioCell - display a radio in a list
 */
Yasound.Views.RadioCell = Backbone.View.extend({
    tagName: 'li',
    className: 'radio-cell',

    events: {
        'click .thumbnail': 'onRadio'
    },

    initialize: function () {
        this.model.bind('change', this.render, this);
    },
    onClose: function () {
        this.model.unbind('change', this.render);
    },
    render: function () {
        var data = this.model.toJSON();
        if (data.name.length > 18) {
            data.name = _.str.prune(data.name, 18);
        }
        $(this.el).hide().html(ich.radioCellTemplate(data)).fadeIn(200);
        return this;
    },
    onRadio: function (e) {
        e.preventDefault();
        var uuid = this.model.get('uuid');
        Yasound.App.Router.navigate("radio/" + uuid + '/', {
            trigger: true
        });
    }
});

/**
 * UserCell - display a user in a list
 */
Yasound.Views.UserCell = Backbone.View.extend({
    tagName: 'li',
    className: 'user-cell',
    events: {
        'click .user-cell-inner': 'onUser'
    },

    initialize: function () {
        this.model.bind('change', this.render, this);
    },

    onClose: function () {
        this.model.unbind('change', this.render);
    },

    render: function () {
        var data = this.model.toJSON();
        $(this.el).html(ich.userCellTemplate(data));
        return this;
    },

    onUser: function (e) {
        e.preventDefault();
        var username = this.model.get('username');
        Yasound.App.Router.navigate("profile/" + username + '/', {
            trigger: true
        });
    }
});

/**
 * User menu handler
 */
Yasound.Views.UserMenu = Backbone.View.extend({
    el: '#user-menu',
    events: {
        'click #btn-my-radio': 'myRadio',
        'click #btn-favorites': 'favorites',
        'click #btn-friends': 'friends',
        'click #btn-my-profile': 'myProfile',
        'click #btn-settings': 'settings',
        'click #btn-programming': 'programming',
        'click #btn-notifications': 'notifications'
    },
    initialize: function() {
        _.bindAll(this, 'addNotificationItem');
        
        this.notificationMenuItems = [];
        var that = this;
        if (Yasound.App.Router.pushManager.enablePush) {
            Yasound.App.Router.pushManager.on('notification', function (notification) {
                colibri(gettext('New notification received'));
                that.addNotificationItem(notification)
            });
        }
    },
    myRadio: function (e) {
        e.preventDefault();
        var uuid = $('#btn-my-radio', this.el).attr('yasound:uuid');
        Yasound.App.Router.navigate("radio/" + uuid + '/', {
            trigger: true
        });
    },
    favorites: function (e) {
        e.preventDefault();
        Yasound.App.Router.navigate('favorites/', {
            trigger: true
        });
    },
    friends: function (e) {
        e.preventDefault();
        Yasound.App.Router.navigate('friends/', {
            trigger: true
        });
    },
    myProfile: function (e) {
        e.preventDefault();
        Yasound.App.Router.navigate('profile/' + Yasound.App.username + '/', {
            trigger: true
        });
    },
    settings: function (e) {
        e.preventDefault();
        Yasound.App.Router.navigate('settings/', {
            trigger: true
        });
    },
    programming: function(e) {
        e.preventDefault();
        Yasound.App.Router.navigate('programming/', {
            trigger: true
        });
    },
    notifications: function(e) {
        e.preventDefault();
        Yasound.App.Router.navigate('notifications/', {
            trigger: true
        });
    },
    addNotificationItem: function(notification) {
        var view = new Yasound.Views.NotificationMenuItem({
            model: new Yasound.Data.Models.Notification(notification)
        });
        this.notificationMenuItems.slice(0, 0, view);
        $('#notifications-menu').prepend(view.render().el);
        if (this.notificationMenuItems.length >= 6) {
            var lastView = this.notificationMenuItems.pop();
            lastView.close();
        }
    }
});

Yasound.Views.NotificationMenuItem = Backbone.View.extend({
    tagName: 'li',
    initialize: function () {
        this.model.bind('change', this.render, this);
    },
    render: function() {
        $(this.el).html(ich.notificationMenuItemTemplate(this.model.toJSON()));
        return this;
    }
});

/**
 * Song player
 */
Yasound.Views.CurrentSong = Backbone.View.extend({
    tagName: 'div',
    className: 'track',
    volumeMouseDown: false,

    events: {
        "click #play": "play",
        "click #inc": "inc",
        "click #dec": "dec",
        "click #like": "like",
        "click #track-image-link": "displayRadio",
        "mousedown #volume-control": "volumeControl",
        "mouseup": 'mouseUp',
        "mousemove": "mouseMove",
        "click #fb_share": "facebookShare"
    },

    initialize: function () {
        this.model.bind('change', this.render, this);
    },

    onClose: function () {
        this.model.unbind('change', this.render);
        if (this.pingIntervalId) {
            clearInterval(this.pingIntervalId);
        }
    },

    generateTwitterText: function () {
        if (!this.radio) {
            return '';
        }

        var share = gettext('I am listening to');
        share += ' ' + this.model.get('name') + ', ';
        share += gettext('by') + ' ' + this.model.get('artist') + ' ';
        share += gettext('on') + ' ' + this.radio.get('name');
        return share;
    },

    generateFacebookText: function () {
        return this.generateTwitterText();
    },

    generateSocialShare: function () {
        if (!this.radio) {
            $('#tweet').hide();
        } else {
            var twitterParams = {
                url: '' + window.location,
                text: this.generateTwitterText(),
                hashtags: 'yasound'
            };
            $('#tweet', this.el).show();
            $('#tweet', this.el).attr('href', "http://twitter.com/share?" + $.param(twitterParams));
            $('meta[name=description]').attr('description', this.generateFacebookText());
        }
    },

    render: function () {
        $(this.el).html(ich.trackTemplate(this.model.toJSON()));
        $('title').text(this.model.title());
        this.generateSocialShare();
        if (Yasound.App.MySound) {
            if (Yasound.App.MySound.playState == 1) {
                $('#play i').removeClass('icon-play').addClass('icon-stop');
                
                this.notifyStreamer();
            }
            $('#volume-position').css("width", Yasound.App.MySound.volume + "%");
        }

        // hide social buttons if current song is empty
        if (this.model.get('id')) {
            $('#tweet', this.el).show();
            $('#fb_share', this.el).show();
        } else {
            $('#tweet', this.el).hide();
            $('#fb_share', this.el).hide();
        }
        this.ping();

        return this;
    },

    play: function () {
        if (typeof Yasound.App.MySound === "undefined") {
            Yasound.App.MySound = soundManager.createSound(Yasound.App.SoundConfig);
            Yasound.App.MySound.play();
            $('#play i').removeClass('icon-play').addClass('icon-stop');
            $('#volume-position').css("width", Yasound.App.MySound.volume + "%");

            this.notifyStreamer();
        } else {
            $('#play i').removeClass('icon-stop').addClass('icon-play');
            Yasound.App.MySound.destruct();
            Yasound.App.MySound = undefined;
        }
    },

    inc: function () {
        if (typeof Yasound.App.MySound === "undefined") {
            return;
        }
        if (Yasound.App.MySound.volume <= 90) {
            $('#volume-position').css("width", Yasound.App.MySound.volume + 10 + "%");
            Yasound.App.MySound.setVolume(Yasound.App.MySound.volume + 10);
        } else {
            $('#volume-position').css("width", "100%");
            Yasound.App.MySound.setVolume(100);
        }
        Yasound.App.SoundConfig.volume = Yasound.App.MySound.volume;
    },

    dec: function () {
        if (typeof Yasound.App.MySound === "undefined") {
            return;
        }
        if (Yasound.App.MySound.volume >= 10) {
            $('#volume-position').css("width", Yasound.App.MySound.volume - 10 + "%");
            Yasound.App.MySound.setVolume(Yasound.App.MySound.volume - 10);
        } else {
            $('#volume-position').css("width", "0%");
            Yasound.App.MySound.setVolume(0);
        }
        Yasound.App.SoundConfig.volume = Yasound.App.MySound.volume;
    },

    resizeVolumeBar: function (event) {
        if (typeof Yasound.App.MySound === "undefined") {
            return;
        }
        $('body').css('cursor', 'pointer');
        var $volumeControl = $('#volume-control');
        var position = event.pageX;
        var left = $volumeControl.offset().left;
        var width = $volumeControl.width();

        var relativePosition = position - left;
        
        var soundVolume = Math.floor(relativePosition * 100 / width);
        var percentage = soundVolume + "%";
        $('#volume-position').css("width", percentage);

        Yasound.App.MySound.setVolume(soundVolume);
        Yasound.App.SoundConfig.volume = Yasound.App.MySound.volume;
    },

    mouseUp: function (event) {
        if (this.volumeMouseDown) {
            $('body').css('cursor', 'auto');
            this.volumeMouseDown = false;
        }
    },

    mouseMove: function (event) {
        if (!this.volumeMouseDown) {
            return;
        }
        this.resizeVolumeBar(event);
    },

    volumeControl: function (event) {
        this.volumeMouseDown = true;
        this.resizeVolumeBar(event);
    },

    like: function (event) {
        var songId = this.model.get('id');
        var url = '/api/v1/song/' + songId + '/liker/';
        $.post(url);
    },

    displayRadio: function (event) {
        event.preventDefault();
        var radio = Yasound.App.Router.currentRadio;
        if (radio) {
            var uuid = this.radio.get('uuid');
            if (uuid) {
                Yasound.App.Router.navigate("radio/" + uuid + '/', {
                    trigger: true
                });
            }
        }
    },

    facebookShare: function (event) {
        event.preventDefault();

        var link = Yasound.App.FacebookShare.link + 'radio/' + this.radio.get('uuid') + '/';
        var obj = {
            method: 'feed',
            link: link,
            picture: Yasound.App.FacebookShare.picture,
            name: gettext('Yasound share'),
            caption: this.generateFacebookText(),
            description: ''
        };
        function callback (response) {
        }
        FB.ui(obj, callback);
    },
    
    ping: function() {
        if (this.pingIntervalId) {
            clearInterval(this.pingIntervalId);
        }
        
        var that = this;
        this.pingIntervalId = setInterval(function () {
            var query = $.ajax({
                type: 'POST',
                url: '/api/v1/ping/',
                data: {
                    radio_uuid: that.radio.get('uuid')
                }
            });
        }, 60000);

    },
    
    notifyStreamer: function() {
        var query = $.ajax({
            type: 'POST',
            url: '/api/v1/notify_streamer/',
            data: {
                radio_uuid: this.radio.get('uuid')
            }
        });
    }
});

Yasound.Views.Pagination = Backbone.View.extend({
    events: {
        'click a.servernext': 'nextResultPage',
        'click a.serverprevious': 'previousResultPage',
        'click a.orderUpdate': 'updateSortBy',
        'click a.serverlast': 'gotoLast',
        'click a.page': 'gotoPage',
        'click a.serverfirst': 'gotoFirst',
        'click a.serverpage': 'gotoPage',
        'click .serverhowmany a': 'changeCount'

    },

    tagName: 'aside',

    initialize: function () {
        _.bindAll(this, 'scroll');

        $(window).on('scroll', this.scroll);
        this.locked = true;
        this.collection.on('reset', this.render, this);
        this.collection.on('change', this.render, this);
    },

    onClose: function () {
        $(window).off('scroll', this.scroll);
        this.collection.unbind('change', this.render);
        this.collection.unbind('reset', this.render);
    },

    render: function () {
        this.locked = false;
        var info = this.collection.info();
        var page = info.page;
        var totalPages = info.totalPages;
        if (page < totalPages) {
            this.$el.html(ich.paginationTemplate());
        } else {
            this.$el.html('');
        }
    },

    updateSortBy: function (e) {
        e.preventDefault();
        var currentSort = $('#sortByField').val();
        this.collection.updateOrder(currentSort);
    },

    nextResultPage: function (e) {
        e.preventDefault();
        this.collection.requestNextPage();
    },

    previousResultPage: function (e) {
        e.preventDefault();
        this.collection.requestPreviousPage();
    },

    gotoFirst: function (e) {
        e.preventDefault();
        this.collection.goTo(this.collection.information.firstPage);
    },

    gotoLast: function (e) {
        e.preventDefault();
        this.collection.goTo(this.collection.information.lastPage);
    },

    gotoPage: function (e) {
        e.preventDefault();
        var page = $(e.target).text();
        this.collection.goTo(page);
    },

    changeCount: function (e) {
        e.preventDefault();
        var per = $(e.target).text();
        this.collection.howManyPer(per);
    },
    scroll: function (event) {
        if (this.locked) {
            return;
        }
        var height = $(document).height();
        var scrollHeight = $(window).scrollTop() + $(window).height();

        if (scrollHeight >= height) {
            this.locked = true;
            this.collection.requestNextPage();
        }
    }
});


/**
 * Connected users
 */
Yasound.Views.ConnectedUsers = Backbone.View.extend({
    el: '#connected-users',
    collection: new Yasound.Data.Models.ConnectedUsers(),
    
    initialize: function() {
        _.bindAll(this, 'addOne', 'addAll', 'render');

        this.collection.bind('add', this.addOne, this);
        this.collection.bind('reset', this.addAll, this);
        this.views = [];
    },
    onClose: function() {
        this.collection.unbind('add', this.addOne);
        this.collection.unbind('reset', this.addAll);
    },

    addAll: function() {
        $('.loading-mask', this.el).remove();
        this.collection.each(this.addOne);
    },

    clear: function() {
        _.map(this.views, function(view) {
            view.close();
        });
        this.views = [];
    },

    addOne: function(user) {
        var view = new Yasound.Views.ConnectedUserCell({
            model: user
        });

        $('#img-users', this.el).prepend(view.render().el);
        this.views.push(view);
    },
    render: function() {
        this.collection.fetch();
    }
});

Yasound.Views.ConnectedUserCell = Backbone.View.extend({
    tagName: 'span',

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
        $(this.el).hide().html(ich.connectedUserTemplate(data)).fadeIn(200);
        return this;
    }
});
