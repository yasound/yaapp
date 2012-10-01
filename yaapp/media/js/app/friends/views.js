/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Views');


Yasound.Views.Friends = Backbone.View.extend({
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
        $('.loading-mask', this.el).remove();
        this.collection.each(this.addOne);
    },

    clear: function() {
        _.map(this.views, function(view) {
            view.close();
        });
        this.views = [];
    },

    addOne: function(user) {
        var currentId = user.id;

        var found = _.find(this.views, function(view) {
            if (view.model.get('username') == user.get('username')) {
                return true;
            }
        });
        if (found) {
            // do not insert duplicated content
            return;
        }

        var view = new Yasound.Views.UserCell({
            model: user
        });

        var lastView = _.max(this.views, function(view) {
            return view.model.get('id');
        });
        var lastId = 0;
        if (lastView) {
            lastId = lastView.model.id;
        }
        $(this.el).append(view.render().el);
        this.views.push(view);
    }
});

Yasound.Views.FriendsPage = Backbone.View.extend({
    collection: new Yasound.Data.Models.Friends({}),
    followers: new Yasound.Data.Models.Followers({}),

    events: {
        'click #login-btn': 'onLogin',
        'click #invite-facebook': 'onInviteFacebook'
    },

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
        if (this.followersView) {
            this.followersView.close();
            this.followersView = undefined;
        }
    },

    render: function() {
        this.reset();
        this.collection.perPage = Yasound.Utils.userCellsPerPage();
        this.followers.perPage = Yasound.Utils.userCellsPerPage();
        $(this.el).html(ich.friendsPageTemplate());

        this.resultsView = new Yasound.Views.Friends({
            collection: this.collection,
            el: $('#results', this.el)
        });

        this.paginationView = new Yasound.Views.Pagination({
            collection: this.collection,
            el: $('#pagination', this.el)
        });

        this.followersView = new Yasound.Views.Friends({
            collection: this.followers,
            el: $('#followers', this.el)
        });

        this.followersPaginationView = new Yasound.Views.Pagination({
            collection: this.followers,
            el: $('#followers-pagination', this.el)
        });


        var that = this;
        if (Yasound.App.userAuthenticated) {
            this.collection.fetch({
                success: function (collection, response) {
                    $('#friends-count', that.el).html(collection.totalCount);
                }
            });
            this.followers.fetch({
                success: function (collection, response) {
                    $('#followers-count', that.el).html(collection.totalCount);
                }
            });
        }

        return this;
    },

    onLogin: function (e) {
        e.preventDefault();
        Yasound.App.Router.navigate("login/", {
            trigger: true
        });
    },

    onInviteFacebook: function (e) {
        e.preventDefault();
        FB.ui({
            method: 'apprequests',
            display: 'popup',
            message: gettext('Join me on Yasound and let\'s share music'),
            picture: g_facebook_share_picture
        }, function(response) {
            if(response && response.hasOwnProperty('to')) {
                for(i = 0; i < response.to.length; i++) {
                    console.log("" + i + " ID: " + response.to[i]);
                }
            }
        });
    }
});

Yasound.Views.UserFriendsPage = Backbone.View.extend({
    collection: new Yasound.Data.Models.Friends({}),

    events: {
        'click #back-btn': 'onBack'
    },

    initialize: function() {
        _.bindAll(this, 'render', 'onBack');
    },

    onClose: function() {
    },

    reset: function() {
        if (this.resultsView) {
            this.resultsView.close();
            this.resultsViews = undefined;
        }
    },

    render: function(username) {
        this.reset();
        this.collection.perPage = Yasound.Utils.userCellsPerPage();
        this.collection.setUsername(username);

        this.username = this.collection.username;
        $(this.el).html(ich.userFriendsPageTemplate());
        this.resultsView = new Yasound.Views.Friends({
            collection: this.collection,
            el: $('#results', this.el)
        });

        this.paginationView = new Yasound.Views.Pagination({
            collection: this.collection,
            el: $('#pagination', this.el)
        });

        this.collection.fetch();

        return this;
    },

    onBack: function(e) {
        e.preventDefault();
        Yasound.App.Router.navigate("profile/" + this.username + '/', {
            trigger: true
        });
    }
});

Yasound.Views.UserFollowersPage = Backbone.View.extend({
    collection: new Yasound.Data.Models.Followers({}),

    events: {
        'click #back-btn': 'onBack'
    },

    initialize: function() {
        _.bindAll(this, 'render', 'onBack');
    },

    onClose: function() {
    },

    reset: function() {
        if (this.resultsView) {
            this.resultsView.close();
            this.resultsViews = undefined;
        }
    },

    render: function(username) {
        this.reset();
        this.collection.perPage = Yasound.Utils.userCellsPerPage();
        this.collection.setUsername(username);

        this.username = this.collection.username;
        $(this.el).html(ich.userFollowersPageTemplate());
        this.resultsView = new Yasound.Views.Friends({
            collection: this.collection,
            el: $('#results', this.el)
        });

        this.paginationView = new Yasound.Views.Pagination({
            collection: this.collection,
            el: $('#pagination', this.el)
        });

        this.collection.fetch();

        return this;
    },

    onBack: function(e) {
        e.preventDefault();
        Yasound.App.Router.navigate("profile/" + this.username + '/', {
            trigger: true
        });
    }
});
