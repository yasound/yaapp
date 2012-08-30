/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Views.Deezer');

Yasound.Views.Deezer.Playlist = Backbone.View.extend({
    initialize: function () {
        _.bindAll(this, 'render', 'addOne', 'addAll', 'onDestroy');

        this.collection.bind('add', this.addOne, this);
        this.collection.bind('reset', this.addAll, this);
        this.collection.bind('destroy', this.onDestroy, this);
        this.views = [];
    },

    render: function() {
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

    addOne: function (playlist) {
        var currentId = playlist.id;

        var found = _.find(this.views, function (view) {
            if (view.model.id == playlist.id) {
                return true;
            }
        });
        if (found) {
            // do not insert duplicated content
            return;
        }

        var view = new Yasound.Views.Deezer.PlaylistCell({
            model: playlist
        });
        $(this.el).append(view.render().el);
        this.views.push(view);
    },

    onDestroy: function(model) {
        this.clear();
        this.collection.fetch();
    }
});

Yasound.Views.ImportFromDeezer =  Backbone.View.extend({
    events: {
        "click #import-btn": "onImport"
    },

    initialize: function() {
        _.bindAll(this, 'render', 'fetchPlaylists');
    },

    onClose: function() {
    },

    reset: function() {
    },

    clear: function () {
    },

    render: function(uuid) {
        $(this.el).html(ich.importFromDeezerTemplate());

        var username = Yasound.App.username;
        this.playlists = new Yasound.Data.Models.Deezer.Playlists({}).setUsername(username);
        this.playlistsView = new Yasound.Views.Deezer.Playlist({
            el: $('#playlists', this.el),
            collection: this.playlists
        });


        this.playlists.fetch();
        return this;
    },

    onImport: function (e) {
        e.preventDefault();
        DZ.login(function(response) {
            if (response.authResponse) {
                this.fetchPlaylists();
            } else {
                console.log('User cancelled login or did not fully authorize.');
            }
        }, {perms: 'basic_access,email'});
    },

    fetchPlaylists: function (e) {
        DZ.api('/user/me/playlists', function(response) {
            console.log(response);
            DZ.logout();
        });
    }
});