/*
 * jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true,
 * evil: true, undef: true, white: true, newcap: true
 */
/* extern Ext, $ */
Namespace('Yasound.Data.Models');

Yasound.Data.Models.MyRadio = Yasound.Data.Models.Radio.extend({
    urlRoot: '/api/v1/my_radios/'
});

Yasound.Data.Models.MyRadios = Yasound.Data.Paginator.extend({
    idAttribute: "uuid",
    model: Yasound.Data.Models.MyRadio,
    url: function() {
        return '/api/v1/my_radios/';
    }
});
