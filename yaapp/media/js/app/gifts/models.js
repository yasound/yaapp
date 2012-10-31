/*
 * jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true,
 * evil: true, undef: true, white: true, newcap: true
 */
/* extern Ext, $ */
Namespace('Yasound.Data.Models');

Yasound.Data.Models.Gift = Backbone.Model.extend({

});

Yasound.Data.Models.Gifts = Backbone.Collection.extend({
    model: Yasound.Data.Models.Gift,
    url: function() {
        return '/api/v1/premium/gifts/';
    }
});

Yasound.Data.Models.ServiceHD = Backbone.Model.extend({
    url: function() {
        return '/api/v1/premium/services/0/';
    }
});
