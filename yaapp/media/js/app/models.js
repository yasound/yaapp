Namespace('Yasound.Data.Models');

Yasound.Data.Models.Radio = Backbone.Model.extend({
    urlRoot: '/api/v1/radio/'
});

Yasound.Data.Models.CurrentSong = Backbone.Model.extend({
    url: function() {
        return '/api/v1/radio/' + this.get('radioId') + '/current_song/'
    }
});


Yasound.Data.Models.WallEvent = Backbone.Model.extend({
});

Yasound.Data.Models.WallEvents = Backbone.Collection.extend({
    model: Yasound.Data.Models.WallEvent,
    url: function() {
        return '/api/v1/radio/' + this.radio.get('id') + '/wall/'
    }
});