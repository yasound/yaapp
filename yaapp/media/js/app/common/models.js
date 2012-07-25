/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */

Namespace('Yasound.Data');
Namespace('Yasound.Data.Models');

/**
 * Generic pager wrapper
 */
Yasound.Data.Paginator = Backbone.Paginator.requestPager.extend({
    model: undefined,
    url: '',
    perPageAttribute: 'limit',
    skipAttribute: 'offset',
    perPage: 16,
    page:0,
    lastId: 0,
    queryAttribute: 'search',
    params: {},
    
    parse: function(response) {
        var results = response.objects;
        this.totalCount = response.meta.total_count;
        this.totalPages = Math.ceil(this.totalCount / this.perPage);
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

/**
 * A radio
 */
Yasound.Data.Models.Radio = Backbone.Model.extend({
    idAttribute: 'uuid',
    urlRoot: '/api/v1/public_radio/',

    // notify server that user is connected to radio
    connect: function () {
        var id = this.get('id');
        if (id > 0) {
            var url = '/api/v1/radio/' + id + '/connect/';
            $.post(url);
        }
    },

    // notify server that user is not connected anymore
    disconnect: function () {
        var id = this.get('id');
        if (id > 0) {
            var url = '/api/v1/radio/' + id + '/disconnect/';
            $.post(url);
        }
    },
    addToFavorite: function () {
        var url = '/api/v1/radio/' + this.get('id') + '/favorite/';
        var that = this;
        $.post(url, {
            success: function () {
                that.set('favorite', true);
                $.publish('/radio/favorite');
                that.trigger('radioFavorite');
            }
        });
    },

    removeFromFavorite: function () {
        var url = '/api/v1/radio/' + this.get('id') + '/not_favorite/';
        var that = this;
        $.post(url, {
            success: function () {
                that.set('favorite', false);
                $.publish('/radio/not_favorite');
                that.trigger('radioNotFavorite');
            }
        });
    },
    genre: function() {
        var genre_id = this.get('genre');
        var genre_data = {
            'style_all': gettext('All genres'),
            'style_classical': gettext('Classical'),
            'style_blues': gettext('Blues'),
            'style_alternative': gettext('Alternative'),
            'style_electro': gettext('Electro'),
            'style_chanson_francaise': gettext('French Music'),
            'style_jazz': gettext('Jazz'),
            'style_pop': gettext('Pop'),
            'style_reggae': gettext('Reggae'),
            'style_rock': gettext('Rock'),
            'style_metal': gettext('Metal'),
            'style_hiphop': gettext('Hip Hop'),
            'style_rnbsoul': gettext('RnB / Soul'),
            'style_world': gettext('World'),
            'style_misc': gettext('Miscellaneous')
        }
        return genre_data[genre_id];
    }
});

/**
 * The song on air
 */
Yasound.Data.Models.CurrentSong = Backbone.Model.extend({
    url: function () {
        return '/api/v1/radio/' + this.get('radioId') + '/current_song/';
    },

    // the current song will auto-refresh with either polling or push system
    initialize: function () {
        var that = this;
        if (Yasound.App.Router.pushManager.enablePush) {
            Yasound.App.Router.pushManager.on('song', function (msg) {
                that.set(msg);
            });
        } else {
            setInterval(function () {
                that.fetch();
            }, 10000);
        }
    },
    title: function() {
        var model = this;
        var context = {
            name: function() {
                var s = model.get('name');
                if (!s) {
                    return gettext('Unknown song');
                }
                return s;
            },
            artist: function() {
                var s = model.get('artist');
                if (!s) {
                    return gettext('Unknown artist');
                }
                return s;
            }
        };
        var str = context.name() + ' ' + gettext('by') + ' ' + context.artist();
        return str;
    }
});


Yasound.Data.Models.User = Backbone.Model.extend({
    idAttribute: 'id'
});

/**
 * Connected user
 */
Yasound.Data.Models.ConnectedUser = Backbone.Model.extend({
    idAttribute: 'id'
});

/**
 * Connected user list
 */
Yasound.Data.Models.ConnectedUsers = Backbone.Collection.extend({
    model: Yasound.Data.Models.ConnectedUser,
    url: function() {
        return '/api/v1/fast_connected_users/?limit=13';
    }
});


Yasound.Data.Models.PublicStats =  Backbone.Model.extend({
    urlRoot: '/api/v1/public_stats/'
});
