/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Views.Jingles');

Yasound.Data.Models.Jingle = Backbone.Model.extend({
    idAttribute: "_id",
    url: function () {
        return '/api/v1/jingle/' + this.get('_id') + '/';
    }
});

Yasound.Data.Models.Jingles = Yasound.Data.Paginator.extend({
    model: Yasound.Data.Models.Jingle,
    url: function() {
        return '/api/v1/jingle/radio/' + this.uuid + '/';
    },

    setUUID: function(uuid) {
        this.uuid = uuid;
        return this;
    }
});