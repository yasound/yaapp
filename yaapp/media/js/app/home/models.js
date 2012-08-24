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

    setGenre: function(genre) {
        if (g_bootstrapped_data) {
            this.reset(g_bootstrapped_data);
            return;
        }

        if (genre == '') {
            return this.fetch()
        } else {
            this.fetch({ data: $.param({ genre: genre}) });
        }
    },
    comparator: function(radioUser) {
        return radioUser.get("id");
    }
});
