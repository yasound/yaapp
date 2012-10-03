/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Views');

Yasound.Views.TopResults = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this, 'addOne', 'addAll');

        this.collection.bind('add', this.addOne, this);
        this.collection.bind('reset', this.addAll, this);
        this.collection.bind('beforeFetch', this.beforeFetch, this);
        this.views = [];
        this.index = 1;
    },
    onClose: function() {
        this.collection.unbind('beforeFetch', this.beforeFetch);
        this.collection.unbind('add', this.addOne);
        this.collection.unbind('reset', this.addAll);
    },

    beforeFetch: function() {
        if (this.loadingMask) {
            $(this.el).append(this.loadingMask);
        }
    },
    addAll: function() {
        var mask = $('.loading-mask', this.el);
        if (!this.loadingMask) {
            this.loadingMask = mask;
        }
        mask.hide();

        if (this.collection.length == 0) {
            $('.empty', this.el).show();
        } else {
            $('.empty', this.el).hide();
        }
        this.collection.each(this.addOne);
    },

    clear: function() {
        _.map(this.views, function(view) {
            view.close();
        });
        this.views = [];
        ths.index = 1;
    },

    addOne: function(radio) {
        var currentId = radio.id;

        var found = _.find(this.views, function(view) {
            if (view.model.id == radio.id) {
                return true;
            }
        });
        if (found) {
            // do not insert duplicated content
            return;
        }

        var view = new Yasound.Views.RadioTopCell({
            model: radio
        });
        $(this.el).append(view.render(this.index++).el);
        this.views.push(view);
    }
});

Yasound.Views.RadioTopCell = Yasound.Views.RadioCell.extend({
    render: function (index) {
        var data = this.model.toJSON();
        data['top_rank'] = index;
        if (data.name.length > 18) {
            data.name = data.name.substring(0,18) + "...";
        }
        if (Yasound.App.enableFX) {
            $(this.el).hide().html(ich.radioCellTemplate(data)).fadeIn(200);
        } else {
            $(this.el).html(ich.radioCellTemplate(data));
        }

        this.currentSongModel.set('radioId', this.model.get('id'));
        return this;
    }
});

Yasound.Views.TopRadiosPage = Backbone.View.extend({
    collection: new Yasound.Data.Models.MostActiveRadios({}),

    initialize: function() {
        _.bindAll(this, 'render', 'onGenreChanged');
        $.subscribe('/submenu/genre', this.onGenreChanged)
    },

    onClose: function() {
        $.unsubscribe('/submenu/genre', this.onGenreChanged)
    },

    reset: function() {
        if (this.resultsView) {
            this.resultsView.close();
            this.resultsViews = undefined;
        }
    },

    render: function(genre) {
        this.reset();

        $(this.el).html(ich.topRadiosPageTemplate());
        this.collection.perPage = Yasound.Utils.cellsPerPage();

        this.resultsView = new Yasound.Views.TopResults({
            collection: this.collection,
            el: $('#results', this.el)
        });

        this.paginationView = new Yasound.Views.Pagination({
            collection: this.collection,
            el: $('#pagination', this.el)
        });

        this.collection.params.genre = genre;

        if (g_bootstrapped_data) {
            this.collection.reset(g_bootstrapped_data);
        } else {
            this.collection.fetch();
        }

        return this;
    },

    onGenreChanged: function(e, genre) {
        this.collection.params.genre = genre;
        this.resultsView.clear();
        this.collection.goTo(0);
    }
});