Namespace('Yasound.Views');

Yasound.Views.SearchMenu = Backbone.View.extend({
    el: '#tbar-search',
    events: {
        'keypress #search-input': 'search'
    },
    search: function(e) {
        if (e.keyCode != 13)
            return;

        var value = $('#search-input', this.el).val();
        if (!value)
            return;

        $('#search-input', this.el).val('');
        e.preventDefault();

        Yasound.App.Router.navigate("search/" + value, {
            trigger: true
        });
    }
});

Yasound.Views.RadioCell = Backbone.View.extend({
    tagName: 'li',
    className: 'radio-cell',

    events: {},

    initialize: function() {
        this.model.bind('change', this.render, this);
    },
    render: function() {
        $(this.el).hide().html(ich.radioCellTemplateMessage(data)).fadeIn(200);
        return this;
    }
});

Yasound.Views.SearchResults = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this, 'addOne', 'addAll');

        this.collection.bind('add', this.addOne, this);
        this.collection.bind('reset', this.addAll, this);
        this.views = [];
    },

    addAll: function() {
        this.collection.each(this.addOne);
    },

    clear: function() {
        _.map(this.views, function(view) {
            view.close();
        })
        this.views = [];
    },

    addOne: function(radio) {
        var currentId = radio.id;

        var found = _.find(this.views, function(view) {
            if (view.model.id == radio.id) {
                return true;
            }
        })
        if (found) {
            // do not insert duplicated content
            return;
        }

        var view = new Yasound.Views.RadioCell({
            model: radio
        });

        var lastView = _.max(this.views, function(view) {
            return view.model.get('id');
        });
        var lastId = 0;
        if (lastView) {
            var lastId = lastView.model.id;
        }
        if (currentId >= lastId) {
            $(this.el).prepend(view.render().el);
            // in case of prepend, it means that the wall has been refreshed
            // with new item
            // so we remove the last one in order to avoid infinite addition to
            // the wall
            if (this.views.length >= this.collection.perPage) {
                this.views[0].close();
                this.views.splice(0, 1)
            }
        } else {
            $(this.el).append(view.render().el);
        }
        this.views.push(view);
    }
});