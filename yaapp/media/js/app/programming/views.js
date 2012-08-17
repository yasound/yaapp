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

        return this;
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
    events: {
        "click #remove-all": "onRemoveAll"
    },

    initialize: function() {
        _.bindAll(this, 'render', 'artistsSelected', 'albumsSelected');
    },

    onClose: function() {
        this.filters.off('artistsSelected', this.artistsSelected);
        this.filters.off('albumsSelected', this.albumsSelected);

        this.songInstancesView.close();
        this.paginationView.close();
        this.filters.close();
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

        return this;
    },

    artistsSelected: function(artists) {
        this.songInstancesView.clear();
        this.songInstances.filterArtists(artists);
    },

    albumsSelected: function(albums) {
        this.songInstancesView.clear();
        this.songInstances.filterAlbums(albums);
    },

    onRemoveAll: function(e) {
        e.preventDefault();
        var that = this;
        $('#modal-remove-all', this.el).modal('show');
        $('#modal-remove-all .btn-primary', this.el).on('click', function () {
            $('#modal-remove-all', this.el).modal('hide');
            that.songInstances.removeAll(function() {
                that.songInstancesView.clear();
                that.songInstances.goTo(0);
            });
        });
    }

});


Yasound.Views.UploadCell = Backbone.View.extend({
    tagName: 'tr',
    events: {
        "click .start": "onStart",
        "click .stop": "onStop",
        "click .remove": "onRemove"
    },

    initialize: function() {
        _.bindAll(this, 'render', 'start', 'onProgress', 'onFinished', 'onFailed');
        this.jqXHR = undefined;
    },

    onClose: function() {
    },

    reset: function() {
    },

    render: function(data, uuid) {
        $(this.el).html(ich.programmingUploadCellTemplate(data.files[0]));
        $('#stop', this.el).attr('disabled', true);

        this.data = data;
        this.data.formData = {
            'response_format': 'json',
            data: JSON.stringify({
                'radio_uuid': uuid
            })
        };

        this.data.onProgress = this.onProgress;
        this.data.onFinished = this.onFinished;
        this.data.onFailed = this.onFailed;
        return this;
    },

    start: function() {
        this.jqXHR = this.data.submit();
    },

    onStart: function(e) {
        e.preventDefault();
        this.start();

        $('#stop', this.el).attr('disabled', false);
    },

    onStop: function (e) {
        if (this.jqHXR) {
            this.jqHXR.abort();
            this.jqHXR = undefined;
            $('#stop', this.el).attr('disabled', true);
        }
    },

    onRemove: function (e) {
        this.onStop();
        this.remove();
    },

    onFinished: function(e, data) {
        this.remove();
    },

    onFailed: function(e, data) {

    },

    onProgress: function(e, data) {
        var progress = parseInt(data.loaded / data.total * 100, 10);
        $progress = $('#progress .bar', this.el);
        $progress.css('width', progress + '%');
    }
});

Yasound.Views.AddFromDesktop =  Backbone.View.extend({
    sticky: true,
    stickyKey: function() {
        return 'add-from-desktop-' + this.uuid;
    },

    events: {
        "click #start-all-btn": "onStartAll"
    },

    initialize: function() {
        _.bindAll(this, 'render');
        this.views = [];
    },

    onClose: function() {
    },

    reset: function() {
    },

    clear: function () {
        _.map(this.views, function (view) {
            view.close();
        });
        this.views = [];
    },

    render: function(uuid, disableTemplate) {
        if (!disableTemplate) {
            $(this.el).html(ich.programmingUploadTemplate());
        }
        this.uuid = uuid;

        var $table = $('#upload-table tbody', this.el);
        var that = this;
        $('#file-upload', this.el).fileupload({
            dataType: 'json',
            add: function (e, data) {
                var view = new Yasound.Views.UploadCell({});
                $('#upload-table', that.el).append(view.render(data, uuid).el);
                that.views.push(view);
            },
            progressall: function (e, data) {
            },
            progress: function (e, data) {
                if (data.onProgress) {
                    data.onProgress(e, data);
                }
            },
            done: function (e, data) {
                if (data.onFinished) {
                    data.onFinished(e, data);
                }
            },
            fail: function (e, data) {
                if (data.onFailed) {
                    data.onFailed(e, data);
                }
            }
        });

        this.delegateEvents();
        _.map(this.views, function (view) {
            view.delegateEvents();
        });

        return this;
    },

    onStartAll: function (e) {
        e.preventDefault();
        _.each(this.views, function(view) {
            view.start();
        });
    }
});


Yasound.Views.ImportFromItunes =  Backbone.View.extend({
    initialize: function() {
        _.bindAll(this, 'render');
    },

    onClose: function() {
    },

    reset: function() {
    },

    clear: function () {
    },

    render: function(uuid) {
        $(this.el).html(ich.importFromItunesTemplate());
        return this;
    }
});

Yasound.Views.Playlist = Backbone.View.extend({
    el: '#playlist',
    events: {
    },

    initialize: function() {
        _.bindAll(this, 'render', 'onAll',  'onClose', 'clearView', 'onImportItunes', 'onAddFromServer', 'onAddFromDesktop');
    },

    onClose: function() {
        this.clearView();
        this.toolbar.close();
    },

    reset: function() {
    },

    clearView: function() {
        if (this.currentView) {
            this.currentView.close();
            $(this.el).append("<div id='content'></div>");
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
        this.currentView = new Yasound.Views.ImportFromItunes({
            el: $('#content', this.el)
        }).render(this.uuid);
    },

    onAddFromServer: function() {
        this.clearView();

        this.currentView = new Yasound.Views.AddFromServer({
            el: $('#content', this.el)
        }).render(this.uuid);
    },

    onAddFromDesktop: function() {
        this.clearView();

        var savedView = Yasound.Utils.getStickyView('add-from-desktop-' + this.uuid);
        if (!savedView) {
            this.currentView = new Yasound.Views.AddFromDesktop({
                el: $('#content', this.el)
            }).render(this.uuid);
        } else {
            this.currentView = savedView;
            $(this.el).append(this.currentView.render(this.uuid, true).el);
        }
    },

    render: function(uuid) {
        this.reset();
        this.uuid = uuid;
        $(this.el).html(ich.playlistTemplate());

        this.toolbar = new Yasound.Views.ProgrammingToolbar({
            el: $('#programming-toolbar', this.el)
        }).render();
        this.toolbar.on('tracks', this.onAll);
        this.toolbar.on('importItunes', this.onImportItunes);
        this.toolbar.on('addFromServer', this.onAddFromServer);
        this.toolbar.on('addFromDesktop', this.onAddFromDesktop);

        this.onAll();

        return this;
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
        'click #add-from-server': 'addFromServer',
        'click #add-from-desktop': 'addFromDesktop'
    },

    initialize: function() {
        _.bindAll(this, 'render', 'selectMenu');
    },

    render: function() {
        $(this.el).html(ich.programmingToolbarTemplate());
        return this;
    },

    selectMenu: function(menu) {
        $('#all', this.el).removeClass('active');
        $('#import-itunes', this.el).removeClass('active');
        $('#add-from-server', this.el).removeClass('active');
        $('#add-from-desktop', this.el).removeClass('active');

        $(menu).addClass('active');
    },

    all: function(e) {
        e.preventDefault();
        this.selectMenu('#all');
        this.trigger('tracks');
    },
    importItunes: function(e) {
        e.preventDefault();
        this.selectMenu('#import-itunes');
        this.trigger('importItunes');
    },
    addFromServer: function(e) {
        e.preventDefault();
        this.selectMenu('#add-from-server');
        this.trigger('addFromServer');
    },
    addFromDesktop: function(e) {
        e.preventDefault();
        this.selectMenu('#add-from-desktop');
        this.trigger('addFromDesktop');
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
        _.bindAll(this, 'render', 'onClose');
    },

    onClose: function() {
        this.playlistView.close();
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
