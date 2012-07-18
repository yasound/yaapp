/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Data.Models');

Yasound.Data.Models.Favorites = Backbone.Paginator.requestPager.extend({
    model: Yasound.Data.Models.Radio,
    url: '/api/v1/favorite_radio/',
    perPageAttribute: 'limit',
    skipAttribute: 'offset',
    perPage: 25,
    page:0,
    lastId: 0,
    queryAttribute: 'search',
    params: {},
    
    parse: function(response) {
        var results = response.objects;
        this.totalCount = response.meta.total_count;
        this.totalPages = this.totalCount / this.perPage;
        return results;
    },
    setQuery: function(query) {
        this.reset();
        this.query = query;
        this.lastId = 0;
        return this;
    },
    findLastId: function() {
        var lastObject = this.max(function(event) {
            return event.get('id');
        });
        if (lastObject) {
            this.lastId = lastObject.get('id');
            return lastObject.get('id');
        }
    },
    comparator: function(obj) {
        return -parseInt(obj.get("id"), 10);
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