"use strict";
/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Models');

Yasound.Data.Models.Notification = Backbone.Model.extend({
    idAttribute: "_id",
    url: function () {
        return '/api/v1/notifications/' + this.get('id') + '/';
    },
    
    getDate: function() {
        var timeZone = '+01:00';
        if (moment().isDST()) {
            timeZone = '+02:00';
        }
        // if start_date contains microsecond precision, we remove it
        var theDate = this.get('date').substr(0, 19);
        theDate = moment(theDate + timeZone);
        return theDate;
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
