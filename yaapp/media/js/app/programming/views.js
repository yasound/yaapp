/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Views');

Yasound.Views.SongInstance = Backbone.View.extend({
    tagName: 'tr',
    events: {
        "click .remove": 'onRemove'
    },

    initialize: function () {
        this.model.bind('change', this.render, this);
    },

    onClose: function () {
        this.model.unbind('change', this.render);
    },

    render: function () {
        var data = this.model.toJSON();
        $(this.el).html(ich.songInstanceCellTemplate(data));
        return this;
    },

    onRemove: function (e) {
        e.preventDefault();
        this.model.destroy();
    }
});

Yasound.Views.SongInstances = Backbone.View.extend({
    initialize: function () {
        _.bindAll(this, 'addOne', 'addAll', 'onDestroy');

        this.collection.bind('add', this.addOne, this);
        this.collection.bind('reset', this.addAll, this);
        this.collection.bind('destroy', this.onDestroy, this);
        this.views = [];
    },

    onClose: function () {
        this.collection.unbind('add', this.addOne);
        this.collection.unbind('reset', this.addAll);
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

    addOne: function (songInstance) {
        var currentId = songInstance.id;

        var found = _.find(this.views, function (view) {
            if (view.model.id == songInstance.id) {
                return true;
            }
        });
        if (found) {
            // do not insert duplicated content
            return;
        }

        var view = new Yasound.Views.SongInstance({
            model: songInstance
        });
        $(this.el).append(view.render().el);
        this.views.push(view);
    },

    onDestroy: function(model) {
        this.clear();
        this.collection.fetch();
    }
});


Yasound.Views.YasoundSong = Backbone.View.extend({
    tagName: 'tr',
    events: {
        "click .add": "addSong"
    },

    initialize: function () {
        this.model.bind('change', this.render, this);
    },

    onClose: function () {
        this.model.unbind('change', this.render);
    },

    render: function () {
        var data = this.model.toJSON();
        $(this.el).html(ich.yasoundSongCellTemplate(data));
        return this;
    },

    addSong: function(e) {
        this.model.addToPlaylist();
        this.close();
    }
});

Yasound.Views.YasoundSongs = Backbone.View.extend({
    initialize: function () {
        _.bindAll(this, 'addOne', 'addAll');

        this.collection.bind('add', this.addOne, this);
        this.collection.bind('reset', this.addAll, this);
        this.views = [];
    },

    onClose: function () {
        this.collection.unbind('add', this.addOne);
        this.collection.unbind('reset', this.addAll);
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

    addOne: function (song) {
        song.setUUID(this.collection.uuid);
        var view = new Yasound.Views.YasoundSong({
            model: song
        });
        $(this.el).append(view.render().el);
        this.views.push(view);
    }
});

Yasound.Views.AddFromServer =  Backbone.View.extend({
    events: {
        "keypress #find-track-input": "onFindTrack",
        "keypress #find-album-input": "onFindAlbum",
        "keypress #find-artist-input": "onFindArtist",
        "click #find-btn": "onFind"
    },

    initialize: function() {
        _.bindAll(this, 'render');
    },

    onClose: function() {
    },

    reset: function() {
    },

    render: function(uuid) {
        $(this.el).html(ich.programmingAddFromServerTemplate());

        this.songs = new Yasound.Data.Models.YasoundSongs({}).setUUID(uuid);
        this.songsView = new Yasound.Views.YasoundSongs({
            collection: this.songs,
            el: $('#songs', this.el)
        }).render();

        this.paginationView = new Yasound.Views.Pagination({
            collection: this.songs,
            el: $('#pagination', this.el)
        });


    },

    onFindTrack: function(e) {
        if (e.keyCode != 13) {
            return;
        }
        this.onFind(e);
    },

    onFindAlbum: function(e) {
        if (e.keyCode != 13) {
            return;
        }
        this.onFind(e);
    },

    onFindArtist: function(e) {
        if (e.keyCode != 13) {
            return;
        }
        this.onFind(e);
    },

    onFind: function(e) {
        e.preventDefault();
        var name = $('#find-track-input', this.el).val();
        var album = $('#find-album-input', this.el).val();
        var artist = $('#find-artist-input', this.el).val();

        this.songsView.clear();
        this.songs.filter(name, album, artist);
    }
});


Yasound.Views.PlaylistContent =  Backbone.View.extend({

    initialize: function() {
        _.bindAll(this, 'render', 'artistsSelected', 'albumsSelected');
    },

    onClose: function() {
        this.filters.off('artistsSelected', this.artistsSelected);
        this.filters.off('albumsSelected', this.albumsSelected);
    },

    reset: function() {
    },

    render: function(uuid) {
        $(this.el).html(ich.songInstancesTemplate());

        this.songInstances = new Yasound.Data.Models.SongInstances({}).setUUID(uuid);
        this.songInstancesView = new Yasound.Views.SongInstances({
            collection: this.songInstances,
            el: $('#song-instances', this.el)
        }).render();

        this.paginationView = new Yasound.Views.Pagination({
            collection: this.songInstances,
            el: $('#pagination', this.el)
        });

        this.filters = new Yasound.Views.ProgrammingFilters({
            el: $('#programming-filters', this.el)
        }).render(uuid);

        this.filters.on('artistsSelected', this.artistsSelected);
        this.filters.on('albumsSelected', this.albumsSelected);

        this.songInstances.fetch();
    },

    artistsSelected: function(artists) {
        this.songInstancesView.clear();
        this.songInstances.filterArtists(artists);
    },

    albumsSelected: function(albums) {
        this.songInstancesView.clear();
        this.songInstances.filterAlbums(albums);
    }
});


Yasound.Views.Playlist = Backbone.View.extend({
    el: '#playlist',
    events: {
    },

    initialize: function() {
        _.bindAll(this, 'render', 'onAll', 'onImportItunes', 'onAddFromServer');
    },

    onClose: function() {
        if (this.currentView) {
            this.currentView.close();
        }
        this.toolbar.close();
    },

    reset: function() {
    },

    clearView: function() {
        if (this.currentView) {
            this.currentView.close();
        }
    },

    onAll: function() {
        this.clearView();
        this.currentView = new Yasound.Views.PlaylistContent({
            el: $('#content', this.el)
        }).render(this.uuid);
    },


    onImportItunes: function() {
        this.clearView();
        $('#content', this.el).hide().html(ich.importFromItunesTemplate()).fadeIn(200);
    },

    onAddFromServer: function() {
        this.clearView();

        this.currentView = new Yasound.Views.AddFromServer({
            el: $('#content', this.el)
        }).render(this.uuid);
    },


    render: function(uuid) {
        this.reset();
        this.uuid = uuid;
        $(this.el).html(ich.playlistTemplate());
        this.songInstances = new Yasound.Data.Models.SongInstances({}).setUUID(uuid);

        this.toolbar = new Yasound.Views.ProgrammingToolbar({
            el: $('#programming-toolbar', this.el)
        }).render();
        this.toolbar.on('tracks', this.onAll);
        this.toolbar.on('importItunes', this.onImportItunes);
        this.toolbar.on('addFromServer', this.onAddFromServer);

        this.onAll();
    }
});


/**
 * Programming menu
 */
Yasound.Views.ProgrammingToolbar = Backbone.View.extend({
    el: '#programming-toolbar',
    events: {
        'click #all': 'all',
        'click #import-itunes': 'importItunes',
        'click #add-from-server': 'addFromServer'
    },
    render: function() {
        $(this.el).html(ich.programmingToolbarTemplate());
        return this;
    },
    all: function(e) {
        e.preventDefault();

        $('#all').addClass('active');
        $('#import-itunes').removeClass('active');
        $('#add-from-server').removeClass('active');

        this.trigger('tracks');
    },
    importItunes: function(e) {
        e.preventDefault();

        $('#all').removeClass('active');
        $('#import-itunes').addClass('active');
        $('#add-from-server').removeClass('active');

        this.trigger('importItunes');
    },
    addFromServer: function(e) {
        e.preventDefault();

        $('#all').removeClass('active');
        $('#import-itunes').removeClass('active');
        $('#add-from-server').addClass('active');

        this.trigger('addFromServer');

    }
});

/**
 * Programming filters
 */
Yasound.Views.ProgrammingFilters = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this, 'render', 'artistsSelected', 'albumsSelected');
    },
    onClose: function () {
        this.artistsView.close();
        this.albumsView.close();
        this.off('artistsSelected', this.artistsSelected);
        this.off('albumsSelected', this.albumsSelected);
    },
    render: function(uuid) {
        $(this.el).html(ich.programmingFiltersTemplate());

        this.artists = new Yasound.Data.Models.ProgrammingArtists({}).setUUID(uuid);
        this.artistsView = new Yasound.Views.ProgrammingFilterArtists({
            collection:this.artists,
            el: $('#artist-select', this.el)
        });

        this.albums = new Yasound.Data.Models.ProgrammingAlbums({}).setUUID(uuid);
        this.albumsView = new Yasound.Views.ProgrammingFilterAlbums({
            collection:this.albums,
            el: $('#album-select', this.el)
        });


        this.artistsView.on('artistsSelected', this.artistsSelected);
        this.artists.fetch();

        this.albumsView.on('albumsSelected', this.albumsSelected);
        this.albums.fetch();

        return this;
    },
    artistsSelected: function(artists) {
        this.trigger('artistsSelected', artists);
        this.albums.filterArtists(artists);
    },
    albumsSelected: function(albums) {
        this.trigger('albumsSelected', albums);
    }

});

Yasound.Views.ProgrammingFilterArtists = Backbone.View.extend({
    events: {
        'change': 'selected'
    },
    initialize: function () {
        _.bindAll(this, 'addOne', 'addAll', 'selected');

        this.collection.bind('add', this.addOne, this);
        this.collection.bind('reset', this.addAll, this);
        this.views = [];
        $(this.el).chosen();
    },

    onClose: function () {
        this.collection.unbind('add', this.addOne);
        this.collection.unbind('reset', this.addAll);
    },

    addAll: function () {
        $(this.el).hide();
        this.collection.each(this.addOne);
        $(this.el).trigger("liszt:updated");
    },

    clear: function () {
        _.map(this.views, function (view) {
            view.close();
        });
        this.views = [];
    },

    addOne: function (artist) {
        var view = new Yasound.Views.ProgrammingFilterArtist({
            model: artist
        });
        $(this.el).append(view.render().el);
        this.views.push(view);
    },
    selected: function(e) {
        var artists = $(this.el).val();
        this.trigger('artistsSelected', artists);
    }
});

Yasound.Views.ProgrammingFilterArtist = Backbone.View.extend({
    tagName: 'option',

    initialize: function () {
        this.model.bind('change', this.render, this);
    },

    onClose: function () {
        this.model.unbind('change', this.render);
    },

    render: function () {
        var name = this.model.get('metadata__artist_name');
        $(this.el).html(name);
        return this;
    }
});

Yasound.Views.ProgrammingFilterAlbums = Backbone.View.extend({
    events: {
        'change': 'selected'
    },
    initialize: function () {
        _.bindAll(this, 'addOne', 'addAll', 'selected');

        this.collection.bind('add', this.addOne, this);
        this.collection.bind('reset', this.addAll, this);
        this.views = [];
        $(this.el).chosen();
    },

    onClose: function () {
        this.collection.unbind('add', this.addOne);
        this.collection.unbind('reset', this.addAll);
    },

    addAll: function () {
        this.clear();
        $(this.el).hide();
        this.collection.each(this.addOne);
        $(this.el).trigger("liszt:updated");
    },

    clear: function () {
        _.map(this.views, function (view) {
            view.close();
        });
        this.views = [];
    },

    addOne: function (album) {
        var view = new Yasound.Views.ProgrammingFilterAlbum({
            model: album
        });
        $(this.el).append(view.render().el);
        this.views.push(view);
    },
    selected: function(e) {
        var albums = $(this.el).val();
        this.trigger('albumsSelected', albums);
    }
});

Yasound.Views.ProgrammingFilterAlbum = Backbone.View.extend({
    tagName: 'option',

    initialize: function () {
        this.model.bind('change', this.render, this);
    },

    onClose: function () {
        this.model.unbind('change', this.render);
    },

    render: function () {
        var name = this.model.get('metadata__album_name');
        $(this.el).html(name);
        return this;
    }
});


/**
 * Programming page
 */
Yasound.Views.ProgrammingPage = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this, 'render');
    },

    onClose: function() {
    },

    reset: function() {
    },

    render: function(uuid) {
        this.reset();
        $(this.el).html(ich.programmingPageTemplate());

        this.playlistView = new Yasound.Views.Playlist({}).render(uuid);

        return this;
    }
});
