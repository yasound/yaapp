/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Data.Models');

Yasound.Data.Models.SongInstance = Backbone.Model.extend({
    idAttribute: "id"
});

Yasound.Data.Models.SongInstances = Backbone.Paginator.requestPager.extend({
    model: Yasound.Data.Models.SongInstance,
    perPageAttribute: 'limit',
    skipAttribute: 'offset',
    perPage: 25,
    page:0,
    params:{},

    url: function() {
        return '/api/v1/radio/' + this.uuid + '/programming/';
    },

    setUUID: function(uuid) {
        this.uuid = uuid;
        return this;
    },

    parse: function(response) {
        var results = response.objects;
        this.totalCount = response.meta.total_count;
        this.totalPages = this.totalCount / this.perPage;
        return results;
    },
    filterArtists: function(artists) {
        if (artists) {
            _.extend(this.params, {artist:artists});
        } else {
            _.extend(this.params, {artist:undefined});
        }
        this.goTo(0);
    },
    filterAlbums: function(albums) {
        if (albums) {
            _.extend(this.params, {album:albums});
        } else {
            _.extend(this.params, {album:undefined});
        }
        this.goTo(0);
    }
});


Yasound.Data.Models.ProgrammingArtist = Backbone.Model.extend({});

Yasound.Data.Models.ProgrammingArtists = Backbone.Collection.extend({
    model: Yasound.Data.Models.ProgrammingArtist,
    url: function() {
        return '/api/v1/radio/' + this.uuid + '/programming/artists';
    },

    setUUID: function(uuid) {
        this.uuid = uuid;
        return this;
    },
});

Yasound.Data.Models.ProgrammingAlbum = Backbone.Model.extend({});

Yasound.Data.Models.ProgrammingAlbums = Backbone.Collection.extend({
    model: Yasound.Data.Models.ProgrammingAlbum,
    url: function() {
        return '/api/v1/radio/' + this.uuid + '/programming/albums/';
    },

    setUUID: function(uuid) {
        this.uuid = uuid;
        return this;
    },

    filterArtists: function(artists) {
        var params = {};
        if (artists) {
            params = {
                data: {
                    artist: artists
                },
                traditional: true,
                processData: true
            };
        }
        this.fetch(params);
    }
});

Yasound.Data.Models.YasoundSong = Backbone.Model.extend({
    idAttribute: "id"
});

Yasound.Data.Models.YasoundSongs = Backbone.Paginator.requestPager.extend({
    model: Yasound.Data.Models.YasoundSong,
    perPageAttribute: 'limit',
    skipAttribute: 'offset',
    perPage: 25,
    page:0,
    params:{},

    url: function() {
        return '/api/v1/programming/' + this.uuid + '/yasound_songs/';
    },

    setUUID: function(uuid) {
        this.uuid = uuid;
        return this;
    },

    parse: function(response) {
        var results = response.objects;
        this.totalCount = response.meta.total_count;
        this.totalPages = this.totalCount / this.perPage;
        return results;
    },
    filterTrack: function(track) {
        if (track) {
            _.extend(this.params, {name:track});
        } else {
            _.extend(this.params, {name:undefined});
        }
        this.goTo(0);
    },

    filterArtist: function(artist) {
        if (artist) {
            _.extend(this.params, {artist:artist});
        } else {
            _.extend(this.params, {artist:undefined});
        }
        this.goTo(0);
    },

    filterAlbum: function(album) {
        if (album) {
            _.extend(this.params, {album:album});
        } else {
            _.extend(this.params, {album:undefined});
        }
        this.goTo(0);
    }
});