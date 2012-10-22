/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Views');

Yasound.Views.FavoritesPage = Backbone.View.extend({
    collection: new Yasound.Data.Models.Favorites({}),
    events: {
        'click #login-btn': 'onLogin'
    },

    initialize: function() {
        _.bindAll(this, 'render', 'onGenreChanged', 'updateGenreSlug');
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

    render: function(genre) {
        this.reset();
        $(this.el).html(ich.favoritesPageTemplate());
        this.collection.perPage = Yasound.Utils.cellsPerPage();

        this.resultsView = new Yasound.Views.SearchResults({
            collection: this.collection,
            el: $('#results', this.el)
        });

        this.paginationView = new Yasound.Views.Pagination({
            collection: this.collection,
            el: $('#pagination', this.el)
        }).setTitle(gettext('Next favorites'));

        this.updateGenreSlug(genre);
        if (Yasound.App.userAuthenticated) {
            this.onGenreChanged('', genre);
        }
        return this;
    },

    updateGenreSlug: function (genre) {
        var found = (/^style_/).test(genre);
        if (found) {
            var prefix_length = 'style_'.length;
            var genre_slug = genre.substr(prefix_length, genre.length - prefix_length);
            Yasound.App.Router.navigate("favorites/" + genre_slug + '/', {
                trigger: false
            });
        } else {
            Yasound.App.Router.navigate("favorites/", {
                trigger: false
            });
        }
    },


    onGenreChanged: function(e, genre) {
        this.updateGenreSlug(genre);
        if (genre === '') {
            this.collection.params.genre = undefined;
        } else {
            this.collection.params.genre = genre;
        }
        this.resultsView.clear();
        this.collection.goTo(0);
    },

    onLogin: function (e) {
        e.preventDefault();
        Yasound.App.Router.navigate("login/", {
            trigger: true
        });
    }
});

Yasound.Views.UserFavoritesPage = Backbone.View.extend({
    collection: new Yasound.Data.Models.Favorites({}),

    events: {
        'click #back-btn': 'onBack'
    },

    initialize: function() {
        _.bindAll(this, 'render', 'onGenreChanged');
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
        $(this.el).html(ich.userFavoritesPageTemplate());
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
        }).setTitle(gettext('Next radios'));

        this.onGenreChanged('', genre);
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
