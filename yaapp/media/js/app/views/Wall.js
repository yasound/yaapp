Namespace('Yasound.Views');
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