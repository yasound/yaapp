"use strict";
/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Views');

/**
 * Programming page
 */
Yasound.Views.ProgrammingPage = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this, 'render');
    },

    onClose: function() {
    },

    reset: function() {
    },
    
    render: function() {
        this.reset();
        $(this.el).html(ich.programmingPageTemplate());
        return this;
    },
});
