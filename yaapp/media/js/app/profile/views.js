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
        'click #radio-activity': 'radio',
        'click #follow': 'follow'
    },

    initialize: function () {
        this.model.bind('change', this.render, this);
    },
    onClose: function () {
        this.model.unbind('change', this.render);
    },

    render: function () {
        var data = this.model.toJSON();
        if (data.current_radio && data.current_radio.name.length > 18) {
            data.current_radio.name = data.current_radio.name.substring(0,18) + "...";
        }
        
        $(this.el).html(ich.userTemplate(data));
        $('#picture img', this.el).imgr({size:"6px",color:"white",radius:"100%"});
        return this;
    },
    radio: function (e) {
        e.preventDefault();
        var uuid = this.model.get('history')['radio_uuid'];
        Yasound.App.Router.navigate("radio/" + uuid + '/', {
            trigger: true
        });
    },
    follow: function(e) {
        e.preventDefault();
        if (this.model.get('is_friend')) {
            $(e.target, this.el).html(gettext('Follow'));
            this.model.unfollow(Yasound.App.username);
        } else {
            $(e.target, this.el).html(gettext('Unfollow'))
            this.model.follow(Yasound.App.username);
        }
    }
});

/**
 * Profile page
 */
Yasound.Views.ProfilePage = Backbone.View.extend({
    events: {
        'click #radios-btn': 'displayRadios',
        'click #favorites-btn': 'displayFavorites',
        'click #friends-btn': 'displayFriends'
    },
    initialize: function () {
        _.bindAll(this, 'render', 'modelLoaded');
    },

    onClose: function () {
    },

    reset: function () {
    },

    render: function () {
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

        this.radios = new Yasound.Data.Models.UserRadios({});
        this.radios.perPage = 4;

        this.radiosView = new Yasound.Views.SearchResults({
            collection: this.radios,
            el: $('#radios', this.el)
        });

        this.ownRadioView = new Yasound.Views.RadioCell({
            model: this.model.ownRadio,
            el: $('#own-radio', this.el)
        });

        this.favorites = new Yasound.Data.Models.Favorites({});
        this.favorites.perPage = 4;

        this.favoritesView = new Yasound.Views.SearchResults({
            collection: this.favorites,
            el: $('#favorites', this.el)
        });

        this.friends = new Yasound.Data.Models.Friends({})
        this.friends.perPage = 5;
        this.friendsView = new Yasound.Views.Friends({
            collection: this.friends,
            el: $('#friends', this.el)
        });

        this.model.fetch({
            success: this.modelLoaded
        });
        return this;
    },
    
    modelLoaded: function(model, response) {
        this.radios.setUsername(model.get('username')).fetch();
        this.favorites.setUsername(model.get('username')).fetch();
        this.friends.setUsername(model.get('username')).fetch();
    },
    
    displayRadios: function(e) {
        e.preventDefault();
        var username = this.model.get('username');
        
        if (username == Yasound.App.username) {
            // display radios with stats for current user
            Yasound.App.Router.navigate("radios/", {
                trigger: true
            });
        } else {
            Yasound.App.Router.navigate("profile/" + username + '/radios/', {
                trigger: true
            });
        } 
        
        
    },

    displayFavorites: function (e) {
        e.preventDefault();
        var username = this.model.get('username')
        Yasound.App.Router.navigate("profile/" + username + '/favorites/', {
            trigger: true
        });
    },
    
    displayFriends: function (e) {
        e.preventDefault();
        var username = this.model.get('username')
        Yasound.App.Router.navigate("profile/" + username + '/friends/', {
            trigger: true
        });
    }
});