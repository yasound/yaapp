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
    events: {
        'plothover .chartdiv': 'plotHover',
        'click .edit-radio': 'onEditRadio',
        'click .edit-playlist': 'onEditPlaylist',
        'click .delete-radio': 'onDeleteRadio',
        'click .responsive-settings-icon': 'onEditRadio',
        'click .responsive-playlist-icon': 'onEditPlaylist',
        'click .responsive-delete-icon': 'onDeleteRadio'
    },

    initialize: function () {
        _.bindAll(this, 'render', 'plotHover', 'showToolTip');
        this.model.bind('change', this.render, this);

        this.previousPoint = null;
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
        var chart_data = [];
        if (stats) {
            _.each(stats, function(stat) {
                if (stat['connections']) {
                    var date = Yasound.Utils.momentDate(stat['date']).unix()*1000;
                    chart_data.push([date, stat['connections']]);
                }
            });
        }

        var options = {
            xaxis: {
                mode: "time",
                minTickSize: [1, "day"],
                timeformat: gettext("%b %d"),
                monthNames: [gettext("jan"),
                             gettext("feb"),
                             gettext("mar"),
                             gettext("apr"),
                             gettext("may"),
                             gettext("jun"),
                             gettext("jul"),
                             gettext("aug"),
                             gettext("sept"),
                             gettext("oct"),
                             gettext("nov"),
                             gettext("dec")]
            },
            grid: { hoverable: true, clickable: true }
        };

        var plot = $.plot($('.chartdiv', this.el), [chart_data], options);

        return this;
    },

    plotHover: function(event, pos, item) {
        if (item) {
            if (this.previousPoint != item.dataIndex) {
                this.previousPoint = item.dataIndex;

                $("#tooltip", this.el).remove();
                var x = item.datapoint[0].toFixed(2),
                    y = item.datapoint[1].toFixed(2);

                var formattedDate = moment.unix(x/1000).format('LL');
                var formattedValue = Math.round(y) + ' ' + gettext('listeners');
                this.showToolTip(item.pageX, item.pageY,
                            formattedDate + " :<br/> " + formattedValue);
            }
        }
        else {
            $("#tooltip", this.el).remove();
            this.previousPoint = null;
        }
    },

    showToolTip: function(x, y, contents) {
        $('<div id="tooltip">' + contents + '</div>').css( {
            position: 'absolute',
            display: 'none',
            top: y + -58,
            left: x + -35,
            'background-color': '#4b4b4b',
            opacity: 0.90,
            'border-radius':'5px',
			'color':'white',
            'font-size':'11px',
            'font-weight':'bold',
            'padding':'3px'
        }).appendTo(this.el).fadeIn(200);
    },

    onEditRadio: function (e) {
        e.preventDefault();

        Yasound.App.Router.navigate("radio/" + this.model.get('uuid') + '/edit/', {
            trigger: true
        });
    },

    onEditPlaylist: function (e) {
        e.preventDefault();

        Yasound.App.Router.navigate("radio/" + this.model.get('uuid') + '/programming/', {
            trigger: true
        });
    },

    onDeleteRadio: function (e) {
        e.preventDefault();
        var that = this;
        $('#modal-delete-radio').modal('show');
        $('#modal-delete-radio .btn-primary').one('click', function () {
            val = $('#modal-delete-radio input').val();
            if (val == gettext('yes')) {
                that.model.destroy();
                that.remove();
            }
            $('#modal-delete-radio input').val('');
            $('#modal-delete-radio').modal('hide');
        });

    }

});

Yasound.Views.MyRadiosPage = Backbone.View.extend({
    collection: new Yasound.Data.Models.MyRadios({}),

    events: {
        "click #create-radio-btn": "onCreateRadio"
    },

    initialize: function () {
    },

    onClose: function () {
    },

    reset: function () {
    },

    render: function (genre) {
        this.reset();
        $(this.el).html(ich.myRadiosPageTemplate());
        this.collection.perPage = 8;

        this.resultsView = new Yasound.Views.RadioResults({
            collection: this.collection,
            el: $('#results', this.el)
        });

        this.paginationView = new Yasound.Views.Pagination({
            collection: this.collection,
            el: $('#pagination', this.el)
        });

        this.onGenreChanged('', genre);
        return this;
    },

    onGenreChanged: function(e, genre) {
        if (genre === '') {
            this.collection.params.genre = undefined;
        } else {
            this.collection.params.genre = genre;
        }
        this.resultsView.clear();
        this.collection.goTo(0);
    },

    onCreateRadio: function (e) {
        e.preventDefault();
        Yasound.App.Router.navigate("radios/new/", {
            trigger: true
        });
    }
});
