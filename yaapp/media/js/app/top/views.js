/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Views');

Yasound.Views.TopRadiosPage = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this, 'render');
    },

    onClose: function() {
    },

    reset: function() {
        if (this.resultsView) {
            this.resultsView.close();
            this.resultsViews = undefined;
        }
    },

    render: function() {
        this.reset();
        $(this.el).html(ich.topRadiosPageTemplate());
        
        this.resultsView = new Yasound.Views.SearchResults({
            collection: this.collection,
            el: $('#results', this.el)
        });
        
        this.paginationView = new Yasound.Views.Pagination({
            collection: this.collection,
            el: $('#pagination', this.el)
        });
        
        this.collection.fetch();
        
        return this;
    }
});