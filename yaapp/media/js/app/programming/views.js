"use strict";
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
        _.bindAll(this, 'render', 'onAll', 'onImportItunes');
    },

    onClose: function() {
        this.songInstancesView.close();
        this.toolbar.close();
    },

    reset: function() {
    },
    
    onAll: function() {
        if (this.currentView) {
            this.currentView.close();
        }
        $('#content', this.el).hide().html(ich.songInstancesTemplate()).fadeIn(200);
        this.currentView = new Yasound.Views.SongInstances({
            collection: this.songInstances,
            el: $('#song-instances', this.el)
        });
        this.songInstances.fetch();
    },
    onImportItunes: function() {
        if (this.currentView) {
            this.currentView.close();
        }
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
        
        
        this.toolbar = new Yasound.Views.ProgrammingToolbar({
            el: $('#programming-toolbar', this.el)
        }).render();
        
        this.toolbar.on('tracks', this.onAll);
        this.toolbar.on('importItunes', this.onImportItunes);
        
        this.songInstances.fetch();
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
