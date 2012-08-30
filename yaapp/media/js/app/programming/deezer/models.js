/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Data.Models.Deezer');

Yasound.Data.Models.Deezer.Playlist = Backbone.Model.extend({
    idAttribute: "id"
});

Yasound.Data.Models.Deezer.Playlists = Backbone.Paginator.requestPager.extend({
    model: Yasound.Data.Models.Deezer.Playlist,
    perPageAttribute: 'limit',
    skipAttribute: 'offset',
    perPage: 25,
    page:0,
    params:{},

    url: function() {
        return '/api/v1/' + this.username + '/deezer/playlists/';
    },

    setUsername: function(username) {
        this.username = username;
        return this;
    },

    parse: function(response) {
        var results = response.objects;
        this.totalCount = response.meta.total_count;
        this.totalPages = this.totalCount / this.perPage;
        return results;
    }
});