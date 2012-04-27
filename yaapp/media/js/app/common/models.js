Namespace('Yasound.Data.Models');

/**
 * A radio
 */
Yasound.Data.Models.Radio = Backbone.Model.extend({
    idAttribute: 'uuid',
    urlRoot: '/api/v1/public_radio/',

    connect: function() {
        var id = this.get('id');
        if (id > 0) {
            var url = '/api/v1/radio/' + id + '/connect/';
            $.post(url);
        }
    },

    disconnect: function() {
        var id = this.get('id');
        if (id > 0) {
            var url = '/api/v1/radio/' + id + '/disconnect/';
            $.post(url);
        }
    }
});

/**
 * The song on air
 */
Yasound.Data.Models.CurrentSong = Backbone.Model.extend({
    url: function() {
        return '/api/v1/radio/' + this.get('radioId') + '/current_song/';
    }
});
