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
        'mouseleave .radio-cell': 'onLeave'
    },

    initialize: function () {
        this.model.bind('change', this.render, this);
        this.currentSongModel = new Yasound.Data.Models.CurrentSong();
        this.currentSongModel.bind('change', this.refreshCurrentSong, this);
    },
    onClose: function () {
        this.model.unbind('change', this.render);
    },
    render: function () {
        var data = this.model.toJSON();
        if (data.name.length > 18) {
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
            this.currentSongModel.fetch()
            
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
        if (Yasound.App.isMobile) {
            return;
        } 
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
        if (!mask.is(":visible")) {
            $("li .mask", $(this.el).parent()).fadeOut(300);
            this.currentSongModel.fetch()
            mask.removeClass('hidden').fadeIn(300);
            $('.radio-border', this.el).fadeIn(300);
        } else {
            mask.fadeOut(300);
            $('.radio-border', this.el).fadeOut(300);
            var uuid = this.model.get('uuid');
            Yasound.App.Router.navigate("radio/" + uuid + '/', {
                trigger: true
            });
        }
        
    },
    refreshCurrentSong: function(e) {
        var el = $('.current-song', this.el);
		var el2 = $('.current-artist', this.el2);
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
        var tagNameTarget = $(e.target).prop('tagName');
        if (tagNameTarget == 'IMG') {
            // do nothing if image clicked (because it is the delete image)
            return;
        }
        
        var username = this.model.get('username');
        Yasound.App.Router.navigate("profile/" + username + '/', {
            trigger: true
        });
    },
    
    unfollow: function (e) {
        e.preventDefault();
        $('#modal-unfollow').modal('show');
        var that = this;
        $('#modal-unfollow .btn-primary').on('click', function () {
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
        'click #messages-btn': 'notifications'
    },
    initialize: function() {
        _.bindAll(this, 'render', 'onNotification', 'onNotificationUnreadCount');
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
        var uuid = $('#btn-my-radio', this.el).attr('yasound:uuid');
        Yasound.App.Router.navigate("radio/" + uuid + '/', {
            trigger: true
        });
    },
    myProfile: function (e) {
        e.preventDefault();
        Yasound.App.Router.navigate('profile/' + Yasound.App.username + '/', {
            trigger: true
        });
    },
    notifications: function(e) {
        e.preventDefault();
        Yasound.App.Router.navigate('notifications/', {
            trigger: true
        });
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
        "click #love-btn": "like",
        "click #radio-picto a": "displayRadio",
        "click #favorite-radio": "favorite"
    },

    initialize: function () {
        this.model.bind('change', this.render, this);
        _.bindAll(this, 'render', 'onVolumeSlide', 'togglePlay', 'favorite', 'facebookShare');
        
        $('#fb_share').click(this.facebookShare);
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
            $('#tw_share').hide();
        } else {
            var twitterParams = {
                url: '' + window.location,
                text: this.generateTwitterText(),
                hashtags: 'yasound'
            };
            $('#tw_share').show();
            $('#tw_share').attr('href', "http://twitter.com/share?" + $.param(twitterParams));
            $('meta[name=description]').attr('description', this.generateFacebookText());
        }
    },

    render: function () {
        $(this.el).html(ich.trackTemplate(this.model.toJSON()));
        document.title = this.model.title();
        
        var volumeSlider = $('#volume-slider'); 
        volumeSlider.slider({
            range: "min",  
            min: 0,
            max: 100
        });
        volumeSlider.bind("slide", this.onVolumeSlide);
        
        this.generateSocialShare();
        if (Yasound.App.MySound) {
            if (Yasound.App.MySound.playState == 1) {
                $('#play-btn i').removeClass('icon-play').addClass('icon-pause');
                
                this.notifyStreamer();
            }
            volumeSlider.slider('value', Yasound.App.MySound.volume);
        }
        
        // hide social buttons if current song is empty
        if (this.model.get('id')) {
            $('#share-btn', this.el).show();
            $('#tw_share').show();
            $('#fb_share').show();
        } else {
            $('#share-btn', this.el).hide();
            $('#tw_share').hide();
            $('#fb_share').hide();
        }

        var radio = Yasound.App.Router.currentRadio;
        if (radio && radio.get('favorite')) {
            $('#favorite-radio', this.el).removeClass('is-not-favorite').addClass('is-favorite');
        } else {
            $('#btn-unfavorite', this.el).removeClass('is-favorite').addClass('is-not-favorite');
        }
        
        this.ping();
        return this;
    },

    togglePlay: function (e) {
        e.preventDefault();
        if (typeof Yasound.App.MySound === "undefined") {
            Yasound.App.MySound = soundManager.createSound(Yasound.App.SoundConfig);
            Yasound.App.MySound.play();
            $('#play-btn i').removeClass('icon-play').addClass('icon-pause');
            $('#volume-slider').slider('value', Yasound.App.MySound.volume);

            this.notifyStreamer();
        } else {
            $('#play-btn i').removeClass('icon-pause').addClass('icon-play');
            Yasound.App.MySound.destruct();
            Yasound.App.MySound = undefined;
        }
    },

    onVolumeSlide: function(e, ui) {
        var soundVolume = ui.value;
        if (Yasound.App.MySound) {
            Yasound.App.MySound.setVolume(soundVolume);
            Yasound.App.SoundConfig.volume = Yasound.App.MySound.volume;
        } else {
            Yasound.App.SoundConfig.volume = soundVolume;
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
        if (page+1 < totalPages) {
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
        this.updateData();
        setInterval(this.updateData, 10 * 1000 * 60);
    },
    onClose: function() {
    },
    render: function() {
        var data = this.model.toJSON();
        $('span', this.el).html(data.minutes);
    },
    updateData: function() {
        this.model.fetch();
    }
});

/**
 * LogIn PopUp
 */

Yasound.Views.LogIn = Backbone.View.extend({
    events: {
        "click #": "clickShowPopup",
        "hover #": "hoverShowPopup"
    },

    render: function() {
        
    }
})

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
        "change #id_genre"          : 'genre',
        "click #create-radio"       : 'myRadios'
    },
    initialize: function() {
        _.bindAll(this, 'render', 'selectMenu');
    },
    reset: function() {
    },
    onClose: function() {
    },
    render: function() {
        this.reset();
        $(this.el).html(ich.subMenuTemplate());
        $('#profile-picture img', this.el).imgr({size:"2px",color:"white",radius:"50%"});
        $("select", this.el).uniform();


        if (Yasound.App.hasRadios) {
            $('#create-radio span').html(gettext('My radios'));
        } else {
            $('#create-radio span').html(gettext('Create radio'));
        }
	
        return this;
    },
    selectMenu: function(menu) {
        $("#sub-header-nav li", this.el).removeClass('selected');
        $("#" + menu, this.el).parent().addClass('selected');
        var $pointer = $('#sub-header-pointer', this.el);
        
        var menuNumber = 0;
        if (menu == 'selection') {
            menuNumber = 1;
        } else if (menu == 'top') {
            menuNumber = 2;
        } else if (menu == 'friends') {
            menuNumber = 3;
        } else if (menu == 'favorites') {
            menuNumber = 4;
        } else if (menu == 'my-radios') {
            menuNumber = 5;
        } else if (menu == 'search') {
            menuNumber = 6;
        } else {
            $pointer.fadeOut(200);
        }
        
        if (menuNumber != 0) {
            $pointer.fadeIn(200);
            $pointer.removeClass().addClass('menu' + menuNumber);
        }

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
    genre: function(e) {
        $.publish('/submenu/genre', $(e.target).val());
    },
    currentGenre: function() {
        return $('#id_genre').val();
    },
    myRadios: function(e) {
        e.preventDefault();
        if (Yasound.App.hasRadios) {
            Yasound.App.Router.navigate('/radios/', {
                trigger: true
            });
        }
    }
});

