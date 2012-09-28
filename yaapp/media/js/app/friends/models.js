/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Data.Models');

Yasound.Data.Models.Friends = Yasound.Data.Paginator.extend({
    model: Yasound.Data.Models.User,
    url: '/api/v1/friend/',
    setUsername: function (username) {
        this.username = username;
        this.url = '/api/v1/user/' + username + '/friends/';
        return this;
    }
});

Yasound.Data.Models.Followers = Yasound.Data.Paginator.extend({
    model: Yasound.Data.Models.User,
    url: '/api/v1/follower/',
    setUsername: function (username) {
        this.username = username;
        this.url = '/api/v1/user/' + username + '/followers/';
        return this;
    }
});
