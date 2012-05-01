Namespace('Yasound.Views');


Yasound.Views.Favorites = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this, 'addOne', 'addAll');

        this.collection.bind('add', this.addOne, this);
        this.collection.bind('reset', this.addAll, this);
        this.views = [];
    },
    onClose: function() {
        this.collection.unbind('add', this.addOne);
        this.collection.unbind('reset', this.addAll);
    },

    addAll: function() {
        this.collection.each(this.addOne);
    },

    clear: function() {
        _.map(this.views, function(view) {
            view.close();
        })
        this.views = [];
    },

    addOne: function(radio) {
        var currentId = radio.id;

        var found = _.find(this.views, function(view) {
            if (view.model.id == radio.id) {
                return true;
            }
        })
        if (found) {
            // do not insert duplicated content
            return;
        }

        var view = new Yasound.Views.RadioCell({
            model: radio
        });

        var lastView = _.max(this.views, function(view) {
            return view.model.get('id');
        });
        var lastId = 0;
        if (lastView) {
            var lastId = lastView.model.id;
        }
        if (currentId >= lastId) {
            $(this.el).prepend(view.render().el);
            // in case of prepend, it means that the wall has been refreshed
            // with new item
            // so we remove the last one in order to avoid infinite addition to
            // the wall
            if (this.views.length >= this.collection.perPage) {
                this.views[0].close();
                this.views.splice(0, 1)
            }
        } else {
            $(this.el).append(view.render().el);
        }
        this.views.push(view);
    }
});

Yasound.Views.FavoritesPage = Backbone.View.extend({
    name: 'favoritepage',
    
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
        $(this.el).html(ich.favoritesPageTemplate());
        
        this.resultsView = new Yasound.Views.SearchResults({
            collection: this.collection,
            el: $('#results', this.el)
        });
        
        this.collection.fetch();
        
        return this;
    }
});