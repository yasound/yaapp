/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Views');

Yasound.Views.SongInstance = Backbone.View.extend({
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
        $(this.el).hide().html(ich.songInstanceCellTemplate(data)).fadeIn(200);
        return this;
    }
});

Yasound.Views.SongInstances = Backbone.View.extend({
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
    }
});

/**
 * Programming page
 */
Yasound.Views.ProgrammingPage = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this, 'render', 'onAll', 'onImportItunes', 'artistsSelected', 'albumsSelected');
    },

    onClose: function() {
        if (this.currentView) {
            this.currentView.close();
        }
        this.toolbar.close();
        this.filters.off('artistsSelected', this.artistsSelected);
        this.filters.close();
    },

    reset: function() {
    },
    
    onAll: function() {
        if (this.currentView) {
            this.currentView.close();
        }
        $('#content', this.el).html(ich.songInstancesTemplate());
        this.currentView = new Yasound.Views.SongInstances({
            collection: this.songInstances,
            el: $('#song-instances', this.el)
        }).render();
        $(this.filters.el).show();
        this.filters.on('artistsSelected', this.artistsSelected);
        this.filters.on('albumsSelected', this.albumsSelected);
        
        this.songInstances.fetch();
    },
    onImportItunes: function() {
        if (this.currentView) {
            this.currentView.close();
        }
        $(this.filters.el).hide();
        this.filters.off('artistsSelected', this.artistsSelected);
        this.filters.off('albumsSelected', this.albumsSelected);
        $('#content', this.el).hide().html(ich.importFromItunesTemplate()).fadeIn(200);
    },
    
    render: function() {
        this.reset();
        $(this.el).html(ich.programmingPageTemplate());
        
        this.songInstances = new Yasound.Data.Models.SongInstances({});
        
        $('#content', this.el).hide().html(ich.songInstancesTemplate()).fadeIn(200);
        this.currentView = new Yasound.Views.SongInstances({
            collection: this.songInstances,
            el: $('#song-instances', this.el)
        });
        
        this.paginationView = new Yasound.Views.Pagination({
            collection: this.songInstances,
            el: $('#pagination', this.el)
        });
        
        this.toolbar = new Yasound.Views.ProgrammingToolbar({
            el: $('#programming-toolbar', this.el)
        }).render();
        this.toolbar.on('tracks', this.onAll);
        this.toolbar.on('importItunes', this.onImportItunes);

        this.filters = new Yasound.Views.ProgrammingFilters({
            el: $('#programming-filters', this.el)
        }).render();

        this.filters.on('artistsSelected', this.artistsSelected);
        this.filters.on('albumsSelected', this.albumsSelected);
        
        this.songInstances.fetch();
        
        return this;
    },
    artistsSelected: function(artists) {
        this.currentView.clear();
        this.songInstances.filterArtists(artists);
    },
    albumsSelected: function(albums) {
        this.currentView.clear();
        this.songInstances.filterAlbums(albums);
    }
});

/**
 * Programming menu
 */
Yasound.Views.ProgrammingToolbar = Backbone.View.extend({
    el: '#programming-toolbar',
    events: {
        'click #all': 'all',
        'click #import-itunes': 'importItunes'
    },
    render: function() {
        $(this.el).html(ich.programmingToolbarTemplate());
        return this;
    },
    all: function(e) {
        e.preventDefault();
        this.trigger('tracks');
    },
    importItunes: function(e) {
        e.preventDefault();
        this.trigger('importItunes');
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
    render: function() {
        $(this.el).html(ich.programmingFiltersTemplate());

        this.artists = new Yasound.Data.Models.ProgrammingArtists({});
        this.artistsView = new Yasound.Views.ProgrammingFilterArtists({
            collection:this.artists,
            el: $('#artist-select', this.el)
        });

        this.albums = new Yasound.Data.Models.ProgrammingAlbums({});
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
        var name = this.model.get('artist_name');
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
        var name = this.model.get('album_name');
        $(this.el).html(name);
        return this;
    }
});

