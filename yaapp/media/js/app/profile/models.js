/*
 * jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true,
 * evil: true, undef: true, white: true, newcap: true
 */
/* extern Ext, $ */
Namespace('Yasound.Data.Models');

Yasound.Data.Models.Like = Backbone.Model.extend({
    idAttribute: 'id',

    title: function() {
        var model = this;
        var context = {
            name: function() {
                var s = model.get('song_name');
                if (!s) {
                    return gettext('Unknown song');
                }
                return s;
            },
            artist: function() {
                var s = model.get('song_artist');
                if (!s) {
                    return gettext('Unknown artist');
                }
                return s;
            },
            album: function() {
                var s = model.get('song_album');
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
        var data = Yasound.Data.Models.Radio.__super__.toJSON.apply(this);
        data.title = this.title();
        return data;
    }

});

Yasound.Data.Models.Likes = Yasound.Data.Paginator.extend({
    model: Yasound.Data.Models.Like,
    url: '/api/v1/likes/',
    setUsername: function (username) {
        this.username = username;
        this.url = '/api/v1/user/' + username + '/likes/';
        return this;
    }
});
