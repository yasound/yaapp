/*
 * jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true,
 * evil: true, undef: true, white: true, newcap: true
 */
/* extern Ext, $ */
Namespace('Yasound.Views');


Yasound.Views.RadiosSlide = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this, 'addOne', 'addAll');

        this.collection.bind('add', this.addOne, this);
        this.collection.bind('reset', this.addAll, this);
        this.collection.bind('beforeFetch', this.beforeFetch, this);
        this.views = [];
    },
    onClose: function() {
        this.collection.unbind('beforeFetch', this.beforeFetch);
        this.collection.unbind('add', this.addOne);
        this.collection.unbind('reset', this.addAll);
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

        if (this.collection.length === 0) {
            $('.empty', this.el).show();
        } else {
            $('.empty', this.el).hide();
        }
        this.currentRadioIndex = 0;
        this.collection.each(this.addOne);
    },

    clear: function() {
        _.map(this.views, function(view) {
            view.close();
        });
        this.views = [];
    },

    addOne: function(radio) {
        if (this.currentRadioIndex === 0 ) {
            this.cellsRange = $('<ul/>').appendTo(this.el);
        } else if ( this.currentRadioIndex % 5 === 0) {
            this.cellsRange = $('<ul/>').appendTo(this.el);
        }
        var view = new Yasound.Views.RadioCell({
            model: radio
        });
        this.cellsRange.append(view.render().el);
        this.views.push(view);
        this.currentRadioIndex++;
    }
});

/**
 * Home page
 */
Yasound.Views.HomePage = Backbone.View.extend({

    events: {
    },

    initialize: function() {
        _.bindAll(this, 'render', 'onGenreChanged', 'updateGenreSlug');
        $.subscribe('/submenu/genre', this.onGenreChanged);

        this.selection = new Yasound.Data.Models.SelectedRadios({});
        this.favorites = new Yasound.Data.Models.SelectedRadios({});
        this.popular = new Yasound.Data.Models.SelectedRadios({});

    },

    onClose: function() {
        $.unsubscribe('/submenu/genre', this.onGenreChanged);
    },

    reset: function() {
        if (this.selectionView) {
            this.selectionView.close();
            this.selectionView = undefined;
        }
        if (this.favoritesView) {
            this.favoritesView.close();
            this.favoritesView = undefined;
        }
        if (this.popularView) {
            this.popularView.close();
            this.popularView = undefined;
        }
    },

    render: function(genre) {
        this.reset();
        $(this.el).html(ich.homePageTemplate());

        this.selectionView = new Yasound.Views.RadiosSlide({
            collection: this.selection,
            el: $('#selection-slides', this.el)
        });
        this.favoritesView = new Yasound.Views.RadiosSlide({
            collection: this.favorites,
            el: $('#favorites-slides', this.el)
        });
        this.popularView = new Yasound.Views.RadiosSlide({
            collection: this.popular,
            el: $('#popular-slides', this.el)
        });

        this.selection.goTo(0);
        this.favorites.goTo(0);
        this.popular.goTo(0);

        this.updateGenreSlug(genre);
        return this;
    },

    updateGenreSlug: function (genre) {
        var found = (/^style_/).test(genre);
        if (found) {
            var prefix_length = 'style_'.length;
            var genre_slug = genre.substr(prefix_length, genre.length - prefix_length);
            Yasound.App.Router.navigate('selection/' + genre_slug + '/', {
                trigger: false
            });
        } else {
            Yasound.App.Router.navigate("", {
                trigger: false
            });
        }
    },

    onGenreChanged: function(e, genre) {
        this.updateGenreSlug(genre);
    }
});
