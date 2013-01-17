/*
 * jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true,
 * evil: true, undef: true, white: true, newcap: true
 */
/* extern Ext, $ */
Namespace('Yasound.Views');

Yasound.Views.Creator = Backbone.View.extend({
    tagName: 'div',
    className: '.wall-owner-container',
    el: '.wall-owner-container',
    events: {
        'click a.pic': 'selectUser',
        'click a.wall-owner-link': 'selectUser',
        'click .wall-owner a.follow': 'follow'
    },

    initialize: function () {
        this.creator = new Yasound.Data.Models.User(this.model.get('creator'));
    },

    close: function () {
        delete this.creator;
    },

    render: function () {
        $(this.el).html(ich.radioCreatorTemplate(this.creator.toJSON()));
        return this;
    },

    follow: function(e) {
        e.preventDefault();
        if (this.creator.get('is_friend')) {
            this.creator.unfollow(Yasound.App.username);
        } else {
            this.creator.follow(Yasound.App.username);
        }
        this.render();
    },

    selectUser: function (event) {
        event.preventDefault();
        Yasound.App.Router.navigate("profile/" + this.creator.get('username') + '/', {
            trigger: true
        });
    }
});

Yasound.Views.WallInput = Backbone.View.extend({
    tagName: 'div',
    events: {
        "click input[type='submit']" : "submit",
        "keypress textarea" : "onWallInputChanged"
    },

    submit: function (e) {
        var $button = $(e.target);
        $button.attr('disabled', 'disable');
        if (this.radioUUID) {
            var $input = $('textarea', this.el);
            var message = $input.val();
            if (message.length > 0) {
                var url = '/api/v1/radio/' + this.radioUUID + '/post_message/';
                $.post(url, {
                    message: message,
                    success: function () {
                        $input.val('');
                        $.publish('/wall/posted');
                    }
                });
            }
        } else {
            alert('no radio!');
        }
        e.preventDefault();
    },

    onWallInputChanged: function (e) {
        var val = $(e.target).val();
        if (val.length > 0) {
            $("input[type='submit']", this.el).removeAttr('disabled');
        }
    },

    refreshWall: function (e) {
        $.publish('/wall/posted');
        e.preventDefault();
    },

    initialize: function () {
    },

    render: function () {
        return this;
    }
});

Yasound.Views.Radio = Backbone.View.extend({
    tagName: 'div',

    events: {
        "click #user": "selectUser",
        "click #radio-actions-container like-btn": "onLike",
        "click .btn-settings": "onSettings",
        "click .btn-programming": "onProgramming",
        "click .btn-broadcast": "onBroadcast",
        "click a.wall-fav": "toggleFavorite",
        "click .wall-digest a": 'onLink'
    },

    initialize: function () {
        _.bindAll(this, 'updateFavorites');
        this.model.bind('change', this.render, this);
        $.subscribe('/radio/favorite', this.updateFavorites);
        $.subscribe('/radio/not_favorite', this.updateFavorites);
    },

    onClose: function () {
        this.model.unbind('change', this.render);
        $.unsubscribe('/radio/favorite', this.updateFavorites);
        $.unsubscribe('/radio/not_favorite', this.updateFavorites);
    },

    selectUser: function (event) {
        event.preventDefault();
        Yasound.App.Router.navigate("profile/" + this.model.get('creator').username + '/', {
            trigger: true
        });
    },

    render: function () {
        $(this.el).html(ich.radioTemplate(this.model.toJSON()));
        if (this.model.get('favorite')) {
            $('#btn-favorite', this.el).hide();
            $('#btn-unfavorite', this.el).show();
        } else {
            $('#btn-unfavorite', this.el).hide();
            $('#btn-favorite', this.el).show();
        }

        if (this.model.get('creator').owner) {
            $('.btn-settings', this.el).show();
            $('.btn-programming', this.el).show();
            $('.btn-broadcast', this.el).show();
        } else {
            $('.btn-settings', this.el).hide();
            $('.btn-programming', this.el).hide();
            $('.btn-broadcast', this.el).hide();
        }
        return this;
    },

    onLike: function (e) {
        e.preventDefault();
        if (this.model.currentSong) {
            this.model.currentSong.like();
        }
    },

    onSettings: function (e) {
        e.preventDefault();
        Yasound.App.Router.navigate("radio/" + this.model.get('uuid') + '/edit/', {
            trigger: true
        });
    },

    onProgramming: function (e) {
        e.preventDefault();
        Yasound.App.Router.navigate("radio/" + this.model.get('uuid') + '/programming/', {
            trigger: true
        });
    },

    onBroadcast: function (e) {
        e.preventDefault();
        var that = this;
        var $textarea = $('#modal-broadcast textarea');

        $('#modal-broadcast').modal('show');
        $('#modal-broadcast').one('shown', function() {
            $textarea.focus();
        });

        $('#modal-broadcast .btn-primary').one('click', function () {
            $('#modal-broadcast').modal('hide');
            that.model.broadcast($textarea.val());
        });
    },

    updateFavorites: function (e, radio) {
        this.model.set('favorites', radio.get('favorites'), {silent: true});
        this.render();
    },

    toggleFavorite: function (e) {
        e.preventDefault();
        var favorite = false;
        if (this.model.get('favorite')) {
            this.model.removeFromFavorite();
        } else {
            this.model.addToFavorite();
            favorite = true;
        }
        $.publish('/current_radio/favorite_change', favorite);
    },

    onLink: function (e) {
        e.preventDefault();
        window.open($(e.target).attr('href'));
    }
});

Yasound.Views.RadioInfos = Backbone.View.extend({
    tagName: 'div',
    events: {
        'click .add-to-favorites': 'onAddToFavorites',
        'click .remove-from-favorites': 'onRemoveFromFavorites',
        'click .like-song': 'onLikeSong'
    },

    initialize: function () {
        _.bindAll(this,  'refreshFavorites');
        this.model.bind('change', this.render, this);
        if (Yasound.App.appName === 'deezer') {
            $.subscribe('/radio/favorite', this.refreshFavorites);
            $.subscribe('/radio/not_favorite', this.refreshFavorites);
        }
    },
    onClose: function () {
        this.model.unbind('change', this.render);
        if (Yasound.App.appName === 'deezer') {
            $.unsubscribe('/radio/favorite', this.refreshFavorites);
            $.unsubscribe('/radio/not_favorite', this.refreshFavorites);
        }
    },

    render: function () {
        $(this.el).html(ich.radioInfosTemplate(this.model.toJSON()));
        if (Yasound.App.appName === 'deezer') {
            this.refreshFavorites();
        }
        return this;
    },

    refreshFavorites: function () {
        if (this.model.get('favorite')) {
            $('.add-to-favorites', this.el).hide();
            $('.remove-from-favorites', this.el).show();
        } else {
            $('.remove-from-favorites', this.el).hide();
            $('.add-to-favorites', this.el).show();
        }
    },

    onAddToFavorites: function (e) {
        e.preventDefault();
        this.model.addToFavorite();
    },

    onRemoveFromFavorites: function (e) {
        e.preventDefault();
        this.model.removeFromFavorite();
    },

    onLikeSong: function (e) {
        e.preventDefault();
        var songId = this.model.currentSong.get('id');
        if (songId) {
            var url = '/api/v1/song/' + songId + '/liker/';
            $.publish('/song/like', this.model.currentSong);
            $.post(url);
        }
    }
});

Yasound.Views.TrackInRadio = Backbone.View.extend({
    tagName: 'div',
    className: 'track',
    events: {
    },

    initialize: function () {
        this.model.bind('change', this.render, this);
    },

    onClose: function () {
        this.model.unbind('change', this.render);
    },

    render: function () {
        $(this.el).html(ich.trackInRadioTemplate(this.model.toJSON()));

        return this;
    }
});

Yasound.Views.WallEvents = Backbone.View.extend({
    initialize: function () {
        _.bindAll(this, 'addOne', 'addAll', 'beforeFetch');

        this.collection.bind('beforeFetch', this.beforeFetch, this);
        this.collection.bind('add', this.addOne, this);
        this.collection.bind('reset', this.addAll, this);
        this.views = [];
    },

    onClose: function () {
        this.collection.unbind('beforeFetch', this.beforeFetch);
        this.collection.unbind('add', this.addOne);
        this.collection.unbind('reset', this.addAll);
    },

    beforeFetch: function() {
        if (this.loadingMask) {
            $(this.el).append(this.loadingMask);
        }
    },

    addAll: function() {
        var mask = $('.loading-mask', this.el);
        if (!this.loadingMask) {
            this.loadingMask = mask;
        }
        mask.remove();
        this.collection.each(this.addOne);
        if (this.collection.length === 0) {
            $('.empty').show();
        } else {
            $('.empty').hide();
        }
    },

    clear: function () {
        _.map(this.views, function (view) {
            view.close();
        });
        // remove all existing items inside the view (bootstraped data for instance)
        $(this.el).html('');
        this.views = [];
    },

    addOne: function (wallEvent) {

        var found = _.find(this.views, function (view) {
            if (view.model.id == wallEvent.id) {
                view.model = wallEvent;
                view.render();
                return true;
            }
        });
        if (found) {
            // do not insert duplicated content
            return;
        }
        wallEvent.set('creator', this.collection.radio.get('creator').owner);
        var view = new Yasound.Views.WallEvent({
            model: wallEvent
        });

        var insertOnTop = false;
        if (this.views.length > 0) {
            var lastDate = this.views[0].model.get('updated');
            var currentDate = wallEvent.get('updated');
            if (currentDate > lastDate) {
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
    },

    removeView: function(view) {
        view.close();
        this.views = _.without(this.views, view);
    }
});


Yasound.Views.WallEvent = Backbone.View.extend({
    tagName: 'div',
    className: 'wall-event-container',
    events: {
        'click .pic': 'selectUser',
        'click .wall-event-title': 'selectUser',
        'click .asset-report': 'reportAbuse',
        'click .asset-bin': 'deleteMessage'
    },

    initialize: function () {
        this.model.bind('change', this.render, this);
    },

    onClose: function () {
        this.model.unbind('change', this.render);
    },

    render: function () {
        var data = this.model.toJSON();

        if (data.event_type === 'like') {
            if (Yasound.App.enableFX) {
                $(this.el).hide().html(ich.wallEventLikeTemplate(data)).fadeIn(200);
            } else {
                $(this.el).html(ich.wallEventLikeTemplate(data));
            }
        } else {
            if (Yasound.App.enableFX) {
                $(this.el).hide().html(ich.wallEventMessageTemplate(data)).fadeIn(200);
            } else {
                $(this.el).html(ich.wallEventMessageTemplate(data));
            }
        }
        return this;
    },

    selectUser: function (event) {
        event.preventDefault();
        var username = this.model.get('message').username;
        if (username) {
            Yasound.App.Router.navigate("profile/" + username + '/', {
                trigger: true
            });
        }
    },

    reportAbuse: function (e) {
        e.preventDefault();
        var that = this;
        $('#modal-report-abuse').modal('show');
        $('#modal-report-abuse .btn-primary').one('click', function (e) {
            e.preventDefault();
            $('#modal-report-abuse').modal('hide');
            that.model.reportAbuse();
        });
    },

    deleteMessage: function (e) {
        e.preventDefault();
        var that = this;
        $('#modal-delete-message').modal('show');
        $('#modal-delete-message .btn-primary').one('click', function (e) {
            e.preventDefault();
            $('#modal-delete-message').modal('hide');
            that.model.deleteMessage();
        });
    }
});

Yasound.Views.RadioUsers = Backbone.View.extend({
    initialize: function () {
        _.bindAll(this, 'addOne', 'addAll', 'clear');

        this.collection.bind('add', this.addOne);
        this.collection.bind('reset', this.addAll);
        this.views = [];
    },

    onClose: function () {
        this.collection.unbind('add', this.addOne);
        this.collection.unbind('reset', this.addAll);
    },

    addAll: function () {
        this.clear();
        this.collection.each(this.addOne);
    },

    clear: function () {
        _.map(this.views, function (view) {
            view.close();
        });
        this.views = [];
    },

    addOne: function (listener) {
        var found = _.find(this.views, function (view) {
            if (view.model.id == listener.id) {
                return true;
            }
        });

        if (found) {
            // do not insert duplicated content
            return;
        }

        var view = new Yasound.Views.RadioUser({
            model: listener
        });

        $(this.el).prepend(view.render().el);
        this.views.push(view);

        if (this.views.length >= this.collection.limit) {
            this.views[0].close();
            this.views.splice(0, 1);
        }
    }
});

/**
 * User on radio
 */
Yasound.Views.RadioUser = Backbone.View.extend({
    tagName: 'li',
    events: {
        'click a': 'selectUser'
    },
    initialize: function () {
        this.model.bind('change', this.render, this);
    },

    beforeRemove: function () {
        $('a', this.el).tooltip('hide');
    },

    onClose: function () {
        this.model.unbind('change', this.render);
    },

    render: function () {
        var data = this.model.toJSON();
        $(this.el).html(ich.radioUserTemplate(data));
        var tooltip = data.name;
        if (data.city) {
            tooltip = tooltip + '<br/>(' + data.city + ')';
        }
        $('a', this.el).tooltip({title: tooltip});

        return this;
    },

    selectUser: function (event) {
        event.preventDefault();
        if (!this.model.get('anonymous')) {
            Yasound.App.Router.navigate("profile/" + this.model.get('username') + '/', {
                trigger: true
            });
        }
    }
});

Yasound.Views.RadioHeader = Backbone.View.extend({
    events: {

    },

    initialize: function () {
        _.bindAll(this, 'render', 'fetchPictures');
    },

    onClose: function () {
    },

    reset: function () {
    },

    render: function () {
        if (this.model.get('uuid') === g_jm_radio) {
            $('.wall-covers-pics', this.el).html(ich.jmHeaderTemplate());
            $('.wall-covers').addClass('jm-header');
            is_jm_radio = true;
            return this;
        } else {
            $('.wall-covers').removeClass('jm-header');
        }

        this.fetchPictures();
        return this;
    },

    fetchPictures: function () {
        var url = '/api/v1/radio/' + this.model.get('uuid') + '/wall_layout/';
        var that = this;
        $.ajax({
            url: url,
            type: 'GET',
            dataType: 'json',
            success: function(data) {
                if (data.length === 1) {
                    if (!that.savedNode)  {
                        that.savedNode = $('.wall-covers-pics').clone();
                    }
                    // only one picture --> lets use all the available space for it
                    if (Yasound.App.enableFX) {
                        $('.wall-covers-pics').hide().html('<img src="' + data[0] + '"/>').fadeIn(500);
                    } else {
                        $('.wall-covers-pics').html('<img src="' + data[0] + '"/>');
                    }
                } else {
                    if (that.savedNode) {
                        $('.wall-covers-pics').html(that.savedNode);
                        that.savedNode = undefined;
                    }
                    $('.wall-covers-pics img').each(function(index) {
                        if (index < data.length) {
                            $(this).attr('src', data[index]);
                        }
                    });
                }
            },
            failure: function() {
            }
        });
    }
});

Yasound.Views.RadioPage = Backbone.View.extend({
    listeners: new Yasound.Data.Models.RadioUsers({}),
    fans: new Yasound.Data.Models.RadioFans({}),
    wallEvents: new Yasound.Data.Models.WallEvents({}),
    intervalId: undefined,
    wallPosted: undefined,

    events: {
        "click #more-listeners": "displayListeners",
        "click #more-fans": "displayFans"
    },

    initialize: function () {
        _.bindAll(this, 'removeWallEvent', 'onDeezerSongFound', 'onDeezerSongNotFound');
        this.model.bind('change', this.render, this);
        this.fans.perPage = 15;

        $.subscribe('/player/deezer/songFound', this.onDeezerSongFound);
        $.subscribe('/player/deezer/songNotFound', this.onDeezerNotSongFound);
    },

    onClose: function () {
        this.model.unbind('change', this.render);
        $.unsubscribe('/player/deezer/songFound', this.onDeezerSongFound);
        $.unsubscribe('/player/deezer/songNotFound', this.onDeezerNotSongFound);
        Yasound.App.Router.pushManager.off('wall_event_v2_updated');
    },

    reset: function () {
        this.listeners.unbind('add', this.onListenersChanged, this);
        this.listeners.unbind('remove', this.onListenersChanged, this);
        this.listeners.unbind('reset', this.onListenersChanged, this);

        this.fans.unbind('add', this.onFansChanged, this);
        this.fans.unbind('remove', this.onFansChanged, this);
        this.fans.unbind('reset', this.onFansChanged, this);

        if (this.wallPosted) {
            $.unsubscribe('/wall/posted', this.wallPosted);
        }
        if (this.intervalId) {
            clearInterval(this.intervalId);
        }
        if (this.wallInputView) {
            this.wallInputView.close();
        }
        if (this.radioView) {
            this.radioView.close();
        }
        if (this.listenersView) {
            this.listenersView.clear();
            this.listenersView.close();
        }
        if (this.fansView) {
            this.fansView.clear();
            this.fansView.close();
        }
        if (this.wallEventsView) {
            this.wallEventsView.clear();
            this.wallEventsView.close();
        }
        if (this.paginationView) {
            this.paginationView.close();
        }
        if (this.creatorView) {
            this.creatorView.close();
        }
        if (this.headerView) {
            this.headerView.close();
        }

        this.wallEvents.reset();
        this.listeners.reset();
    },

    render: function () {
        this.reset();

        $(this.el).html(ich.radioPageTemplate());

        if (Yasound.App.appName === 'deezer') {
            var player = Yasound.App.player;
            if (player.deezerId) {
                this.addDeezerLinks(player);
            }
        }

        $('h1', this.el).html(this.model.get('name'));

        this.listeners.bind('add', this.onListenersChanged, this);
        this.listeners.bind('remove', this.onListenersChanged, this);
        this.listeners.bind('reset', this.onListenersChanged, this);

        this.fans.bind('add', this.onFansChanged, this);
        this.fans.bind('remove', this.onFansChanged, this);
        this.fans.bind('reset', this.onFansChanged, this);

        this.headerView = new Yasound.Views.RadioHeader({
            el: $('.wall-covers'),
            model: this.model
        });

        var that = this;
        var wallPosted = function () {
            that.wallEvents.page = 0;

            if (!Yasound.App.Router.pushManager.enablePush) {
                that.wallEvents.fetch();
            }
        };
        this.wallPosted = wallPosted;
        $.subscribe("/wall/posted", wallPosted);

        this.wallInputView = new Yasound.Views.WallInput({
            model: this.model,
            el: $('.wall-input-container', this.el)
        });

        this.wallInputView.radioUUID = this.model.get('uuid');
        this.wallInputView.render();

        this.radioView = new Yasound.Views.Radio({
            model: this.model,
            el: $('#radio-side', this.el)
        });

        this.trackView = new Yasound.Views.TrackInRadio({
            model: this.model.currentSong,
            el: $('#webapp-track', this.el)
        });


        this.listeners.radio = this.model;
        this.listenersView = new Yasound.Views.RadioUsers({
            collection: this.listeners,
            el: $('#listeners', this.el)
        });

        this.fans.uuid = this.model.get('uuid');
        this.fansView = new Yasound.Views.RadioUsers({
            collection: this.fans,
            el: $('#fans', this.el)
        });

        this.wallEventsView = new Yasound.Views.WallEvents({
            collection: this.wallEvents,
            el: $('#wall', this.el)
        });
        this.wallEvents.setRadio(this.model);


        this.wallEventsView.clear();


        if (Yasound.App.appName == 'deezer') {
            this.wallEvents.perPage = 10;
        }

        if (this.model.get('id')) {
            if (g_bootstrapped_data) {
                this.wallEvents.reset(g_bootstrapped_data.wall_events);
                this.wallEvents.totalPages = 2;
            } else {
                this.wallEvents.goTo(0);
            }
            this.listeners.fetch();
            this.fans.fetch();
        }

        this.paginationView = new Yasound.Views.Pagination({
            collection: this.wallEvents,
            el: $('#pagination-wall', this.el)
        }).setTitle(gettext('Next messages'));

        this.creatorView = new Yasound.Views.Creator({
            model: this.model
        });

        this.headerView.render();
        this.radioView.render();
        this.trackView.render();
        this.wallEventsView.render();
        this.paginationView.render();
        this.creatorView.render();

        if (Yasound.App.Router.pushManager.enablePush) {
            Yasound.App.Router.pushManager.on('wall_event_v2_updated', function (msg) {
                that.wallEvents.reset(msg);
            });
            Yasound.App.Router.pushManager.on('wall_event_v2_deleted', function (msg) {
                that.removeWallEvent(msg);
            });
        }

        this.intervalId = setInterval(function () {
            if (!Yasound.App.Router.pushManager.enablePush) {
                that.wallEvents.fetchFirst();
            }
            that.listeners.fetch();
            that.fans.fetch();
        }, 10000);

        return this;
    },

    removeWallEvent: function(message) {
        var viewToRemove;
        _.each(this.wallEventsView.views, function(view) {
            if (view.model.get('event_id') === message.event_id) {
                viewToRemove = view;
            }
        });

        if (!viewToRemove) {
            return;
        }
        this.wallEventsView.removeView(viewToRemove);
    },

    onListenersChanged: function (collection) {
        $('.listener-count', this.el).html(collection.totalCount);
        if (collection.length === 0) {
            $('#more-listeners', this.el).hide();
        } else {
            $('#more-listeners', this.el).show();
        }
    },

    onFansChanged: function (collection) {
        $('.fan-count', this.el).html(collection.totalCount);
        if (collection.length === 0) {
            $('#more-fans', this.el).hide();
        } else {
            $('#more-fans', this.el).show();
        }
    },

    displayListeners: function (e) {
        e.preventDefault();
        Yasound.App.Router.navigate("radio/" + this.model.get('slug') + '/listeners/', {
            trigger: true
        });
    },

    displayFans: function (e) {
        e.preventDefault();
        Yasound.App.Router.navigate("radio/" + this.model.get('slug') + '/fans/', {
            trigger: true
        });
    },

    addDeezerLinks: function(player) {
        var $addToPlaylist = $('.dz-addtoplaylist', this.el);
        $addToPlaylist.attr('dz-id', player.deezerId);
        $addToPlaylist.show();

        if (player.deezerArtistId) {
            var $share = $('.dz-share', this.el);
            $share.attr('dz-id', player.deezerArtistId);
            $share.show();
        }

        DZ.framework.parse();
    },

    onDeezerSongFound: function(e, player) {
        this.addDeezerLinks(player);
    },

    onDeezerSongNotFound: function(e, player) {
        $('.dz-addtoplaylist', this.el).hide();
        $('.dz-share', this.el).hide();
    }

});

Yasound.Views.UserRadiosPage = Backbone.View.extend({
    collection: new Yasound.Data.Models.UserRadios({}),

    events: {
        'click #back-btn': 'onBack'
    },

    initialize: function() {
        _.bindAll(this, 'render', 'onGenreChanged', 'onBack');
        $.subscribe('/submenu/genre', this.onGenreChanged);
    },

    onClose: function() {
        $.unsubscribe('/submenu/genre', this.onGenreChanged);
    },

    reset: function() {
        if (this.resultsView) {
            this.resultsView.close();
            this.resultsViews = undefined;
        }
    },

    render: function(genre, username) {
        this.reset();
        $(this.el).html(ich.userRadiosPageTemplate());
        this.collection.perPage = Yasound.Utils.cellsPerPage();
        if (username) {
            this.collection.setUsername(username);
            this.username = username;
            this.user = new Yasound.Data.Models.User({username:username}),
            this.userView = new Yasound.Views.User({
                model: this.user,
                el: $('#user-profile', this.el)
            });
            this.user.fetch();
        }

        this.resultsView = new Yasound.Views.SearchResults({
            collection: this.collection,
            el: $('#results', this.el)
        });

        this.paginationView = new Yasound.Views.Pagination({
            collection: this.collection,
            el: $('#pagination', this.el)
        });

        this.onGenreChanged('', genre);
        return this;
    },

    onGenreChanged: function(e, genre) {
        if (genre === '') {
            this.collection.params.genre = undefined;
        } else {
            this.collection.params.genre = genre;
        }
        this.resultsView.clear();
        this.collection.goTo(0);
    },

    onBack: function(e) {
        e.preventDefault();
        Yasound.App.Router.navigate("profile/" + this.username + '/', {
            trigger: true
        });
    }
});

Yasound.Views.ListenersPage = Backbone.View.extend({
    collection: new Yasound.Data.Models.Listeners({}),

    events: {
        'click #back-btn': 'onBack'
    },

    initialize: function() {
        _.bindAll(this, 'render', 'onBack');
    },

    onClose: function() {
    },

    reset: function() {
        if (this.resultsView) {
            this.resultsView.close();
            this.resultsViews = undefined;
        }
    },

    render: function(uuid) {
        this.reset();
        this.uuid = uuid;
        $(this.el).html(ich.listenersPageTemplate());
        this.collection.uuid = uuid;
        this.collection.perPage = Yasound.Utils.cellsPerPage();

        this.resultsView = new Yasound.Views.Friends({
            collection: this.collection,
            el: $('#results', this.el)
        });

        this.collection.fetch();
        return this;
    },

    onBack: function(e) {
        e.preventDefault();
        Yasound.App.Router.navigate("radio/" + this.uuid + '/', {
            trigger: true
        });
    }
});

Yasound.Views.FansPage = Backbone.View.extend({
    collection: new Yasound.Data.Models.RadioFans({}),

    events: {
        'click #back-btn': 'onBack'
    },

    initialize: function() {
        _.bindAll(this, 'render', 'onBack');
    },

    onClose: function() {
    },

    reset: function() {
        if (this.resultsView) {
            this.resultsView.close();
            this.resultsViews = undefined;
        }
    },

    render: function(uuid) {
        this.reset();
        this.uuid = uuid;
        $(this.el).html(ich.fansPageTemplate());
        this.collection.uuid = uuid;
        this.collection.perPage = Yasound.Utils.cellsPerPage();

        this.resultsView = new Yasound.Views.Friends({
            collection: this.collection,
            el: $('#results', this.el)
        });

        this.collection.fetch();
        return this;
    },

    onBack: function(e) {
        e.preventDefault();
        Yasound.App.Router.navigate("radio/" + this.uuid + '/', {
            trigger: true
        });
    }
});

Yasound.Views.EditRadioPage = Backbone.View.extend({
    events: {
        "click #programming-btn": "onProgramming",
        "click #listen-btn": "onListen",
        "click #radio-settings-menu": 'onRadioSettings',
        "click #wall-settings-menu": 'onWallSettings',
        "submit #edit-radio": "onSubmit",
        'keyup #id_slug' : 'onSlug',
        "submit #edit-wall": "onSubmit"
    },

    initialize: function () {
        _.bindAll(this, 'render', 'templateLoaded');
    },

    onClose: function () {
        if (this.headerView) {
            this.headerView.close();
        }
    },

    reset: function () {
    },

    render: function (uuid) {
        this.reset();
        this.uuid = uuid;
        var params = {
            uuid: uuid
        };
        ich.loadRemoteTemplate('radio/editRadioPage.mustache', 'editRadioPageTemplate', this.templateLoaded, params);
        return this;
    },

    templateLoaded: function() {
        $(this.el).html(ich.editRadioPageTemplate());

        var model = new Yasound.Data.Models.Radio({});
        model.set('uuid', this.uuid);
        this.headerView = new Yasound.Views.RadioHeader({
            el: $('.wall-covers'),
            model: model
        }).render();


        var that = this;
        var $progress = $('#progress .bar', this.el);
        $progress.parent().hide();
        $('#file-upload').fileupload({
            dataType: 'json',
            add: function (e, data) {
                $progress.parent().show();
                data.submit();
            },
            progressall: function (e, data) {
                var progress = parseInt( (data.loaded*100) / data.total, 10);
                $progress.css('width', progress + '%');
            },

            done: function (e, data) {
                var result = data.result[0];
                if (result.error) {
                    var error = result.error;
                    $('#modal-upload-error .modal-body p', that.el).html(error);
                    $('#modal-upload-error', that.el).modal('show');
                } else {
                    var url = result.url;
                    var now = moment();
                    url = url + '?' + now.unix();
                    $('#radio-picture-image', that.el).attr('src', url);
                }
                $progress.css('width', '0%');
                $progress.parent().hide();
                that.headerView.render();
            },
            fail: function (e, data) {
            }
        });

        var parent = $('#id_slug').closest('.controls');
        $('span.help-block', parent).html('https://yasound.com/radio/' + $('#id_slug').val());
    },

    onSubmit: function (e) {
        e.preventDefault();
        var form = $(e.target).closest('form');
        var successMessage = gettext('Radio settings updated');
        var errorMessage = gettext('Error while saving settings');
        var that = this;
        Yasound.Utils.submitForm({
            form: form,
            successMessage: successMessage,
            errorMessage: errorMessage,
            success: function () {
                that.headerView.render();
            }
        });
    },

    onProgramming: function (e) {
        e.preventDefault();
        Yasound.App.Router.navigate("radio/" + this.uuid + '/programming/', {
            trigger: true
        });
    },

    onListen: function (e) {
        e.preventDefault();
        Yasound.App.Router.navigate("radio/" + this.uuid, {
            trigger: true
        });
    },

    onRadioSettings: function (e) {
        e.preventDefault();
        $('#settings-nav li', this.el).removeClass('checked');
        $('#settings-nav #radio-settings-menu', this.el).addClass('checked');


        if (Yasound.App.enableFX) {
            $('#radio-settings', this.el).fadeIn(200);
        } else {
            $('#radio-settings', this.el).show();
        }
        $('#wall-settings', this.el).hide();
    },

    onWallSettings: function (e) {
        e.preventDefault();
        $('#settings-nav li', this.el).removeClass('checked');
        $('#settings-nav #wall-settings-menu', this.el).addClass('checked');


        if (Yasound.App.enableFX) {
            $('#wall-settings', this.el).fadeIn(200);
        } else {
            $('#wall-settings', this.el).show();
        }
        $('#radio-settings', this.el).hide();
    },

    onSlug: function (e) {
        var value = $('#id_slug', this.el).val();
        console.log(value)
        if (!value) {
            return;
        }
        var parent = $('#id_slug').closest('.controls');
        $('span.help-block', parent).html('https://yasound.com/radio/' + value);
    }

});
