"use strict";
/*
 * jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true,
 * evil: true, undef: true, white: true, newcap: true
 */
/* extern Ext, $ */
Namespace('Yasound.Data.Models');

Yasound.Data.Models.SelectedRadios = Backbone.Collection.extend({
    model: Yasound.Data.Models.Radio,
    url: function() {
        return '/api/v1/selected_web_radio/';
    },

    comparator: function(radioUser) {
        return radioUser.get("id");
    }
});

Yasound.Data.Models.MostActiveRadios = Backbone.Collection.extend({
    model: Yasound.Data.Models.Radio,
    url: function() {
        return '/api/v1/most_active_radio/';
    }
});
