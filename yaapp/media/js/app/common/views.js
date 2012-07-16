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
        'click #profile-picture a': 'myProfile',
        'click #btn-settings': 'settings',
        'click #btn-programming': 'programming',
        'click #messages-btn': 'notifications'
    },
    initialize: function() {
        _.bindAll(this, 'render', 'onNotification');
        if (Yasound.App.Router.pushManager.enablePush) {
            Yasound.App.Router.pushManager.on('notification', this.onNotification);
        }
    },
    onClose: function() {
        if (Yasound.App.Router.pushManager.enablePush) {
            Yasound.App.Router.pushManager.off('notification', this.onNotification);
        }
    },
    render: function() {
        $('#profile-picture a img', this.el).imgr({size:"2px",color:"white",radius:"50%"});
        return this;
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
    onNotification: function(notification) {
        colibri(gettext('New notification received'));
        var unreadCount = notification.unread_count;
        var el = $('#messages-btn span', this.el); 
        el.html(unreadCount);
        if (unreadCount > 0) {
            el.removeClass('hidden');            
        } else {
            el.addClass('hidden');
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
        "click #play-btn": "togglePlay",
        "click #like": "like",
        "click #radio-picto a": "displayRadio",
        "click #fb_share": "facebookShare",
        "click #favorite-radio": "favorite"
    },

    initialize: function () {
        this.model.bind('change', this.render, this);
        _.bindAll(this, 'render', 'onVolumeSlide', 'togglePlay', 'favorite');
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
            $('#tweet', this.el).show();
            $('#fb_share', this.el).show();
        } else {
            $('#tweet', this.el).hide();
            $('#fb_share', this.el).hide();
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
        Yasound.App.MySound.setVolume(soundVolume);
        Yasound.App.SoundConfig.volume = Yasound.App.MySound.volume;
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
        $('img', this.el).imgr({size:"2px",color:"white",radius:"50%"});
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
 * Sub menu handler
 */
Yasound.Views.SubMenu = Backbone.View.extend({
    events: {
        "click #selection"          : "selection",
        "click #top"                : "top",
        "click #friends"            : "friends",
        "click #favorites"          : "favorites",
        "keypress #search-input"    : 'search'
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
        return this;
    },
    selectMenu: function(e) {
        $("#sub-header-nav li", this.el).removeClass('selected');
        $(e.target, this.el).parent().addClass('selected');
        
    },
    selection: function(e) {
        e.preventDefault();
        this.selectMenu(e);

        $('#sub-header-pointer', this.el).removeClass().addClass('menu1');
        Yasound.App.Router.navigate('/', {
            trigger: true
        });
    },
    top: function(e) {
        e.preventDefault();
        this.selectMenu(e);

        $('#sub-header-pointer', this.el).removeClass().addClass('menu2');
        Yasound.App.Router.navigate('/', {
            trigger: true
        });
    },
    friends: function(e) {
        e.preventDefault();
        this.selectMenu(e);

        $('#sub-header-pointer', this.el).removeClass().addClass('menu3');
        Yasound.App.Router.navigate('/friends/', {
            trigger: true
        });
    },
    favorites: function(e) {
        e.preventDefault();
        this.selectMenu(e);

        $('#sub-header-pointer', this.el).removeClass().addClass('menu4');
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
    }
});

