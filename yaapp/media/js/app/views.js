Namespace('Yasound.Views');

Yasound.Views.Radio = Backbone.View.extend({
    tagName : 'div',
    className : 'radio',
    events : {},

    initialize : function() {
        this.model.bind('change', this.render, this);
    },

    render : function() {
        $(this.el).html(ich.radioTemplate(this.model.toJSON()));
        return this;
    }
});

Yasound.Views.CurrentSong = Backbone.View.extend({
    tagName : 'div',
    className : 'track',

    events : {},

    initialize : function() {
        this.model.bind('change', this.render, this);
    },

    render : function() {
        $(this.el).html(ich.trackTemplate(this.model.toJSON()));
        return this;
    }
});

Yasound.Views.WallEvents = Backbone.View.extend({
    initialize : function() {
        _.bindAll(this, 'addOne', 'addAll');

        this.collection.bind('add', this.addOne);
        this.collection.bind('reset', this.addAll, this);
        this.views = [];
    },

    addAll : function() {
        this.views = [];
        this.collection.each(this.addOne);
    },

    addOne : function(wallEvent) {
        var view = new Yasound.Views.WallEvent({
            model : wallEvent
        });
        $(this.el).prepend(view.render().el);
        this.views.push(view);
        view.bind('all', this.rethrow, this);
    },

    rethrow : function() {
        this.trigger.apply(this, arguments);
    }

});

Yasound.Views.WallEvent = Backbone.View.extend({
    tagName : 'li',
    className : 'wall-event',

    events : {},

    initialize : function() {
        this.model.bind('change', this.render, this);
    },

    render : function() {
        $(this.el).html(ich.wallEventTemplate(this.model.toJSON()));
        return this;
    }
});

