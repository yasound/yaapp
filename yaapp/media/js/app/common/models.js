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
    queryAttribute: 'q',
    params: {},

    parse: function(response) {
        var results = response.objects;
        this.totalCount = response.meta.total_count;
        this.next = response.meta.next;
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
        $.ajax({
            url: url,
            type: 'POST',
            dataType: 'json',
            success: function(data) {
                that.set({
                    'favorite': true,
                    'favorites' : data.favorites
                }, {
                    silent: true
                });
                $.publish('/radio/favorite', that);
            },
            failure: function() {
            }
        });
    },

    removeFromFavorite: function () {
        var url = '/api/v1/radio/' + this.get('id') + '/not_favorite/';
        var that = this;
        $.ajax({
            url: url,
            type: 'POST',
            dataType: 'json',
            success: function(data) {
                that.set({
                    'favorite': false,
                    'favorites' : data.favorites
                }, {
                    silent: true
                });
                $.publish('/radio/not_favorite', that);
            },
            failure: function() {
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
        };
        return genre_data[genre_id];
    },

    broadcast: function (message) {
        var url = '/api/v1/radio/' + this.get('uuid') + '/broadcast_message/';
        var that = this;
        var params = {
            message: message
        };
        $.post(url, params);
    },

    fetchAuthenticatedURL: function (callback) {
        var url = '/api/v1/streamer_auth_token/';
        var streamURL = this.get('stream_url');
        $.ajax({
            url: url,
            type: 'GET',
            dataType: 'json',
            success: function(data) {
                var token = data.token;
                var fullURL = streamURL + '/?token=' + token;
                callback(fullURL);
                //callback(streamURL);
            },
            failure: function() {
                callback(streamURL);
            }
        });
    },

    toJSON: function() {
        var data = Yasound.Data.Models.Radio.__super__.toJSON.apply(this);
        data.fullname = data.name;
        if (data && data.name && data.name.length > 18) {
            data.name = data.name.substring(0,18) + "...";
        }

        data.multiple_favorites = false;
        if (data.favorites > 1) {
            data.multiple_favorites = true;
        }

        data.multiple_messages = false;
        if (data.messages > 1) {
            data.multiple_messages = true;
        }

        data.genre_display = this.genre();

        return data;
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
        _.bindAll(this, 'refresh', 'stopPushOrTimer', 'startPushOrTimer', 'startPush', 'startTimer', 'onClose');

        var that = this;
        that.startPushOrTimer();
    },

    onClose: function () {
        this.stopPushOrTimer();
    },

    refresh: function (msg) {
        this.set(msg);
    },

    stopPushOrTimer: function () {
        var that = this;
        if (that.timer) {
            clearInterval(that.timer);
            that.timer = undefined;
        }
        if (Yasound.App.Router.pushManager.enablePush) {
            Yasound.App.Router.pushManager.off('song', this.refresh);
        }
    },

    startPushOrTimer: function () {
        var that = this;
        if (Yasound.App.Router.pushManager.enablePush) {
            Yasound.App.Router.pushManager.on('song', this.refresh);
        } else {
            that.timer = setInterval(function () {
                that.fetch();
            }, 10000);
        }
    },

    startPush: function () {
        var that = this;
        Yasound.App.Router.pushManager.on('song', this.refresh);
    },

    startTimer: function () {
        var that = this;
        that.timer = setInterval(function () {
            that.fetch();
        }, 10000);

    },

    setOrigin: function (origin) {
        this.stopPushOrTimer();
        if (origin !== Yasound.App.RADIO_ORIGIN_YASOUND) {
            this.startTimer();
        } else {
            this.startPushOrTimer();
        }
    },

    rawTitle: function () {
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
        var str = context.name() + ' ' + ' ' + context.artist();
        if (context.album() != gettext('Unknown album')) {
            str = str + ' ' +  ' ' + context.album();
        }
        return str;
    },

    rawTitleWithoutAlbum: function () {
        var model = this;
        var context = {
            name: function() {
                var s = model.get('name');
                if (!s) {
                    return gettext('');
                }
                return s;
            },
            artist: function() {
                var s = model.get('artist');
                if (!s) {
                    return gettext('');
                }
                return s;
            }
        };
        var str = context.name() + ' ' + ' ' + context.artist();
        return str;
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

    title_wrapped: function() {
        var title = this.title();
        if (title.length > 53) {
            return title.substr(0, 53);
        }
        return title;
    },

    like: function () {
        var songId = this.get('id');
        var url = '/api/v1/song/' + songId + '/liker/';
        $.post(url);
    },

    toJSON: function() {
        var data = Yasound.Data.Models.CurrentSong.__super__.toJSON.apply(this);
        data['title'] = this.title();
        data['title_wrapped'] = this.title_wrapped();
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

        data['fagc'] = '';
        data['agc'] = '';
        data['human_date'] = this.humanDate();

        var addComma = false;

        if (this.get('followers_count') > 1) {
            data['fagc'] = this.get('followers_count') +  ' ' + gettext('followers');
            addComma = true;

        } else if (this.get('followers_count') == 1) {
            data['fagc'] = this.get('followers_count') +  ' ' + gettext('follower');
            addComma = true;
        }

        if (this.get('age')) {
            if (addComma) {
                data['fagc'] = data['fagc'] + ', ';
            }
            data['fagc'] = data['fagc'] + this.get('age') +  ' ' + gettext('years old');
            data['agc'] = this.get('age') +  ' ' + gettext('years old');
            addComma = true;
        }
        if (this.get('gender')) {
            var gender = this.get('gender');
            var gender_display = '';
            if (gender == 'M') {
                gender_display = gettext('male');
            } else if (gender == 'F') {
                gender_display = gettext('female');
            }
            if (addComma) {
                data['agc'] = data['agc'] + ', ' + gender_display;
                data['fagc'] = data['fagc'] + ', ' + gender_display;
            } else {
                data['agc'] = data['agc'] + gender_display;
                data['fagc'] = data['fagc'] + gender_display;
            }
            addComma = true;
        }
        if (this.get('city')) {
            if (addComma) {
                data['agc'] = data['agc'] + ', ' + this.get('city');
                data['fagc'] = data['fagc'] + ', ' + this.get('city');
            } else {
                data['agc'] = data['agc'] + this.get('city');
                data['fagc'] = data['fagc'] + this.get('city');
            }
        }
        return data;
    },

    follow: function(requestUser) {
        this.set({'is_friend': true});
        var url = '/api/v1/user/' + requestUser + '/friends/' + this.get('username') + '/';
        $.ajax({
           url: url,
           type: 'POST'
        });
    },

    unfollow: function(requestUser) {
        this.set({'is_friend': false});
        var url = '/api/v1/user/' + requestUser + '/friends/' + this.get('username') + '/';
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
Yasound.Data.Models.ConnectedUsers = Yasound.Data.Paginator.extend({
    model: Yasound.Data.Models.ConnectedUser,
    url: function() {
        return '/api/v1/fast_connected_users/?limit=13';
    }
});

Yasound.Data.Models.PublicStats =  Backbone.Model.extend({
    urlRoot: '/api/v1/public_stats/'
});
