/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Data.Models');

Yasound.Data.Models.RadioSearchResults = Yasound.Data.Paginator.extend({
    model: Yasound.Data.Models.Radio,
    url: '/api/v1/search/radios/',
    setQuery: function(query) {
        this.reset();
        this.query = query;
        this.lastId = 0;
        return this;
    }
});