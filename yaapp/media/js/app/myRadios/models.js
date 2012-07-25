/*
 * jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true,
 * evil: true, undef: true, white: true, newcap: true
 */
/* extern Ext, $ */
Namespace('Yasound.Data.Models');

Yasound.Data.Models.MyRadios = Yasound.Data.Paginator.extend({
    model: Yasound.Data.Models.Radio,
    url: function() {
        return '/api/v1/my_radios/';
    }
});