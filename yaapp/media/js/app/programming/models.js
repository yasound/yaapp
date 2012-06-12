"use strict";
/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Data.Models');

Yasound.Data.Models.SongInstance = Backbone.Model.extend({
    idAttribute: "id",
    url: function () {
        // TODO
    },
});

Yasound.Data.Models.SongInstances = Backbone.Paginator.requestPager.extend({
    model: Yasound.Data.Models.SongInstance,
    url: '/api/v1/my_programming', 
    perPageAttribute: 'limit',
    skipAttribute: 'offset',
    perPage: 25,
    page:0,
    customAttribute1: 'read_status',
    customParam1: 'unread',
    
    
    parse: function(response) {
        var results = response.objects;
        this.totalCount = response.meta.total_count;
        this.totalPages = this.totalCount / this.perPage;
        return results;
    },
    
    fetchFirst: function() {
        var savedPage = this.page;
        this.page = 0;
        var that = this;
        this.fetch({
            success: function() {
                that.page = savedPage;
            },
            error: function() {
                that.page = savedPage;
            }
        });
    }    
});