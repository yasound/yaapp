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

    setStyle: function(style) {
        this.fetch({ data: $.param({ style: style}) });
    },
    comparator: function(radioUser) {
        return radioUser.get("id");
    }
});


