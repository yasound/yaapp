/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Views');

//----------------------------------------------------------
// View items
//----------------------------------------------------------

Yasound.Views.SongInstance = Backbone.View.extend({
    tagName: 'tr',
    events: {
        "click .preview": "onPreview",
        "click .stop-preview": "onStopPreview",
        "click .remove": "onRemove",
        "click .artist": "onArtist",
        "click .album": "onAlbum"
    },

    initialize: function () {
        _.bindAll(this, 'onPreviewFinished');
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
        this.model.destroy({wait: true});
    },

    onArtist: function (e) {
        e.preventDefault();
        $('#artist-select').val(this.model.get('metadata__artist_name'));
        $('#artist-select').trigger("liszt:updated");
        $('#artist-select').trigger("change");
        $('html, body').scrollTop(0);

    },

    onAlbum: function (e) {
        e.preventDefault();
        $('#album-select').val(this.model.get('metadata__album_name'));
        $('#album-select').trigger("liszt:updated");
        $('#album-select').trigger("change");
        $('html, body').scrollTop(0);
    },

    onPreview: function (e) {
        e.preventDefault();
        var url = '/api/v1/song/' + this.model.get('id') + '/download_preview/';
        $('.preview', this.el).hide();
        $('.stop-preview', this.el).show();
        Yasound.App.previewPlayer.play(url, this.onPreviewFinished);
    },

    onStopPreview: function (e) {
        e.preventDefault();
        Yasound.App.previewPlayer.stop();
        $('.stop-preview', this.el).hide();
        $('.preview', this.el).show();
    },

    onPreviewFinished: function () {
        $('.stop-preview', this.el).hide();
        $('.preview', this.el).show();
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
        this.clear();
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
        "click .add": "addSong",
        "click .preview": "onPreview",
        "click .stop-preview": "onStopPreview"
    },

    initialize: function () {
        _.bindAll(this, 'onPreviewFinished');
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
    },

    onPreview: function (e) {
        e.preventDefault();
        $('.stop-preview', this.el).show();
        $('.preview', this.el).hide();

        var url = '/yaref/download_preview/'+ this.model.get('id') + '/';
        Yasound.App.previewPlayer.play(url, this.onPreviewFinished);
    },

    onStopPreview: function (e) {
        e.preventDefault();
        Yasound.App.previewPlayer.stop();
        $('.stop-preview', this.el).hide();
        $('.preview', this.el).show();
    },

    onPreviewFinished: function () {
        $('.stop-preview', this.el).hide();
        $('.preview', this.el).show();
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
        "click #find-btn": "onFind",
        "keypress #find-fuzzy-input": "onFindFuzzyInput",
        "click #find-fuzzy-btn": "onFindFuzzy",
        "click #advanced": "onAdvanced"
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

    onFindFuzzyInput: function(e) {
        if (e.keyCode != 13) {
            return;
        }
        this.onFindFuzzy(e);
    },

    onFind: function(e) {
        e.preventDefault();
        var name = $('#find-track-input', this.el).val();
        var album = $('#find-album-input', this.el).val();
        var artist = $('#find-artist-input', this.el).val();

        this.songsView.clear();
        this.songs.filter(name, album, artist);
    },

    onFindFuzzy: function(e) {
        e.preventDefault();
        var criteria = $('#find-fuzzy-input', this.el).val();

        this.songsView.clear();
        this.songs.findFuzzy(criteria);
    },

    onAdvanced: function (e) {
        $('#advanced-search', this.el).toggle();
    }

});


Yasound.Views.PlaylistContent =  Backbone.View.extend({
    events: {
        "click #remove-all": "onRemoveAll",
        "click #export-deezer": "onExportDeezer",
        "click #export-deezer-all": "onExportDeezerAll"
    },

    initialize: function() {
        _.bindAll(this, 'render', 'artistsSelected', 'albumsSelected', 'exportAllSongs');
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
        this.uuid = uuid;
        $(this.el).html(ich.songInstancesTemplate());
        this.songInstances = new Yasound.Data.Models.SongInstances({}).setUUID(uuid);
        this.songInstancesView = new Yasound.Views.SongInstances({
            collection: this.songInstances,
            el: $('#song-instances', this.el)
        }).render();

        this.paginationView = new Yasound.Views.Pagination({
            collection: this.songInstances,
            el: $('#pagination', this.el),
            type: 'prevnext'
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
        $('#modal-remove-all .btn-primary', this.el).one('click', function () {
            $('#modal-remove-all', this.el).modal('hide');
            that.songInstances.removeAll(function() {
                that.songInstancesView.clear();
                that.songInstances.goTo(0);
            });
        });
    },


    exportAllSongs: function (e) {
        var that = this;
        var songInstances = new Yasound.Data.Models.SongInstances({}).setUUID(that.uuid);
        $('#playlist-actions #progress').show();

        var total = 1;
        var current = 1;
        songInstances.fetch({
            success: function () {
                total += songInstances.length;
                var t = 0;
                songInstances.each(function (model) {
                    t = t+1;
                    current += 1;
                    setTimeout(function() {
                        $.publish('/radio/import/add_from_server', model);
                        var percentage = (current*100) / total;
                        var progress = parseInt(percentage, 10);
                        $progress = $('#playlist-actions #progress .bar');
                        $progress.css('width', progress + '%');
                        if (progress > 99) {
                            $('#playlist-actions #progress').hide();
                        }
                    }, 1000*t);


                });
                var info = songInstances.info();
                var totalPages = info.totalPages;
                var i;
                var t = 0;
                if (totalPages > 1 ) {
                    $('#playlist-actions #progress').show();
                }
                for (i = 1; i <= totalPages; i++) {
                    songInstances.page = i;
                    songInstances.fetch({
                        success: function () {
                            total += songInstances.length;

                            songInstances.each(function (model) {
                                t = t+1;
                                setTimeout(function() {
                                    $.publish('/radio/import/add_from_server', model);

                                    current += 1;
                                    var percentage = (current*100) / total;
                                    var progress = parseInt(percentage, 10);
                                    $progress = $('#playlist-actions #progress .bar');
                                    $progress.css('width', progress + '%');
                                    if (progress > 99) {
                                        $('#playlist-actions #progress').hide();
                                    }
                                }, t*1000);
                            });
                        }
                    });
                }
            }
        });
    },

    onExportDeezerAll: function (e) {
        e.preventDefault();
        var that = this;
        $('#playlist-actions #progress').show();
        $('#modal-export-deezer').modal('show');
        $('#modal-export-deezer .btn-primary').one('click', function () {
            val = $('#modal-export-deezer input').val();
            if (val.length !== 0) {
                var startFunction = that.exportAllSongs;
                var endFunction = function () {
                };
                Yasound.App.deezerExportOperations.reset(val, that.songInstances.length, startFunction, endFunction);
            }
            $('#modal-export-deezer input').val('');
            $('#modal-export-deezer').modal('hide');
        });
    },

    onExportDeezer: function (e) {
        e.preventDefault();
        var that = this;
        var total = that.songInstancesView.views.length;
        var i = 0;

        $('html, body').animate({scrollTop: 0}, 400);
        $('#modal-export-deezer').modal('show');
        $('#modal-export-deezer .btn-primary').one('click', function () {
            val = $('#modal-export-deezer input').val();
            if (val.length !== 0) {
                var startFunction = function () {
                    t = 0;
                    _.each(that.songInstancesView.views, function(view) {
                        t = t+1;
                        setTimeout(function() {
                            $.publish('/radio/import/add_from_server', view.model);
                            i = i + 1;
                            var percentage = (i*100) / total;
                            var progress = parseInt(percentage, 10);
                            $progress = $('#playlist-actions #progress .bar');
                            $progress.css('width', progress + '%');


                        }, t*1000);
                    });
                };
                var endFunction = function () {
                    var found = Yasound.App.deezerExportOperations.found;
                    var notFound = Yasound.App.deezerExportOperations.notFound;
                    var body = gettext('Export results:') + '<br/>';
                    body += found + ' ' + gettext('tracks founds') + '<br/>' + notFound + ' ' + gettext('tracks not found');
                    Yasound.Utils.dialog(gettext('Results'),  body);
                    $('#playlist-actions #progress').hide();
                };

                Yasound.App.deezerExportOperations.reset(val, that.songInstances.length, startFunction, endFunction);
            }

            $('#modal-export-deezer input').val('');
            $('#modal-export-deezer').modal('hide');
        });


    }
});



Yasound.Views.UploadCell = Backbone.View.extend({
    tagName: 'tr',
    events: {
        "click #start": "onStart",
        "click #stop": "onStop",
        "click #remove": "onRemove"
    },

    initialize: function() {
        _.bindAll(this, 'render', 'start', 'stop', 'onStart', 'onStop', 'onRemove', 'onProgress', 'onFinished', 'onFailed');
        this.job = undefined;
    },

    onClose: function() {
        this.stop();
    },

    reset: function() {
    },

    render: function(data, uuid) {
        $(this.el).html(ich.programmingUploadCellTemplate(data.files[0]));
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
        this.job = this.data.submit();
        $.publish('/programming/upload_started');
        $('#start', this.el).hide();
        $('#stop', this.el).show();
    },

    stop: function () {
        if (this.job) {
            this.job.abort();
            this.job = undefined;

            $.publish('/programming/upload_stopped');

            $('#start', this.el).show();
            $('#stop', this.el).hide();
        }
    },

    onStart: function(e) {
        e.preventDefault();
        this.start();
    },

    onStop: function (e) {
        e.preventDefault();
        this.stop();
    },

    onRemove: function (e) {
        this.stop();
        this.trigger('remove', this);
        this.remove();
    },

    onFinished: function(e, data) {
        $.publish('/programming/upload_finished');
        this.trigger('remove', this);
        this.remove();
    },

    onFailed: function(e, data) {
        $.publish('/programming/upload_failed');
    },

    onProgress: function(e, data) {
        var percentage = (data.loaded*100) / data.total;
        var progress = parseInt(percentage, 10);
        $progress = $('#progress .bar', this.el);
        $progress.css('width', progress + '%');
    }
});

//----------------------------------------------------------
// Import views
//----------------------------------------------------------

Yasound.Views.AddFromDesktop =  Backbone.View.extend({
    sticky: true,
    stickyKey: function() {
        return 'add-from-desktop-' + this.uuid;
    },

    events: {
        "click #start-all-btn": "onStartAll",
        "click #stop-all-btn": "onStopAll",
        "click #remove-all-btn": "onRemoveAll"
    },

    initialize: function() {
        _.bindAll(this, 'render', 'onRemoveView');
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
                var warningTitle = gettext('Warning');
                var warningContent = gettext('You must own the copyright or have the necessary rights for any content you upload on Yasound');
                Yasound.Utils.dialog({
                    title: warningTitle,
                    content: warningContent,
                    closeButton: gettext('I agree'),
                    cancelButton: gettext('Cancel'),
                    onClose: function () {
                        var view = new Yasound.Views.UploadCell({});
                        view.on('remove', that.onRemoveView);
                        $('#upload-table', that.el).append(view.render(data, uuid).el);
                        that.views.push(view);

                        $('#start-all-btn', that.el).hide();
                        $('#stop-all-btn', that.el).show();
                        $('#remove-all-btn', that.el).show();
                        view.start();
                    }
                });

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
        $('#start-all-btn', this.el).hide();
        $('#stop-all-btn', this.el).show();
        $('#remove-all-btn', this.el).show();

        _.each(this.views, function(view) {
            view.start();
        });
    },

    onStopAll: function (e) {
        e.preventDefault();
        $('#start-all-btn', this.el).show();
        $('#stop-all-btn', this.el).hide();
        $('#remove-all-btn', this.el).show();

        _.each(this.views, function(view) {
            view.stop();
        });
    },

    onRemoveAll: function (e) {
        e.preventDefault();
        $('#start-all-btn', this.el).hide();
        $('#stop-all-btn', this.el).hide();
        $('#remove-all-btn', this.el).hide();
        this.clear();
    },

    onRemoveView: function (view) {
        this.views = _.without(this.views, view);
        view.off('remove', this.onRemoveView);
    }
});



Yasound.Views.ImportFromItunes =  Backbone.View.extend({
    events: {
        "submit #programming-import-itunes": "onSubmit"
    },

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
        $(this.el).html(ich.importFromItunesTemplate({uuid:uuid}));
        return this;
    },

    onSubmit: function (e) {
        e.preventDefault();
        var form = $('#programming-import-itunes', this.el);

        var successMessage = gettext('iTunes import analyzis started');
        var errorMessage = gettext('Error while analyzing iTunes import data');

        Yasound.Utils.submitForm({
            form: form,
            successMessage: successMessage,
            errorMessage: errorMessage,
            success: function (e) {
                $('textarea', form).val('');
            }
        });
    }
});



Yasound.Views.Playlist = Backbone.View.extend({
    el: '#playlist',
    events: {
    },

    initialize: function() {
        _.bindAll(this,
            'render',
            'onAll',
            'onClose',
            'clearView',
            'onImportItunes',
            'onImportDeezer',
            'onAddFromServer',
            'onAddFromDesktop',
            'onJingles');
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

    onImportDeezer: function() {
        this.clearView();
        this.currentView = new Yasound.Views.ImportFromDeezer({
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

    onJingles: function() {
        this.clearView();

        this.currentView = new Yasound.Views.JinglesPage({
            el: $('#content', this.el)
        }).render(this.uuid);
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
        this.toolbar.on('importDeezer', this.onImportDeezer);
        this.toolbar.on('addFromServer', this.onAddFromServer);
        this.toolbar.on('addFromDesktop', this.onAddFromDesktop);
        this.toolbar.on('jingles', this.onJingles);

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
        'click #import-deezer': 'importDeezer',
        'click #jingles': 'jingles',
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
        $('#import-deezer', this.el).removeClass('active');
        $('#import-itunes', this.el).removeClass('active');
        $('#add-from-server', this.el).removeClass('active');
        $('#add-from-desktop', this.el).removeClass('active');
        $('#jingles', this.el).removeClass('active');

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
    importDeezer: function(e) {
        e.preventDefault();
        this.selectMenu('#import-deezer');
        this.trigger('importDeezer');
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
    },

    jingles: function(e) {
        e.preventDefault();
        this.selectMenu('#jingles');
        this.trigger('jingles');
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

Yasound.Views.ProgrammingStatusDetail = Backbone.View.extend({
    tagName: 'tr',
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
        $(this.el).html(ich.programmingStatusDetailsCellTemplate(data));
        return this;
    }
});

Yasound.Views.ProgrammingStatusDetails = Backbone.View.extend({
    collection: new Yasound.Data.Models.ProgrammingStatusDetails({}),

    initialize: function () {
        _.bindAll(this, 'render', 'addOne', 'addAll', 'onDestroy');

        this.collection.bind('add', this.addOne, this);
        this.collection.bind('reset', this.addAll, this);
        this.collection.bind('destroy', this.onDestroy, this);
        this.views = [];
    },

    render: function(id) {
        this.collection.setID(id);
        this.collection.fetch();
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

    addOne: function (detail) {
        var currentId = detail.id;

        var found = _.find(this.views, function (view) {
            if (view.model.id == detail.id) {
                return true;
            }
        });
        if (found) {
            // do not insert duplicated content
            return;
        }

        var view = new Yasound.Views.ProgrammingStatusDetail({
            model: detail
        });
        $(this.el).append(view.render().el);
        this.views.push(view);
    },

    onDestroy: function(model) {
        this.clear();
        this.collection.fetch();
    }
});

Yasound.Views.ProgrammingStatus = Backbone.View.extend({
    tagName: 'tr',
    events: {
        "click .open": "onDetails",
        "click .delete": "onRemove"
    },

    initialize: function () {
        this.model.bind('change', this.render, this);
    },

    onClose: function () {
        this.model.unbind('change', this.render);
    },

    render: function () {
        var data = this.model.toJSON();
        $(this.el).html(ich.programmingStatusCellTemplate(data));
        return this;
    },

    onRemove: function (e) {
        e.preventDefault();
        var that = this;
        $('#modal-remove-status').modal('show');
        $('#modal-remove-status .btn-primary').one('click', function () {
            $('#modal-remove-status').modal('hide');
            that.model.destroy();
        });
    },

    onDetails: function (e) {
        e.preventDefault();
        var view = new Yasound.Views.ProgrammingStatusDetails({
            tagName: 'tbody'
        }).render(this.model.id);

        $('#status-details-list').append(view.el);

        $('#modal-status-details').modal('show');
        $('#modal-status-details').one('hidden', function () {
            view.close();
        });
    }
});

Yasound.Views.StatusList = Backbone.View.extend({
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

    addOne: function (status) {
        var currentId = status.id;

        var found = _.find(this.views, function (view) {
            if (view.model.id == status.id) {
                return true;
            }
        });
        if (found) {
            // do not insert duplicated content
            return;
        }

        var view = new Yasound.Views.ProgrammingStatus({
            model: status
        });
        $(this.el).append(view.render().el);
        this.views.push(view);
    },

    onDestroy: function(model) {
        this.clear();
        this.collection.fetch();
    }
});


Yasound.Views.Status = Backbone.View.extend({
    el: '#status',
    events: {

    },

    initialize: function () {
    },

    onClose: function () {
    },

    render: function (uuid) {
        this.uuid = uuid;
        $(this.el).html(ich.programmingStatusPageTemplate());

        this.statusList = new Yasound.Data.Models.ProgrammingStatusList({}).setUUID(uuid);
        this.statusView = new Yasound.Views.StatusList({
            collection: this.statusList,
            el: $('#status-list', this.el)
        }).render();

        this.paginationView = new Yasound.Views.Pagination({
            collection: this.statusList,
            el: $('#pagination', this.el)
        });

        this.statusList.fetch();

        return this;
    }
});


Yasound.Views.RadioInline = Backbone.View.extend({

    events: {
        'click .radio-name': 'onRadio',
        'click .listen-btn': 'onListen',
        'click .edit-settings-btn': 'onSettings'
    },

    initialize: function () {
        this.model.bind('change', this.render, this);
    },

    onClose: function () {
        this.model.unbind('change', this.render);
    },

    render: function () {
        var data = this.model.toJSON();
        $(this.el).html(ich.radioInlineTemplate(data));
        return this;
    },

    onRadio: function (e) {
        e.preventDefault();
        var uuid = this.model.get('uuid');
        Yasound.App.Router.navigate("radio/" + uuid + '/', {
            trigger: true
        });
    },

    onSettings: function (e) {
        e.preventDefault();
        var uuid = this.model.get('uuid');
        Yasound.App.Router.navigate("radio/" + uuid + '/edit/', {
            trigger: true
        });
    },

    onListen: function (e) {
        e.preventDefault();
        var uuid = this.model.get('uuid');
        Yasound.App.Router.navigate("radio/" + uuid, {
            trigger: true
        });
    }
});

/**
 * Programming page
 */
Yasound.Views.ProgrammingPage = Backbone.View.extend({
    events: {
        "click #status-btn": "onStatus"
    },

    initialize: function() {
        _.bindAll(this, 'render', 'onClose');
        this.radio = new Yasound.Data.Models.Radio();
    },

    onClose: function() {
        this.playlistView.close();
        this.radioView.close();
    },

    reset: function() {
    },

    render: function(uuid) {
        this.reset();
        this.uuid = uuid;
        $(this.el).html(ich.programmingPageTemplate());

        this.radio.set({
                'slug': uuid,
                'id': 0
            }, {
                silent: true
        });

        this.radioView = new Yasound.Views.RadioInline({
            model: this.radio,
            el: '#radio'
        });
        this.radio.fetch();

        this.playlistView = new Yasound.Views.Playlist({}).render(uuid);
        return this;
    },

    onProgramming: function (e) {
        e.preventDefault();
        $('#status', this.el).hide();
        $('#playlist', this.el).show();

        $('#status-btn', this.el).removeClass('active');
        $('#programming-btn', this.el).addClass('active');
    },

    onStatus: function (e) {
        e.preventDefault();
        $('#playlist', this.el).hide().parent();
        $('#status', this.el).show().parent();

        $('#programming-btn', this.el).removeClass('active');
        $('#status-btn', this.el).addClass('active');

        if (!this.statusView) {
            this.statusView = new Yasound.Views.Status({});
        }
        this.statusView.render(this.uuid);
    }

});
