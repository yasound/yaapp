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
            },
            album: function() {
                var s = model.get('album');
                if (!s) {
                    return gettext('Unknown album');
                }
                return s;
            }
            
        };
        var str = context.name() + ' ' + gettext('by') + ' ' + context.artist();
        if (context.album() != gettext('Unknown album')) {
            str = str + ' ' + gettext('on') + ' ' + context.album();
        }
        return str;
    },
    
    toJSON: function() {
        var data = Yasound.Data.Models.CurrentSong.__super__.toJSON.apply(this);
        data['title'] = this.title();
        return data;
    }
});


Yasound.Data.Models.User = Backbone.Model.extend({
    idAttribute: 'username',
    
    url: function () {
        return '/api/v1/public_user/' + this.id + '/';
    },
    
    initialize: function () {
        _.bindAll(this, 'fetchSuccess');

        this.currentRadio = new Yasound.Data.Models.Radio(this.get('current_radio'));
        this.ownRadio = new Yasound.Data.Models.Radio(this.get('own_radio'));
        
        this.bind('change', this.fetchSuccess);
    },
    
    fetchSuccess: function () {
        this.currentRadio.clear({silent: true});
        this.currentRadio.set(this.get('current_radio'));

        this.ownRadio.clear({silent: true});
        this.ownRadio.set(this.get('own_radio'));
    },
    
    humanDate: function() {
        var history = this.get('history');
        if (history) {
            var date = history['date'];
            if (date) {
                return _.str.capitalize(Yasound.Utils.humanizeDate(this.get('history')['date']));
            }
         }
        return '';
    },
    
    toJSON: function() {
        var data = Yasound.Data.Models.User.__super__.toJSON.apply(this);
        
        data['agc'] = '';
        data['human_date'] = this.humanDate();
        
        if (this.get('age')) {
            data['agc'] = this.get('age') +  ' ' + gettext('years old');
        }
        if (this.get('gender')) {
            data['agc'] = data['agc'] + ', ' + this.get('gender');
        }
        if (this.get('city')) {
            data['agc'] = data['agc'] + ', ' + this.get('city');
        }
        return data;
    },
    
    follow: function(requestUser) {
        this.set({'is_friend': true});
        var url = '/api/v1/user/' + requestUser + '/friends/' + this.get('username');
        $.ajax({
           url: url,
           type: 'POST'
        });
    },
        
    unfollow: function(requestUser) {
        this.set({'is_friend': false});
        var url = '/api/v1/user/' + requestUser + '/friends/' + this.get('username');
        $.ajax({
           url: url,
           type: 'DELETE'
        });
    }
    
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
