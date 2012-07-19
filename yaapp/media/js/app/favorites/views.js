/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Views');

Yasound.Views.FavoritesPage = Backbone.View.extend({
    collection: new Yasound.Data.Models.Favorites({}),
    
    initialize: function() {
        _.bindAll(this, 'render', 'onGenreChanged', 'cellsPerPage');
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

    cellsPerPage: function() {
        var viewportHeight = $(window).height();
        var headerHeight = $('#header').height();
        var footerHeight = $('#footer').height();
        var containerHeight = viewportHeight - headerHeight - footerHeight;
        
        var cellHeight = 217;
        
        var rows =  Math.ceil(containerHeight / cellHeight);
        return rows*4;
    },
    
    render: function(genre) {
        this.reset();
        $(this.el).html(ich.favoritesPageTemplate());
        this.collection.perPage = this.cellsPerPage()
        
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