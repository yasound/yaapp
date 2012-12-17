/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Views');

/**
 * User zone
 */
Yasound.Views.User = Backbone.View.extend({
    tagName: 'div',
    className: 'radio',
    events: {
        'click #radio-history': 'radioHistory',
        'click #radio-activity': 'currentRadio',
        'click #follow': 'follow',
        'click #settings-btn': 'settings'
    },

    initialize: function () {
        this.model.bind('change', this.render, this);
    },
    onClose: function () {
        this.model.unbind('change', this.render);
    },

    render: function () {
        var data = this.model.toJSON();
        if (data.current_radio && data.current_radio.name.length > 18) {
            data.current_radio.name = data.current_radio.name.substring(0,18) + "...";
        }

        $(this.el).html(ich.userTemplate(data));

        var color = 'white';
        if (data.connected && !data.owner) {
            color = '#5aabda';
        }
        $('#picture img', this.el).imgr({size:"6px",color:color,radius:"100%"});
        return this;
    },

    radioHistory: function (e) {
        e.preventDefault();
        var uuid = this.model.get('history')['radio_uuid'];
        Yasound.App.Router.navigate("radio/" + uuid + '/', {
            trigger: true
        });
    },

    currentRadio: function (e) {
        e.preventDefault();
        var uuid = this.model.get('current_radio')['uuid'];
        Yasound.App.Router.navigate("radio/" + uuid + '/', {
            trigger: true
        });
    },

    settings: function (e) {
        e.preventDefault();
        Yasound.App.Router.navigate("settings/", {
            trigger: true
        });
    },

    follow: function(e) {
        e.preventDefault();
        if (this.model.get('is_friend')) {
            $(e.target, this.el).html(gettext('Follow'));
            this.model.unfollow(Yasound.App.username);
        } else {
            $(e.target, this.el).html(gettext('Unfollow'));
            this.model.follow(Yasound.App.username);
        }
    }
});

Yasound.Views.Like = Backbone.View.extend({
    tagName: 'li',
    events: {
        "click .track-container": "onRadio"
    },

    initialize: function () {
        this.model.bind('change', this.render, this);
    },

    onClose: function () {
        this.model.unbind('change', this.render);
    },

    render: function () {
        var data = this.model.toJSON();
        $(this.el).html(ich.likeCellTemplate(data));
        return this;
    },

    onRadio: function (e) {
        e.preventDefault();
        var uuid = this.model.get('radio_uuid');
        Yasound.App.Router.navigate("radio/" + uuid + '/', {
            trigger: true
        });
    }
});

Yasound.Views.Likes = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this, 'addOne', 'addAll');

        this.collection.bind('add', this.addOne, this);
        this.collection.bind('reset', this.addAll, this);
        this.collection.bind('beforeFetch', this.beforeFetch, this);
        this.views = [];
    },
    onClose: function() {
        this.collection.unbind('add', this.addOne);
        this.collection.unbind('reset', this.addAll);
        this.collection.unbind('beforeFetch', this.beforeFetch, this);
    },

    beforeFetch: function() {
        if (this.loadingMask) {
            this.loadingMask.show();
        }
    },

    addAll: function() {
        if (!this.loadingMask) {
            var mask = this.$el.siblings('.loading-mask');
            this.loadingMask = mask;
        }

        this.loadingMask.hide();
        this.collection.each(this.addOne);
    },

    clear: function() {
        _.map(this.views, function(view) {
            view.close();
        });
        this.views = [];
    },

    addOne: function(like) {
        var view = new Yasound.Views.Like({
            model: like
        });
        $(this.el).append(view.render().el);
        this.views.push(view);
    }
});

Yasound.Views.UserLikesPage = Backbone.View.extend({
    collection: new Yasound.Data.Models.Likes({}),

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

    render: function(username) {
        this.reset();
        this.collection.perPage = Yasound.Utils.cellsPerPage();
        this.collection.setUsername(username);

        this.username = this.collection.username;
        $(this.el).html(ich.userLikesPageTemplate());

        this.user = new Yasound.Data.Models.User({username:username}),
        this.userView = new Yasound.Views.User({
            model: this.user,
            el: $('#user-profile', this.el)
        });
        this.user.fetch();

        this.resultsView = new Yasound.Views.Likes({
            collection: this.collection,
            el: $('#results', this.el)
        });

        this.paginationView = new Yasound.Views.Pagination({
            collection: this.collection,
            el: $('#pagination', this.el)
        });

        this.collection.fetch();

        return this;
    },

    onBack: function(e) {
        e.preventDefault();
        Yasound.App.Router.navigate("profile/" + this.username + '/', {
            trigger: true
        });
    }
});


/**
 * Profile page
 */
Yasound.Views.ProfilePage = Backbone.View.extend({
    events: {
        'click #radios-btn': 'displayRadios',
        'click #favorites-btn': 'displayFavorites',
        'click #friends-btn': 'displayFriends',
        'click #followers-btn': 'displayFollowers',
        'click #likes-btn': 'displayLikes'
    },
    initialize: function () {
        _.bindAll(this, 'render');
        this.model.bind('change', this.render, this);
    },

    onClose: function () {
        this.model.unbind('change', this.render, this);
    },

    reset: function () {
    },

    render: function () {
        this.reset();
        var data = this.model.toJSON();
        $(this.el).html(ich.profilePageTemplate(data));

        this.userView = new Yasound.Views.User({
            model: this.model,
            el: $('#user-profile', this.el)
        }).render();

        this.currentRadioView = new Yasound.Views.RadioCell({
            model: this.model.currentRadio,
            el: $('#current-radio', this.el)
        });

        this.radios = new Yasound.Data.Models.UserRadios({});
        this.radios.perPage = 6;

        this.radiosView = new Yasound.Views.SearchResults({
            collection: this.radios,
            el: $('#radios', this.el)
        });

        this.ownRadioView = new Yasound.Views.RadioCell({
            model: this.model.ownRadio,
            el: $('#own-radio', this.el)
        });

        this.favorites = new Yasound.Data.Models.Favorites({});
        this.favorites.perPage = 6;

        this.favoritesView = new Yasound.Views.SearchResults({
            collection: this.favorites,
            el: $('#favorites', this.el)
        });

        this.friends = new Yasound.Data.Models.Friends({});
        this.friends.perPage = 5;
        this.friendsView = new Yasound.Views.Friends({
            collection: this.friends,
            el: $('#friends', this.el)
        });

        this.followers = new Yasound.Data.Models.Followers({});
        this.followers.perPage = 5;
        this.followersView = new Yasound.Views.Friends({
            collection: this.followers,
            el: $('#followers', this.el)
        });

        this.likes = new Yasound.Data.Models.Likes({});
        this.likes.perPage = 4;
        this.likesView = new Yasound.Views.Likes({
            collection: this.likes,
            el: $('#likes', this.el)
        });

        var username = this.model.get('username');
        this.radios.setUsername(username).fetch();
        this.favorites.setUsername(username).fetch();
        this.friends.setUsername(username).fetch();
        this.followers.setUsername(username).fetch();
        this.likes.setUsername(username).fetch();
        return this;
    },

    displayRadios: function(e) {
        e.preventDefault();
        var username = this.model.get('username');

        if (username == Yasound.App.username) {
            // display radios with stats for current user
            Yasound.App.Router.navigate("radios/", {
                trigger: true
            });
        } else {
            Yasound.App.Router.navigate("profile/" + username + '/radios/', {
                trigger: true
            });
        }


    },

    displayFavorites: function (e) {
        e.preventDefault();
        var username = this.model.get('username');
        Yasound.App.Router.navigate("profile/" + username + '/favorites/', {
            trigger: true
        });
    },

    displayFriends: function (e) {
        e.preventDefault();
        var username = this.model.get('username');
        Yasound.App.Router.navigate("profile/" + username + '/friends/', {
            trigger: true
        });
    },

    displayFollowers: function (e) {
        e.preventDefault();
        var username = this.model.get('username');
        Yasound.App.Router.navigate("profile/" + username + '/followers/', {
            trigger: true
        });
    },

    displayLikes: function (e) {
        e.preventDefault();
        var username = this.model.get('username');
        Yasound.App.Router.navigate("profile/" + username + '/likes/', {
            trigger: true
        });
    }
});
