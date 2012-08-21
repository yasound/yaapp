/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Data.Models');

Yasound.Data.Models.Favorites = Yasound.Data.Paginator.extend({
    model: Yasound.Data.Models.Radio,
    url: '/api/v1/favorite_radio/',
    setUsername: function(username) {
        this.url = '/api/v1/user/' + username + '/favorites/';
        return this;
    }
});
