/*
 * jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true,
 * evil: true, undef: true, white: true, newcap: true
 */
/* extern Ext, $ */
Namespace('Yasound.Views');

Yasound.Views.RadioResults = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this, 'addOne', 'addAll');

        this.collection.bind('add', this.addOne, this);
        this.collection.bind('reset', this.addAll, this);
        this.collection.bind('beforeFetch', this.beforeFetch, this);
        this.views = [];
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
        mask.remove();
        this.collection.each(this.addOne);
    },

    clear: function() {
        _.map(this.views, function(view) {
            view.close();
        });
        this.views = [];
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

        var view = new Yasound.Views.RadioWithStatsCell({
            model: radio
        });
        $(this.el).append($(view.render().el).hide().fadeIn(200));
        this.views.push(view);
    }
});

/**
 * RadioCell - display a radio in a list
 */
Yasound.Views.RadioWithStatsCell = Backbone.View.extend({
    tagName: 'li',
    initialize: function () {
        this.model.bind('change', this.render, this);
    },
    
    onClose: function () {
        this.model.unbind('change', this.render);
    },
    
    reset: function() {
        if (this.radioCellView) {
            this.radioCellView.reset();
            this.radioCellView.close();
            this.radioCellView = undefined;
        }
    },
    
    render: function () {
        this.reset();
        var data = this.model.toJSON();
        
        $(this.el).hide().html(ich.radioWithStatsCellTemplate(data)).fadeIn(200);
        this.radioCellView = new Yasound.Views.RadioCell({
            el: $('.radio-cell-parent', this.el),
            model: this.model
        }).render();
        
        var stats = data['stats'];
        var chart_data = []
        if (stats) {
            _.each(stats, function(stat) { 
                if (stat['overall_listening_time']) {
                    var date = Yasound.Utils.momentDate(stat['date']).unix();
                    chart_data.push([date, stat['overall_listening_time']])
                }
            });
        }
        
        var options = {
            xaxis: {
                mode: "time",
                minTickSize: [1, "day"]
            }
        };
        
        var plot = $.plot($('.chartdiv', this.el), [chart_data], options);
        
        return this;
    }
});

Yasound.Views.MyRadiosPage = Backbone.View.extend({
    collection: new Yasound.Data.Models.MyRadios({}),
    
    initialize: function () {
    },

    onClose: function () {
    },

    reset: function () {
    },

    render: function (genre) {
        this.reset();
        $(this.el).html(ich.myRadiosPageTemplate());
        this.collection.perPage = 24;

        this.resultsView = new Yasound.Views.RadioResults({
            collection: this.collection,
            el: $('#results', this.el)
        });
        
        this.onGenreChanged('', genre)
        return this;
    },
    
    onGenreChanged: function(e, genre) {
        if (genre == '') {
            this.collection.params.genre = undefined;
        } else {
            this.collection.params.genre = genre;
        }
        this.resultsView.clear();
        this.collection.goTo(0);
    }    
});