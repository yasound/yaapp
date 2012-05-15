"use strict";
/*
 * jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true,
 * evil: true, undef: true, white: true, newcap: true
 */
/* extern Ext, $ */
Namespace('Yasound.Views');


/**
 * Selected radios view
 */
Yasound.Views.SelectedRadios = Backbone.View.extend({
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

    addOne: function (radio) {
        var found = _.find(this.views, function (view) {
            if (view.model.id == radio.id) {
                return true;
            }
        });

        if (found) {
            // do not insert duplicated content
            return;
        }

        var view = new Yasound.Views.RadioCell({
            model: radio
        });

        $(this.el).prepend(view.render().el);
        this.views.push(view);
    }
});


/**
 * Home page
 */
Yasound.Views.HomePage = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this, 'render');
    },

    onClose: function() {
    },

    reset: function() {
    },

    render: function() {
        this.reset();
        $(this.el).html(ich.homePageTemplate());
        
        this.selectedRadios = new Yasound.Data.Models.SelectedRadios({});
        this.selectedRadiosView = new Yasound.Views.SelectedRadios({
            collection: this.selectedRadios,
            el: $('#selected-radios', this.el)
        });

        this.mostActiveRadios = new Yasound.Data.Models.MostActiveRadios({});
        this.mosteActiveRadiosView = new Yasound.Views.SelectedRadios({
            collection: this.mostActiveRadios,
            el: $('#most-active-radios', this.el)
        });
        
        if (Yasound.App.userAuthenticated) {
            this.favorites = new Yasound.Data.Models.Favorites({});
            this.favoritesViews = new Yasound.Views.SearchResults({
                collection: this.favorites,
                el: $('#favorites', this.el)
            });
            this.favorites.fetch();
        }
        
        this.selectedRadios.fetch();
        this.mostActiveRadios.fetch();
        return this;
    }
});