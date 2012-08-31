/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Views.Deezer');

Yasound.Views.Deezer.PlaylistCell = Backbone.View.extend({
    tagName: 'tr',
    events: {
        "click .details" : "onDetails"
    },

    initialize: function () {
        this.model.bind('change', this.render, this);
    },

    onClose: function () {
        this.model.unbind('change', this.render);
    },

    render: function () {
        var data = this.model.toJSON();
        $(this.el).html(ich.deezerPlaylistCellTemplate(data));
        return this;
    },

    onDetails: function (e) {
        e.preventDefault();
        this.trigger('loadPlaylist', this.model.get('id'));
    }
});


Yasound.Views.Deezer.Playlist = Backbone.View.extend({
    initialize: function () {
        _.bindAll(this, 'render', 'addOne', 'addAll', 'onDestroy', 'onLoadPlaylist');

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
            view.off('loadPlaylist', this.onLoadPlaylist);
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
        view.on('loadPlaylist', this.onLoadPlaylist);
        $(this.el).append(view.render().el);
        this.views.push(view);
    },

    onDestroy: function(model) {
        this.clear();
        this.collection.fetch();
    },

    onLoadPlaylist: function (id) {
        this.trigger('loadPlaylist', id);
    }
});

Yasound.Views.Deezer.TrackCell = Backbone.View.extend({
    tagName: 'tr',
    events: {
        "click .import": "onImport"
    },

    initialize: function () {
        _.bindAll(this, 'onImportSucceded', 'onImportFailed');
        this.model.bind('change', this.render, this);
    },

    onClose: function () {
        this.model.unbind('change', this.render);
    },

    render: function () {
        var data = this.model.toJSON();
        $(this.el).html(ich.deezerTrackCellTemplate(data));
        return this;
    },

    setUUID: function (uuid) {
        this.uuid = uuid;
        return this;
    },

    onImport: function (e) {
        e.preventDefault();
        this.model.addToRadio(this.uuid, this.onImportSucceded, this.onImportFailed);
    },

    onImportSucceded: function (message) {
        this.remove();
        collibri(gettext('song imported'));
    },

    onImportFailed: function (message) {
        colibri(message, 'colibri-error');
    }
});


Yasound.Views.Deezer.Tracks = Backbone.View.extend({
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

    setUUID: function (uuid) {
        this.uuid = uuid;
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

    addOne: function (track) {
        var currentId = track.id;

        var found = _.find(this.views, function (view) {
            if (view.model.id == track.id) {
                return true;
            }
        });
        if (found) {
            // do not insert duplicated content
            return;
        }

        var view = new Yasound.Views.Deezer.TrackCell({
            model: track
        });
        $(this.el).append(view.render().setUUID(this.uuid).el);
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
        _.bindAll(this, 'render', 'fetchPlaylists', 'onLoadPlaylist');
    },

    onClose: function() {
        if (this.playlistsView) {
            this.playlistsView.off('loadPlaylist', this.onLoadPlaylist);
            this.playlistsView.close();
        }
    },

    reset: function() {
    },

    clear: function () {
    },

    render: function(uuid) {
        $(this.el).html(ich.importFromDeezerTemplate());

        var username = Yasound.App.username;
        this.playlists = new Yasound.Data.Models.Deezer.Playlists({});
        this.playlistsView = new Yasound.Views.Deezer.Playlist({
            el: $('#playlists', this.el),
            collection: this.playlists
        });
        this.playlistsView.on('loadPlaylist', this.onLoadPlaylist);

        this.tracks = new Yasound.Data.Models.Deezer.Tracks({});
        this.tracksView = new Yasound.Views.Deezer.Tracks({
            el: $('#tracks', this.el),
            collection: this.tracks
        }).setUUID(uuid);

        return this;
    },

    onImport: function (e) {
        e.preventDefault();
        var that = this;
        DZ.login(function(response) {
            if (response.authResponse) {
                that.fetchPlaylists();
            } else {
                console.log('User cancelled login or did not fully authorize.');
            }
        }, {perms: 'basic_access,email'});

        // data = [{
        //     id:1,
        //     title: 'hello'
        // }, {
        //     id:2,
        //     title: 'foo'
        // }]
        // that.playlistsView.clear();
        // that.playlists.reset(data)
    },

    fetchPlaylists: function (e) {
        var that = this;
        DZ.api('/user/me/playlists', function(response) {
            if (response.data) {
                that.playlistsView.clear();
                that.playlists.reset(response.data);
            }
        });
    },

    onLoadPlaylist: function (id) {
        var that = this;
        DZ.api('/playlist/' + id, function(response) {
            if (response.tracks && response.tracks.data) {
                that.tracksView.clear();
                that.tracks.reset(response.tracks.data);
            }
        });

        // if (id ==1) {
        //     data = [{
        //         id: 1,
        //         title: 'track1',
        //         artist: {
        //             name: 'artist'
        //         },
        //         album: {
        //             title: 'album'
        //         }
        //     }, {
        //         id: 2,
        //         title: 'track2',
        //         artist: {
        //             name: 'artist'
        //         },
        //         album: {
        //             title: 'album'
        //         }
        //     }
        //     ];
        // } else {
        //     data = [{
        //         id: 3,
        //         title: 'track12',
        //         artist: {
        //             name: 'artist'
        //         },
        //         album: {
        //             title: 'album'
        //         }
        //     }, {
        //         id: 4,
        //         title: 'track22',
        //         artist: {
        //             name: 'artist'
        //         },
        //         album: {
        //             title: 'album'
        //         }
        //     }
        //     ];

        // }
        // that.tracksView.clear();
        // that.tracks.reset(data)
    }
});