Namespace('Yasound.Data.Models');

Yasound.Data.Models.WallEvent = Backbone.Model.extend({
});

Yasound.Data.Models.WallEvents = Backbone.Collection.extend({
    model: Yasound.Data.Models.WallEvent,
    url: function() {
        return '/api/v1/radio/' + this.radio.get('id') + '/wall'
    }
});