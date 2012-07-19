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
    },

    initialize: function () {
        this.model.bind('change', this.render, this);
    },
    onClose: function () {
        this.model.unbind('change', this.render);
    },

    render: function () {
        var data = this.model.toJSON();
        data.human_date = this.model.humanDate();
        $(this.el).html(ich.userTemplate(data));
        return this;
    }
});

/**
 * Profile page
 */
Yasound.Views.ProfilePage = Backbone.View.extend({
    name: 'profilepage',
    
    initialize: function() {
        _.bindAll(this, 'render');
    },

    onClose: function() {
    },

    reset: function() {
    },

    render: function() {
        this.reset();
        $(this.el).html(ich.profilePageTemplate());
        
        this.userView = new Yasound.Views.User({
            model: this.model,
            el: $('#user-profile', this.el)
        });
        
        this.currentRadioView = new Yasound.Views.RadioCell({
            model: this.model.currentRadio,
            el: $('#current-radio', this.el)
        });

        this.ownRadioView = new Yasound.Views.RadioCell({
            model: this.model.ownRadio,
            el: $('#own-radio', this.el)
        });
        
        var favorites = new Yasound.Data.Models.Favorites({});
        
        this.favoritesView = new Yasound.Views.SearchResults({
            collection: favorites,
            el: $('#favorites', this.el)
        });
        this.paginationView = new Yasound.Views.Pagination({
            collection: favorites,
            el: $('#pagination', this.el)
        });
        
        
        this.model.fetch({
            success: function(model, response) {
                favorites.url = '/api/v1/user/' + model.get('id') + '/favorite_radio/';
                favorites.fetch();
            }
        });
        return this;
    }
});