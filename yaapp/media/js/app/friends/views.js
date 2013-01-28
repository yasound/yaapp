/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Views');

Yasound.Views.FriendsSlide = Backbone.View.extend({

    events: {
        'click a.asset-slide-right': 'onSlide',
        'click a.asset-slide-left': 'onSlide'
    },

    currentStep: 0,
    lastStep: 1,

    initialize: function() {
        _.bindAll(this, 'addOne', 'addAll', 'onSlide', 'resetSlide', 'getSlideOffset', 'onWindowResized');

        this.collection.bind('add', this.addOne, this);
        this.collection.bind('reset', this.addAll, this);
        this.collection.bind('beforeFetch', this.beforeFetch, this);
        this.views = [];

        $(window).bind('resize', this.onWindowResized);
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
            var mask = $('.loading-mask', this.el);
            this.loadingMask = mask;
        }

        this.loadingMask.remove();
        this.loadingMask = undefined;

        if (this.collection.length === 0) {
            $('.empty', this.el).show();
        } else {
            $('.empty', this.el).hide();
        }
        this.currentRadioIndex = 0;
        this.collection.each(this.addOne);
        this.resetSlide();
    },

    clear: function() {
        _.map(this.views, function(view) {
            view.close();
        });
        this.views = [];
        $('ul', this.el).remove();

        this.currentStep = 0;
        this.lastStep = 1;
        this.currentRadioIndex = 0;
        this.resetSlide();
        this.$('.block-slide').animate({ marginLeft: '-' + this.currentStep*this.getSlideOffset() + 'px' });
    },

    addOne: function(user) {
        if (this.currentRadioIndex === 0 ) {
            this.cellsRange = $('<ul/>').appendTo(this.$('.block-slide'));
        } else if ( this.currentRadioIndex % 5 === 0) {
            this.cellsRange = $('<ul/>').appendTo(this.$('.block-slide'));
        }
        var view = new Yasound.Views.UserCell({
            model: user
        });
        this.cellsRange.append(view.render().el);
        this.views.push(view);
        this.currentRadioIndex++;
    },

    resetSlide: function() {
        var cells = this.$('li');
        if(cells.length > 0) {
            var cellWidth = $(cells.get(0)).outerWidth(true);
            this.$('.block-slide').width(cells.length*cellWidth + 'px');
        }
        this.lastStep = this.$('ul').length;
    },

    onSlide: function(e) {
        e.preventDefault();

        var previousStep = this.currentStep;
        var btn = $(e.currentTarget);

        if(btn.hasClass('asset-slide-right') && this.currentStep < this.lastStep-1) this.currentStep++;
        else if(btn.hasClass('asset-slide-left') && this.currentStep !== 0) this.currentStep--;

        if(this.currentStep === 0) this.$el.addClass('first');
        else this.$el.removeClass('first');

        if(this.currentStep === this.lastStep - 1) this.$el.addClass('last');
        else this.$el.removeClass('last');

        this.$('.block-slide').animate({ marginLeft: '-' + this.currentStep*this.getSlideOffset() + 'px' });

        if (previousStep < this.currentStep) {
            this.collection.requestNextPage();
        }
    },

    getSlideOffset: function() {
        var ranges = this.$('ul');
        if(ranges.length === 0) return 0;
        else return $(ranges.get(0)).outerWidth(true);
    },

    onWindowResized: function() {
        this.resetSlide();
        this.$('.block-slide').css('marginLeft', '-' + this.currentStep*this.getSlideOffset() + 'px');
    }

});


Yasound.Views.GoogleContact = Backbone.View.extend({
    tagName: 'tr',

    initialize: function () {
        _.bindAll(this, 'render');
        this.model.bind('change', this.render, this);
    },

    onClose: function () {
        this.model.unbind('change', this.render);
    },

    render: function () {
        var data = this.model.toJSON();
        $(this.el).html(ich.googleContactTemplate(data));
        return this;
    }
});

Yasound.Views.GoogleContacts = Backbone.View.extend({
    collection: new Yasound.Data.Models.GoogleContacts({}),
    events: {
    },

    initialize: function () {
        _.bindAll(this, 'render', 'addOne', 'addAll', 'onDestroy', 'onSelect');

        this.collection.bind('add', this.addOne, this);
        this.collection.bind('reset', this.addAll, this);
        this.collection.bind('destroy', this.onDestroy, this);
        this.views = [];
    },

    render: function(data) {
        var collection = this.collection;
        collection.reset();
        _.each(data.feed.entry, function (entry) {
            _.each(entry['gd$email'], function (email) {
                var contact = {
                    name: entry.title['$t'],
                    email: email.address
                };
                collection.add(contact);
            });
        });

        return this;
    },

    onClose: function () {
        this.collection.unbind('add', this.addOne);
        this.collection.unbind('reset', this.addAll);
        this.collection.unbind('destroy', this.onDestroy);
    },

    addAll: function () {
        $('.loading-mask', this.el).remove();
        this.collection.each(this.addOne);
    },

    clear: function () {
        _.map(this.views, function (view) {
            view.close();
        });
        this.views = [];
    },

    addOne: function (contact) {
        var view = new Yasound.Views.GoogleContact({
            model: contact
        });
        var that = this;
        $(this.el).append(view.render().el);
        view.$el.on('click', function () {
            that.onSelect(contact);
        });
        this.views.push(view);
    },

    onDestroy: function(model) {
        this.clear();
    },

    onSelect: function (contact) {
        var email = contact.get('email');
        $('#modal-invite-email #recipients').change();
        var recipients = $('#modal-invite-email #recipients').val();
        if (recipients.length == 0) {
            recipients = email;
        } else {
            recipients = recipients + ', ' + email;
        }
        $('#modal-invite-email #recipients').val(recipients);
        $('#modal-google-contacts').modal('hide');
    }
});


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
    connected: new Yasound.Data.Models.ConnectedUsers({}),

    events: {
        'click #login-btn': 'onLogin',
        'click #invite-facebook': 'onInviteFacebook',
        'click #invite-twitter': 'onInviteTwitter',
        'click #invite-email': 'onInviteEmail',
        'click #google-contacts': 'onGoogleContacts'
    },

    initialize: function() {
        _.bindAll(this, 'render', 'notifyFacebookInvitations', 'notifyTwitterInvitations');
    },

    onClose: function() {
    },

    reset: function() {
        this.collection.perPage = 15;
        this.collection.page = 0;
        this.followers.perPage = 15;
        this.followers.page = 0;
        this.connected.perPage = 15;
        this.connected.page = 0;

        if (this.resultsView) {
            this.resultsView.close();
            this.resultsViews = undefined;
        }
        if (this.followersView) {
            this.followersView.close();
            this.followersView = undefined;
        }
        if (this.connectedView) {
            this.connectedView.close();
            this.connectedView = undefined;
        }
    },

    render: function() {
        this.reset();
        $(this.el).html(ich.friendsPageTemplate());

        this.resultsView = new Yasound.Views.FriendsSlide({
            collection: this.collection,
            el: $('#following-slides', this.el)
        });

        this.followersView = new Yasound.Views.FriendsSlide({
            collection: this.followers,
            el: $('#followers-slides', this.el)
        });

        this.connectedView = new Yasound.Views.FriendsSlide({
            collection: this.connected,
            el: $('#connected-slides', this.el)
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
            this.connected.fetch({
                success: function (collection, response) {
                    $('#connected-count', that.el).html(collection.totalCount);
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
        var twitterText = gettext('Join me on #yasound') + ' ' + g_twitter_referal;
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
        var body = gettext('Join me on yasound:') + ' ' + g_email_referal;
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
        };
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
    },

    onGoogleContacts: function (e) {
        e.preventDefault();
        var clientId = '271869463998-dvtuhiri7dp06ni4vopm8n68bo96tah2.apps.googleusercontent.com';
        var apiKey = 'AIzaSyA9pqwDu4yveBRTUXHEASUFNWgyt7le0Ak';
        var scopes = 'https://www.google.com/m8/feeds';

        function handleClientLoad() {
          gapi.client.setApiKey(apiKey);
          window.setTimeout(checkAuth,1);
        }

        function checkAuth() {
          gapi.auth.authorize({client_id: clientId, scope: scopes, immediate: true}, handleAuthResult);
        }

        function handleAuthResult(authResult) {
          if (authResult && !authResult.error) {

            var token = gapi.auth.getToken();
            $.ajax({
                url: 'https://www.google.com/m8/feeds/contacts/default/full',
                dataType: 'jsonp',
                data: {
                    access_token: token.access_token,
                    alt: 'json-in-script'
                },
                success: function(data, status) {
                    var view = new Yasound.Views.GoogleContacts({
                        tagName: 'tbody'
                    }).render(data);

                    $('#google-contacts-list').append(view.el);

                    $('#modal-google-contacts').modal('show');
                    $('#modal-google-contacts').one('hidden', function () {
                        view.close();
                    });

                }
            });
          } else {
            console.log(authResult);
          }
        }

        gapi.auth.authorize({client_id: clientId, scope: scopes, immediate: false}, handleAuthResult);

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
