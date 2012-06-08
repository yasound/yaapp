"use strict";
/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Models');

Yasound.Data.Models.Notification = Backbone.Model.extend({
    idAttribute: "_id",
    url: function () {
        return '/api/v1/notifications/' + this.get('id') + '/';
    }
});

Yasound.Data.Models.Notifications = Backbone.Paginator.requestPager.extend({
    model: Yasound.Data.Models.Notification,
    url: '/api/v1/notifications/',
    perPageAttribute: 'limit',
    skipAttribute: 'offset',
    perPage: 25,
    page:0,
    
    parse: function(response) {
        var results = response.objects;
        this.totalCount = response.meta.total_count;
        this.totalPages = this.totalCount / this.perPage;
        return results;
    },
    comparator: function(notification) {
        return -parseInt(notification.get("id"));
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
