Namespace('Yasound.Views');

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

