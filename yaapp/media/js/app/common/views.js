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

    events: {
        'click .radio-cell': 'onRadio',
        'mouseover .radio-cell': 'onHover',
        'mouseleave .radio-cell': 'onLeave',
        'mouseenter .tip-btn': 'showTip'
    },

    initialize: function () {
        this.model.bind('change', this.render, this);
        this.currentSongModel = new Yasound.Data.Models.CurrentSong();
        this.currentSongModel.bind('change', this.refreshCurrentSong, this);
    },

    onClose: function () {
        this.model.unbind('change', this.render);
        this.currentSongModel.unbind('change', this.refreshCurrentSong);
        this.currentSongModel.onClose();
        delete this.currentSongModel;
    },

    render: function () {
        var data = this.model.toJSON();
        if (data && data.name && data.name.length > 18) {
            data.name = data.name.substring(0,18) + "...";
        }
        if (Yasound.App.enableFX) {
            $(this.el).hide().html(ich.radioCellTemplate(data)).fadeIn(200);
        } else {
            $(this.el).html(ich.radioCellTemplate(data));
        }

        this.currentSongModel.set('radioId', this.model.get('id'));
        return this;
    },

    onHover: function (e) {
        if (Yasound.App.isMobile) {
            return;
        }
        var mask = $('.mask', this.el);
        if (!mask.is(":visible")) {
            if (Yasound.App.enableFX) {
                $("li .mask", $(this.el).parent()).fadeOut(300);
            } else {
                $("li .mask", $(this.el).parent()).hide();
            }

            if (Yasound.App.appName !== 'deezer') {
                // deezer design does not need info to be fetched
                this.currentSongModel.fetch();
            }

            if (Yasound.App.enableFX) {
                mask.removeClass('hidden').fadeIn(300);
                $('.radio-border', this.el).fadeIn(300);
            } else {
                mask.removeClass('hidden').show();
                $('.radio-border', this.el).show();
            }
        }
    },
    onLeave: function (e) {
        var mask = $('.mask', this.el);
        if (Yasound.App.enableFX) {
            mask.fadeOut(300);
            $('.radio-border', this.el).fadeOut(300);
        } else {
            mask.hide();
            $('.radio-border', this.el).hide();
        }

    },
	onRadio: function (e) {
        e.preventDefault();
        var mask = $('.mask', this.el);
        if (Yasound.App.enableFX) {
            mask.fadeOut(300);
            $('.radio-border', this.el).fadeOut(300);
        } else {
            mask.hide();
            $('.radio-border', this.el).hide();
        }
        var uuid = this.model.get('uuid');
        Yasound.App.Router.navigate("radio/" + uuid + '/', {
            trigger: true
        });
    },

    refreshCurrentSong: function(e) {
        var el = $('.current-song', this.el);
		var el2 = $('.current-artist', this.el);
        var name = this.currentSongModel.get('name');
        var artist =  this.currentSongModel.get('artist');
        var cover = this.currentSongModel.get('cover');
        if (!name) {
            name = '';
        }
        if (!artist) {
            artist = '';
        }
        el.html(name);
		el2.html(artist);

        var img = $('.radio-icon img', this.el);
        img.attr('src', cover);

        var genre = this.model.genre();
        $('.tag', this.el).html(genre + '<div class="tag-right-side"></div>');
    },

    showTip: function(e) {
        var $source = $(e.currentTarget),
            $cell = this.$('.radio-cell');

        if($cell.hasClass('open')) return;
        else $cell.addClass('open');

        this.tip = new Yasound.Views.RadioCellTip({ model: this.model, $source: $source }).render();
        var $cellInfo = this.$('.radio-cell-info');
        var offset = $cellInfo.offset();
        offset.width = $cellInfo[0].offsetWidth;
        offset.height = $cellInfo[0].offsetHeight;
        this.tip.show(offset);
    }

});

Yasound.Views.RadioCellTip = Backbone.View.extend({
    tagName: 'div',
    className: 'radio-cell-tip',

    events: {
        'mouseleave': 'hide',
        'click .main-button a' : 'onDisplayRadio'
    },

    initialize: function () {
        _.bindAll(this, 'show', 'hide');
        this.options.$source.on('click mouseleave', this.hide);
        this.currentSongModel = new Yasound.Data.Models.CurrentSong();
        this.currentSongModel.bind('change', this.refreshCurrentSong, this);
    },

    onClose: function () {
        this.currentSongModel.unbind('change', this.refreshCurrentSong);
        this.currentSongModel.onClose();
        delete this.currentSongModel;
    },

    render: function () {
        var data = this.model.toJSON();
        this.$el.html(ich.radioCellTipTemplate(data));

        this.currentSongModel.set('radioId', this.model.get('id'));
        this.currentSongModel.fetch();

        return this;
    },

    show: function(offset) {

        $('body').append(this.$el);

        // Dynamic tip position.
        var actualWidth = this.$el[0].offsetWidth;
        var actualHeight = this.$el[0].offsetHeight;

        var pos = { top: offset.top + offset.height, left: offset.left + offset.width / 2 - actualWidth / 2 };
        // Top: Maybe @todo
        // else pos = { top: pos.top - actualHeight, left: pos.left + pos.width / 2 - actualWidth / 2 };

        this.$el.offset(pos);
    },

    hide: function(e) {
        if($(e.toElement).closest('.radio-cell-tip, .tip-btn').length > 0 && e.originalEvent.type !== 'click') return;
        this.options.$source.off('mouseleave', this.hide);
        this.off('click mouseleave', this.hide);
        this.options.$source.closest('.radio-cell').removeClass('open');
        this.close();
    },

    refreshCurrentSong: function(e) {
        var $name = $('.track-info span', this.el);
        var $artist = $('.track-info strong', this.el);
        var name = this.currentSongModel.get('name');
        var artist =  this.currentSongModel.get('artist');
        var cover = this.currentSongModel.get('cover');
        if (!name) {
            name = '&nbsp;';
        }
        if (!artist) {
            artist = '&nbsp;';
        }
        $name.html(name);
        $artist.html(artist);

        var img = $('.track-info img', this.el);
        img.attr('src', cover);
    },

    onDisplayRadio: function (e) {
        e.preventDefault();

        var uuid = this.model.get('uuid');
        Yasound.App.Router.navigate("radio/" + uuid + '/', {
            trigger: true
        });

        this.hide();
    }
});

/**
 * UserCell - display a user in a list
 */
Yasound.Views.UserCell = Backbone.View.extend({
    tagName: 'li',
    className: 'user-cell',
    events: {
        'click .user-cell-inner': 'onUser',
		'mouseover .user-cell-inner': 'onHover',
		'mouseleave .user-cell-inner': 'onLeave',
		'click .delete-friend': 'unfollow'
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
        if (data.connected) {
            $(this.el).addClass('user-connected');
        }
        return this;
    },

	onHover: function (e) {
        if (Yasound.App.isMobile) {
            return;
        }
        var maskUser = $('.mask-user', this.el);
        if (!maskUser.is(":visible")) {
            $("li .mask-user", $(this.el).parent()).fadeOut(300);

            maskUser.removeClass('hidden').fadeIn(300);
        }
    },

	onLeave: function (e) {
        if (Yasound.App.isMobile) {
            return;
        }
        var mask = $('.mask-user', this.el);
        mask.fadeOut(300);
        $('.radio-border', this.el).fadeOut(300);
    },

    onUser: function (e) {
        e.preventDefault();
        var username = this.model.get('username');
        if (!this.model.get('anonymous')) {
            Yasound.App.Router.navigate("profile/" + username + '/', {
                trigger: true
            });
        }
    },

    unfollow: function (e) {
        e.preventDefault();
        $('#modal-unfollow').modal('show');
        var that = this;
        $('#modal-unfollow .btn-primary').one('click', function () {
            $('#modal-unfollow').modal('hide');
            that.model.unfollow(Yasound.App.username);
            that.close();
        });

    }
});

/**
 * User menu handler
 */
Yasound.Views.UserMenu = Backbone.View.extend({
    el: '#user-menu',
    events: {
        'click #profile-picture a': 'myProfile',
        'hover #profile-picture a': 'displayPopupProfile',
        'mouseleave #profile-picture a': 'hidePopupProfile',
        'click #my-profile-btn': 'myProfile',
        'click #my-settings-btn': 'mySettings',
        'click #logout-btn': 'logout',
        'click #messages-btn': 'notifications',
        'click #gift-btn': 'gifts'
    },

    initialize: function() {
        _.bindAll(this, 'render', 'onNotification', 'onNotificationUnreadCount', 'displayPopupProfile', 'hidePopupProfile');
        if (Yasound.App.Router.pushManager.enablePush) {
            Yasound.App.Router.pushManager.on('notification', this.onNotification);
            Yasound.App.Router.pushManager.on('notification_unread_count', this.onNotificationUnreadCount);
        }
    },
    onClose: function() {
        if (Yasound.App.Router.pushManager.enablePush) {
            Yasound.App.Router.pushManager.off('notification', this.onNotification);
        }
    },
    render: function() {
        return this;
    },

    myRadio: function (e) {
        e.preventDefault();
        this.hidePopupProfile();
        var uuid = $('#btn-my-radio', this.el).attr('yasound:uuid');
        Yasound.App.Router.navigate("radio/" + uuid + '/', {
            trigger: true
        });
    },
    myProfile: function (e) {
        e.preventDefault();
        this.hidePopupProfile();
        Yasound.App.Router.navigate('profile/' + Yasound.App.username + '/', {
            trigger: true
        });
        return false;
    },
    mySettings: function (e) {
        e.preventDefault();
        this.hidePopupProfile();
        Yasound.App.Router.navigate('settings/', {
            trigger: true
        });
        return false;
    },
    notifications: function(e) {
        e.preventDefault();
        this.hidePopupProfile();
        Yasound.App.Router.navigate('notifications/', {
            trigger: true
        });
    },

    gifts: function(e) {
        e.preventDefault();
        this.hidePopupProfile();
        Yasound.App.Router.navigate('gifts/', {
            trigger: true
        });
    },

    logout: function(e) {
        e.preventDefault();
        window.location = Yasound.App.root + 'logout';
        return false;
    },

    onNotification: function(notification) {
        colibri(gettext('New notification received'));
    },

    onNotificationUnreadCount: function(data) {
        var unreadCount = data.count;
        var el = $('#messages-btn span', this.el);
        el.html(unreadCount);
        if (unreadCount > 0) {
            el.removeClass('hidden');
        } else {
            el.addClass('hidden');
        }
    },

    displayPopupProfile: function (e) {
        if (this.closeTimer) {
            this.closeTimer = clearTimeout(this.closeTimer);
        }
        $('#profile-box-container', this.el).removeClass('hidden');
    },

    hidePopupProfile: function() {
        this.closeTimer = setTimeout(function() {
            $('#profile-box-container', this.el).addClass('hidden');
        }, 300);
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
        "click #play-btn": "togglePlay",
        "click #play-btn-large": "togglePlay",
        "click #love-btn": "like",
        "click #shop-btn": "shop",
        "click #radio-picto": "displayRadio",
        "click #favorite-radio": "favorite",
        "hover #hd-button": "displayPopupHD",
        "mouseleave #hd-button": "hidePopupHD",
        "click #player-title span": "displayRadio",
        "click #radio-title span": "displayRadio"
    },

    initialize: function () {
        this.model.bind('change', this.render, this);
        _.bindAll(this, 'render',
            //'onVolumeSlide',
            'togglePlay',
            'favorite',
            'onPlayerPlay',
            'onPlayerStop',
            'hidePopupHD',
            'displayPopupHD',
            'onShare');
    },

    onClose: function () {
        this.model.unbind('change', this.render);
        $('#modal-share').off('show', this.onShare);

        $.unsubscribe('/player/play', this.onPlayerPlay);
        $.unsubscribe('/player/stop', this.onPlayerStop);

        if (this.pingIntervalId) {
            clearInterval(this.pingIntervalId);
        }
    },

    render: function () {
        var data = this.model.toJSON();
        data['hd'] = Yasound.App.player.hd;
        if (this.radio) {
            data['radio_picture'] = this.radio.get('picture');
            data['radio_name'] = this.radio.get('name');
        }
        $(this.el).html(ich.trackTemplate(data));

        if (this.userMenu) {
            this.userMenu.close();
            this.userMenu = undefined;
        }
        this.userMenu = new Yasound.Views.UserMenu({}).render();

        if (this.loginView) {
            this.loginView.close();
            this.loginView = undefined;
        }
        this.loginView = new Yasound.Views.LogIn({}).render();


        /*var volumeSlider = $('#volume-slider');
        volumeSlider.slider({
            range: "min",
            min: 0,
            max: 100
        });
        volumeSlider.bind("slide", this.onVolumeSlide);*/

        if (Yasound.App.player.isPlaying()) {
            $('#play-btn i').removeClass('icon-play').addClass('icon-pause');
        }
        //volumeSlider.slider('value', Yasound.App.player.volume());

        var radio = Yasound.App.Router.currentRadio;
        if (radio && radio.get('favorite')) {
            $('#favorite-radio', this.el).removeClass('is-not-favorite').addClass('is-favorite');
        } else {
            $('#btn-unfavorite', this.el).removeClass('is-favorite').addClass('is-not-favorite');
        }

        this.ping();

        $.subscribe('/player/play', this.onPlayerPlay);
        $.subscribe('/player/stop', this.onPlayerStop);

        if (Yasound.App.player.isPlaying()) {
            this.onPlayerPlay();
        } else {
            this.onPlayerStop();
        }

        this.giftsPopup = new Yasound.Views.GiftsPopup({
            el: '#hd-box-container'
        });

        $('#modal-share').on('show', this.onShare);

        return this;
    },

    onPlayerPlay: function () {
        $('#play-btn-large').removeClass('play').addClass('pause');
        $('#play-btn i').removeClass('icon-play').addClass('icon-pause');
        $('#volume-slider').slider('value', Yasound.App.player.volume());
    },

    onPlayerStop: function () {
        $('#play-btn-large').removeClass('pause').addClass('play');
        $('#play-btn i').removeClass('icon-pause').addClass('icon-play');
    },

    togglePlay: function (e) {
        e.preventDefault();
        if (!Yasound.App.player.isPlaying()) {
            Yasound.App.player.play();
        } else {
            Yasound.App.player.stop();
        }
    },

    /*onVolumeSlide: function(e, ui) {
        Yasound.App.player.setVolume(ui.value);
    },*/

    like: function (e) {
        e.preventDefault();
        var songId = this.model.get('id');
        var url = '/api/v1/song/' + songId + '/liker/';
        $.publish('/song/like', this.model);
        $.post(url);
    },

    shop: function (e) {
        e.preventDefault();
        var link = $(e.target).attr('href');
        window.open(link);
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

    favorite: function(e) {
        e.preventDefault();
        var radio = Yasound.App.Router.currentRadio;
        if (radio && radio.get('favorite')) {
            radio.removeFromFavorite();
            $('#favorite-radio', this.el).removeClass('is-favorite').addClass('is-not-favorite');

        } else {
            radio.addToFavorite();
            $('#favorite-radio', this.el).removeClass('is-not-favorite').addClass('is-favorite');
        }
    },

    displayPopupHD: function (e) {
        if (this.closeTimer) {
            this.closeTimer = clearTimeout(this.closeTimer);
        }
        if ($('#hd-box-container').is(":visible")) {
            return;
        }
        $('#hd-promocode input', this.el).val('');
        $('#hd-box-container', this.el).show();
        $('#hd-box-container', this.el).one('mousenter', this.displayPopupHD);

        this.giftsPopup.render();
    },

    hidePopupHD: function() {
        this.closeTimer = setTimeout(function() {
            $('#hd-box-container', this.el).hide();
        }, 300);
    },

    onShare: function (e) {
        // hide social buttons if current song is empty
        if (this.model.get('id')) {
            var el = $('#modal-share .modal-body');

            if (!this.shareView) {
                this.shareView = new Yasound.Views.Share({
                    el: el,
                    model: this.model
                });
            }
            this.shareView.render(this.radio);
        } else {
            Yasound.Utils.dialog(gettext('Error'), gettext('Nothing to share'));
        }
    },

    ping: function() {
        if (this.pingIntervalId) {
            clearInterval(this.pingIntervalId);
        }
        var that = this;

        sendPing = function () {
            if (!that.radio) {
                return;
            }

            var query = $.ajax({
                type: 'POST',
                url: '/api/v1/ping/',
                data: {
                    radio_uuid: that.radio.get('uuid')
                }
            });
        };
        this.pingIntervalId = setInterval(function () {
            sendPing();
        }, 10*1000);
        sendPing();
    }
});

Yasound.Views.Pagination = Backbone.View.extend({
    title: gettext('Show more'),

    events: {
        'click button.servernext': 'nextResultPage',
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
        _.bindAll(this, 'scroll', 'setTitle');

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

    setTitle: function (title) {
        this.title = title;
        return this;
    },

    render: function () {
        this.locked = false;
        var info = this.collection.info();
        var page = info.page;
        var totalPages = info.totalPages;

        if (info.next) {
            this.$el.html(ich.paginationTemplate({title: this.title}));
        } else if (page+1 < totalPages) {
                this.$el.html(ich.paginationTemplate({title: this.title}));
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
            /*this.collection.requestNextPage();*/
        }
    }
});


/**
 * Connected users
 */
Yasound.Views.ConnectedUsers = Backbone.View.extend({
    el: '#connected-users',
    events: {
        "click #footer-button": "onShowAll"
    },

    collection: new Yasound.Data.Models.ConnectedUsers(),

    initialize: function() {
        _.bindAll(this, 'addOne', 'addAll', 'render', 'updateData');
        setInterval(this.updateData, 10 * 1000 * 60);

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
        $('span.connected-user-cell', this.el).remove();
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
        this.updateData();
    },
    onShowAll: function(e) {
        e.preventDefault();
        Yasound.App.Router.navigate("users/", {
            trigger: true
        });
    },
    updateData: function() {
        this.clear();
        this.collection.fetch();
    }
});

Yasound.Views.ConnectedUserCell = Backbone.View.extend({
    tagName: 'span',
    className: 'connected-user-cell',

    events: {
        "click a": "onUser"
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
        $('a', this.el).tooltip({title: data.name});
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


Yasound.Views.PublicStats = Backbone.View.extend({
    el: '#minutes',
    model: new Yasound.Data.Models.PublicStats(),
    events: {
    },

    initialize: function () {
        _.bindAll(this, 'updateData');
        this.model.bind('change', this.render, this);
        setInterval(this.updateData, 10 * 1000 * 60);
    },
    onClose: function() {
    },
    render: function() {
        var data = this.model.toJSON();
        $('#minutes-listened', this.el).html(data.minutes);
    },
    updateData: function() {
        this.model.fetch();
    }
});

/**
 * LogIn PopUp
 */

Yasound.Views.LogIn = Backbone.View.extend({
    el: '#login',

    events: {
        "mouseenter .login-btn"  :"displayPopupLogin",
        "click #login-btn": "displayRegularLogin",
        "click #signup-btn": "displayRegularSignup",
        "submit #popup-login-form": "submit"
    },

    initialize: function() {
        _.bindAll(this, 'render', 'displayPopupLogin', 'hidePopupLogin', 'displayRegularLogin', 'displayRegularSignup');
    },

    render: function() {
        var that = this;
        $(this.el).on('mouseleave', function() {
            that.hidePopupLogin();
        });

        return this;
    },

    displayPopupLogin: function (e) {
        e.preventDefault();
        $('#login-box-container', this.el).removeClass('hidden');
    },

    hidePopupLogin: function() {
        $('#login-box-container', this.el).addClass('hidden');
    },

    displayRegularLogin: function (e) {
        e.preventDefault();
        this.hidePopupLogin();
        Yasound.App.Router.navigate('/login/', {
            trigger: true
        });
    },

    displayRegularSignup: function (e) {
        e.preventDefault();
        this.hidePopupLogin();
        Yasound.App.Router.navigate('/signup/', {
            trigger: true
        });
    },

    submit: function(e) {
        e.preventDefault();
        var form = $('#popup-login-form', this.el);
        $('.error-msg', form).remove();
        $('input').removeClass('error');

        var url = form.attr('action');
        $.post(url, form.serializeArray(), function(data) {
            var success = data.success;
            if (!data.success) {
                colibri(gettext('Login error'));
                var errors = data.errors;
                if (errors) {
                    _.each(errors, function(value, key) {
                        var $input = $('input[name=' + key + ']', form);
                        $input.addClass('error');
                        $input.after('<div class="error-msg">' + value + '</div>');
                    });
                }
            } else {
                window.location = Yasound.App.root;
            }
        }).error(function() {
            colibri(gettext('Error while login in', 'colibri-error'));
        });
    }

});

/**
 * Sub menu handler
 */
Yasound.Views.SubMenu = Backbone.View.extend({
    events: {
        "click #selection"          : "selection",
        "click #top"                : "top",
        "click #friends"            : "friends",
        "click #favorites"          : "favorites",
        "keypress #search-input"    : 'search',
        "change #id_genre"          : 'genreChanged',
        "click #create-radio"       : 'myRadios',
        "click #play-btn"           : "togglePlay",
        "click #responsive-love-btn": "like",
        "click #responsive-song"    : "displayRadio",
        "click .responsive-infos"   : "displayRadio",
        'click .dropdown-genre ul li a': 'onGenre'
    },

    initialize: function() {
        _.bindAll(this, 'render', 'selectMenu', 'onPlayerPlay', 'onPlayerStop');
        this.model.bind('change', this.render, this);
    },
    reset: function() {
    },
    onClose: function() {
        $.unsubscribe('/player/play', this.onPlayerPlay);
        $.unsubscribe('/player/stop', this.onPlayerStop);
    },
    render: function() {
        this.reset();
        var jsonModel = this.model.toJSON();
        // $(this.el).html('');
        // $(this.el).html(ich.subMenuTemplate(jsonModel));
        this.mobileMenuShareView = new Yasound.Views.MobileMenuShare({}).render(jsonModel);

        $('#profile-picture img', this.el).imgr({size:"2px",color:"white",radius:"50%"});

        if (this.genre) {
            $('#id_genre').val(this.genre);
        }
        $("select", this.el).uniform();

        if (Yasound.App.hasRadios) {
            $('#create-radio span').html(gettext('My radios'));
        } else {
            $('#create-radio span').html(gettext('Create radio'));
        }

        if (Yasound.App.player.isPlaying()) {
            $('#play-btn i').removeClass('icon-play').addClass('icon-pause');
        }

        $.subscribe('/player/play', this.onPlayerPlay);
        $.subscribe('/player/stop', this.onPlayerStop);

        $('.dropdown-genre ul li', this.el).first().hide();
        return this;
    },
    selectMenu: function(menu) {
        $(".btn-group a", this.el).removeClass('active');
        $("#" + menu, this.el).addClass('active');
    },

    selection: function(e) {
        e.preventDefault();

        Yasound.App.Router.navigate('/', {
            trigger: true
        });
    },
    top: function(e) {
        e.preventDefault();
        Yasound.App.Router.navigate('/top/', {
            trigger: true
        });
    },
    friends: function(e) {
        e.preventDefault();
        Yasound.App.Router.navigate('/friends/', {
            trigger: true
        });
    },
    favorites: function(e) {
        e.preventDefault();
        Yasound.App.Router.navigate('/favorites/', {
            trigger: true
        });
    },
    search: function(e) {
        if (e.keyCode != 13) {
            return;
        }

        var value = $('#search-input', this.el).val();
        if (!value) {
            return;
        }

        $('#search-input', this.el).val('');
        e.preventDefault();

        Yasound.App.Router.navigate("search/" + value + '/', {
            trigger: true
        });
    },

    genreChanged: function(e) {
        var genre = $(e.target).val();
        $.publish('/submenu/genre', genre);
    },

    currentGenre: function() {
        return $('#id_genre').val();
    },

    setCurrentGenre: function (genre) {
        $('#id_genre').val(genre);
        this.genre = genre;
        $.publish('/submenu/genre', genre);
    },

    myRadios: function(e) {
        e.preventDefault();
        Yasound.App.Router.navigate('/radios/', {
            trigger: true
        });
    },

    onPlayerPlay: function () {
        $('#play-btn i').removeClass('icon-play').addClass('icon-pause');
    },

    onPlayerStop: function () {
        $('#play-btn i').removeClass('icon-pause').addClass('icon-play');
    },

    togglePlay: function (e) {
        e.preventDefault();
        if (!Yasound.App.player.isPlaying()) {
            Yasound.App.player.play();
        } else {
            Yasound.App.player.stop();
        }
    },

    like: function (e) {
        e.preventDefault();
        var songId = this.model.get('id');
        var url = '/api/v1/song/' + songId + '/liker/';
        $.post(url);
    },

    displayRadio: function (event) {
        event.preventDefault();
        var radio = Yasound.App.Router.currentRadio;
        if (radio) {
            var uuid = radio.get('uuid');
            if (uuid) {
                Yasound.App.Router.navigate("radio/" + uuid + '/', {
                    trigger: true
                });
            }
        }
    },

    onGenre: function (e) {
        e.preventDefault();
        var value = $(e.target).data('genre');
        $('.btn-select', this.el).text(text);
        var first = $('.dropdown-genre ul li', this.el).first();
        if (value !== '') {
            first.show();
            var text = $(e.target).text();
            $('.btn-select', this.el).html(text + ' <i class="asset-select">');
        } else {
            first.hide();
            $('.btn-select', this.el).html(gettext('Sort by genre') + ' <i class="asset-select">');
        }
        $.publish('/submenu/genre', value);
    }
});

Yasound.Views.SelectedGenre = Backbone.View.extend({
    el: '#selected-genre',
    events: {},
    initialize: function() {
        _.bindAll(this, 'render', 'onGenreChanged');
        $.subscribe('/submenu/genre', this.onGenreChanged);
        this.visible = false;
    },

    onClose: function() {
        $.unsubscribe('/submenu/genre', this.onGenreChanged);
    },

    render: function () {
        return this;
        var genre = $('#id_genre option:selected').val();
        if (genre === '' || !this.visible) {
            this.$el.fadeOut(200);
        } else {
            var genreDisplay = $('#id_genre option:selected').text();
            $('span', this.el).html(genreDisplay);
            this.$el.fadeIn(200);
        }
        return this;

    },

    setVisible: function (visible, menu) {
        this.menu = menu;
        this.visible = visible;
        this.render();
    },

    onGenreChanged: function (e, genre) {
        if (!this.visible) {
            this.$el.hide();
            return;
        }
        this.render();
    }

});
