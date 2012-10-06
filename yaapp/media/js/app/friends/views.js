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
        'click #invite-facebook': 'onInviteFacebook',
        'click #invite-twitter': 'onInviteTwitter',
        'click #invite-email': 'onInviteEmail'
    },

    initialize: function() {
        _.bindAll(this, 'render', 'notifyFacebookInvitations', 'notifyTwitterInvitations');
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
        var that = this;
        e.preventDefault();
        FB.ui({
            method: 'apprequests',
            display: 'popup',
            message: gettext('Join me on Yasound and let\'s share music'),
            picture: g_facebook_share_picture
        }, function(response) {
            if(response && response.hasOwnProperty('to')) {
                var users = [];
                for(i = 0; i < response.to.length; i++) {
                    users.push(response.to[i]);
                }
                that.notifyFacebookInvitations(users);
            }
        });
    },

    onInviteTwitter: function (e) {
        e.preventDefault();
        if (!g_twitter_referal) {
            Yasound.Utils.dialog(gettext('Error'), gettext('You must be logged in'));
            return;
        }
        var twitterText = gettext('Join me on #yasound ' + g_twitter_referal);
        $('#modal-invite-twitter textarea').val(twitterText);

        $('#modal-invite-twitter').modal('show');
        var that = this;
        $('#modal-invite-twitter .btn-primary').one('click', function () {
            $('#modal-invite-twitter').modal('hide');
            var val = $('#modal-invite-twitter textarea').val();
            that.notifyTwitterInvitations(val);
        });

    },

    onInviteEmail: function (e) {
        e.preventDefault();
        var body = gettext('Join me on yasound: ' + g_email_referal);
        var subject = gettext('Join me on Yasound');

        $('#modal-invite-email textarea').val(body);
        $('#modal-invite-email #recipients').val('');
        $('#modal-invite-email #subject').val(subject);

        $('#modal-invite-email').modal('show');
        var that = this;
        $('#modal-invite-email .btn-primary').one('click', function () {
            $('#modal-invite-email').modal('hide');
            var message = $('#modal-invite-email textarea').val();
            var subject = $('#modal-invite-email #subject').val();
            var recipients = $('#modal-invite-email #recipients').val();
            that.notifyEmailInvitations(recipients, subject, message);
        });

    },

    notifyFacebookInvitations: function (users) {
        var url = '/api/v1/invite_facebook_friends/';
        $.ajax({
            url: url,
            type: 'POST',
            dataType: 'json',
            data: JSON.stringify(users),
            contentType: 'application/json',
            success: function(data) {
                if (!(data.success)) {
                    Yasound.Utils.dialog(gettext('Error'), data.error);
                } else {
                    Yasound.Utils.dialog(gettext('Thank you'), gettext('Your friends have been invited successfully.'));
                }
            },
            failure: function() {
                Yasound.Utils.dialog(gettext('Error'), gettext('Error while communicating with Yasound, please retry late'));
            }
        });
    },

    notifyTwitterInvitations: function (message) {
        var url = '/api/v1/invite_twitter_friends/';
        $.ajax({
            url: url,
            type: 'POST',
            dataType: 'json',
            data: JSON.stringify({message: message}),
            success: function(data) {
                if (!(data.success)) {
                    Yasound.Utils.dialog(gettext('Error'), data.error);
                } else {
                    Yasound.Utils.dialog(gettext('Thank you'), gettext('Your friends have been invited successfully.'));
                }
            },
            failure: function() {
                Yasound.Utils.dialog(gettext('Error'), gettext('Error while communicating with Yasound, please retry late'));
            }
        });
    },

    notifyEmailInvitations: function (recipients, subject, message) {
        var url = '/api/v1/invite_email_friends/';
        var data = {
            recipients: recipients,
            subject: subject,
            message: message
        }
        $.ajax({
            url: url,
            type: 'POST',
            dataType: 'json',
            data: JSON.stringify(data),
            success: function(data) {
                if (!(data.success)) {
                    Yasound.Utils.dialog(gettext('Error'), data.error);
                } else {
                    Yasound.Utils.dialog(gettext('Thank you'), gettext('Your friends have been invited successfully.'));
                }
            },
            failure: function() {
                Yasound.Utils.dialog(gettext('Error'), gettext('Error while communicating with Yasound, please retry late'));
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

        this.user = new Yasound.Data.Models.User({username:username}),
        this.userView = new Yasound.Views.User({
            model: this.user,
            el: $('#user-profile', this.el)
        });
        this.user.fetch();


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

        this.user = new Yasound.Data.Models.User({username:username}),
        this.userView = new Yasound.Views.User({
            model: this.user,
            el: $('#user-profile', this.el)
        });
        this.user.fetch();

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
