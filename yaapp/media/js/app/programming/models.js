"use strict";
/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Data.Models');

Yasound.Data.Models.SongInstance = Backbone.Model.extend({
    idAttribute: "id"
});

Yasound.Data.Models.SongInstances = Backbone.Paginator.requestPager.extend({
    model: Yasound.Data.Models.SongInstance,
    url: '/api/v1/my_programming/', 
    perPageAttribute: 'limit',
    skipAttribute: 'offset',
    perPage: 25,
    page:0,
    params:{},
    
    parse: function(response) {
        var results = response.objects;
        this.totalCount = response.meta.total_count;
        this.totalPages = this.totalCount / this.perPage;
        return results;
    },
    filterArtists: function(artists) {
        this.params = {};
        if (artists) {
            _.extend(this.params, {artist:artists});
        }
        this.goTo(0);
    }
});


Yasound.Data.Models.ProgrammingArtist = Backbone.Model.extend({});

Yasound.Data.Models.ProgrammingArtists = Backbone.Collection.extend({
    model: Yasound.Data.Models.ProgrammingArtist,
    url: '/api/v1/my_programming/artists/'    
});