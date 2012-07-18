/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */

Namespace('Yasound.Data.Models');

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
            'style_misc': gettext('Miscellaneous'),
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
