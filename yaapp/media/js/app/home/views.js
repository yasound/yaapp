/*
 * jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true,
 * evil: true, undef: true, white: true, newcap: true
 */
/* extern Ext, $ */
Namespace('Yasound.Views');

/**
 * Home page
 */
Yasound.Views.HomePage = Backbone.View.extend({
    collection: new Yasound.Data.Models.SelectedRadios({}),

    events: {
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

    render: function(genre) {
        this.reset();
        $(this.el).html(ich.homePageTemplate());

        this.collection.perPage = Yasound.Utils.cellsPerPage();

        this.resultsView = new Yasound.Views.SearchResults({
            collection: this.collection,
            el: $('#selected-radios', this.el)
        });

        this.paginationView = new Yasound.Views.Pagination({
            collection: this.collection,
            el: $('#pagination', this.el)
        }).setTitle(gettext('Next radios'));

        this.collection.params.genre = genre;

        if (g_bootstrapped_data) {
            this.collection.reset(g_bootstrapped_data, {'silent': true});
            this.collection.next = g_next_url;
            this.collection.baseUrl = g_base_url;
            this.collection.trigger('reset', this.collection);
        } else {
            this.collection.goTo(0);
        }

        return this;
    },

    onGenreChanged: function(e, genre) {
        this.collection.params.genre = genre;
        this.resultsView.clear();
        this.collection.goTo(0);
    }
});
