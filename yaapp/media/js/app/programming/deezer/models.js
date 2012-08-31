/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Data.Models.Deezer');

Yasound.Data.Models.Deezer.Playlist = Backbone.Model.extend({
    idAttribute: "id"
});

Yasound.Data.Models.Deezer.Playlists = Backbone.Collection.extend({
    model: Yasound.Data.Models.Deezer.Playlist
});

Yasound.Data.Models.Deezer.Track = Backbone.Model.extend({
    idAttribute: "id",

    addToRadio: function(uuid, successCallback, errorCallback) {
        var url = '/api/v1/deezer/import_track/' + uuid + '/';
        var name = this.get('title');
        var artist_name = '';
        var album_name = '';
        if (this.get('artist')) {
            artist_name = this.get('artist').name
        }
        if (this.get('album')) {
            album_name = this.get('album').title;
        }
        var params = {
            'name': name,
            'artist_name': artist_name,
            'album_name': album_name
        };

        $.post(url, params, function(data) {
            var success = data.success;
            if (data.success) {
                successCallback(data.message);
            } else {
                errorCallback(data.message);
            }
        }, 'json');
    }
});

Yasound.Data.Models.Deezer.Tracks = Backbone.Collection.extend({
    model: Yasound.Data.Models.Deezer.Track
});

