/*
 * jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true,
 * evil: true, undef: true, white: true, newcap: true
 */
/* extern Ext, $ */
Namespace('Yasound.Data.Models');

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
        return _.str.capitalize(Yasound.Utils.humanizeDate(this.get('history')['date']));
    }
});
