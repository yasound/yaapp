/*
 * jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true,
 * evil: true, undef: true, white: true, newcap: true
 */
/* extern Ext, $ */
Namespace('Yasound.Data.Models');

Yasound.Data.Models.Gift = Backbone.Model.extend({

});

Yasound.Data.Models.Gifts = Backbone.Paginator.requestPager.extend({
    model: Yasound.Data.Models.Gift,
    url: function() {
        return '/api/v1/premium/gifts/';
    }
});


Yasound.Data.Models.GiftsDigest = Backbone.Paginator.requestPager.extend({
    model: Yasound.Data.Models.Gift,
    url: '/api/v1/premium/gifts/',
    perPageAttribute: 'limit',
    skipAttribute: 'offset',
    perPage: 2,
    page:0,

    parse: function(response) {
        var results = response.objects;
        this.totalCount = response.meta.total_count;
        this.totalPages = this.totalCount / this.perPage;
        return results;
    }
});

Yasound.Data.Models.ServiceHD = Backbone.Model.extend({
    url: function() {
        return '/api/v1/premium/services/0/';
    }
});
