/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Views');

Yasound.Views.TopRadiosPage = Backbone.View.extend({
    collection: new Yasound.Data.Models.MostActiveRadios({}),

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

        $(this.el).html(ich.topRadiosPageTemplate());
        this.collection.perPage = Yasound.Utils.cellsPerPage();

        this.resultsView = new Yasound.Views.SearchResults({
            collection: this.collection,
            el: $('#results', this.el)
        });

        this.paginationView = new Yasound.Views.Pagination({
            collection: this.collection,
            el: $('#pagination', this.el)
        });

        this.collection.params.genre = genre;

        if (g_bootstrapped_data) {
            this.collection.reset(g_bootstrapped_data);
        } else {
            this.collection.fetch();
        }

        return this;
    },

    onGenreChanged: function(e, genre) {
        this.collection.params.genre = genre;
        this.resultsView.clear();
        this.collection.goTo(0);
    }
});