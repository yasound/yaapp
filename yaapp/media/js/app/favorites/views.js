/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Views');

Yasound.Views.FavoritesPage = Backbone.View.extend({
    collection: new Yasound.Data.Models.Favorites({}),
    
    initialize: function() {
        _.bindAll(this, 'render', 'onGenreChanged');
        $.subscribe('/submenu/genre', this.onGenreChanged)
    },

    onClose: function() {
        $.unsubscribe('/submenu/genre', this.onGenreChanged)
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
        });
        
        this.onGenreChanged('', genre)
        return this;
    },
    
    onGenreChanged: function(e, genre) {
        if (genre == '') {
            this.collection.params.genre = undefined;
        } else {
            this.collection.params.genre = genre;
        }
        this.resultsView.clear();
        this.collection.goTo(0);
    }    
});

Yasound.Views.UserFavoritesPage = Backbone.View.extend({
    collection: new Yasound.Data.Models.Favorites({}),

    events: {
        'click #back-btn': 'onBack'
    },
    
    initialize: function() {
        _.bindAll(this, 'render', 'onGenreChanged');
        $.subscribe('/submenu/genre', this.onGenreChanged)
    },

    onClose: function() {
        $.unsubscribe('/submenu/genre', this.onGenreChanged)
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
        }
        
        this.resultsView = new Yasound.Views.SearchResults({
            collection: this.collection,
            el: $('#results', this.el)
        });
        
        this.paginationView = new Yasound.Views.Pagination({
            collection: this.collection,
            el: $('#pagination', this.el)
        });
        
        this.onGenreChanged('', genre)
        return this;
    },
    
    onGenreChanged: function(e, genre) {
        if (genre == '') {
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