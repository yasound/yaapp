Namespace('Yasound.Data.Models');


Yasound.Data.Models.WallEvent = Backbone.Model.extend({
    idAttribute: 'id'
});

Yasound.Data.Models.WallEvents = Backbone.Collection.extend({
    model: Yasound.Data.Models.WallEvent,
    lastId: 0,
    limit: 25,
    url: function() {
        var lastId = this.findLastId();
        if (!lastId) {
            lastId = this.lastId;
        }
        return '/api/v1/radio/' + this.radio.get('id') + '/wall/?id__gt=' + lastId + '&limit=' + this.limit;
    },
    setRadio: function(radio) {
        this.reset();
        this.radio = radio;
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
    comparator: function(wallEvent) {
        return wallEvent.get("id");
    }
});

Yasound.Data.Models.PaginatedWallEvents = Backbone.Paginator.requestPager.extend({
    model: Yasound.Data.Models.WallEvent,
    url: '/api/v1/radio/0/wall/',
    perPageAttribute: 'limit',
    skipAttribute: 'offset',
    perPage: 25,
    page:0,
    lastId: 0,
    
    parse: function(response) {
        var results = response.objects;
        this.totalCount = response.meta.total_count;
        this.totalPages = this.totalCount / this.perPage;
        return results;
    },
    setRadio: function(radio) {
        this.reset();
        this.radio = radio;
        this.lastId = 0;
        this.url = '/api/v1/radio/' + this.radio.get('id') + '/wall/';
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
    comparator: function(wallEvent) {
        return wallEvent.get("id");
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
        })
    }

});

Yasound.Data.Models.RadioUser = Backbone.Model.extend({});
Yasound.Data.Models.RadioUsers = Backbone.Collection.extend({
    model: Yasound.Data.Models.RadioUser,
    limit: 25,
    url: function() {
        return '/api/v1/radio/' + this.radio.get('id') + '/current_user/';
    },

    setRadio: function(radio) {
        this.reset();
        this.radio = radio;
        return this;
    },

    comparator: function(radioUser) {
        return radioUser.get("id");
    }
});
