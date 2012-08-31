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
    idAttribute: "id"
});

Yasound.Data.Models.Deezer.Tracks = Backbone.Collection.extend({
    model: Yasound.Data.Models.Deezer.Track
});

