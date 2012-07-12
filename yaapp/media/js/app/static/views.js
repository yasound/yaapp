/*
 * jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true,
 * evil: true, undef: true, white: true, newcap: true
 */
/* extern Ext, $ */
Namespace('Yasound.Views.Static');

/**
 * Legal page
 */
Yasound.Views.Static.LegalPage = Backbone.View.extend({
    initialize: function () {
        _.bindAll(this, 'render');
    },
    reset: function() {
        
    },
    render: function () {
        this.reset();
        $(this.el).html(ich.staticLegalPageTemplate());
        return this;
    }
});

/**
 * Contact page
 */
Yasound.Views.Static.ContactPage = Backbone.View.extend({
    initialize: function () {
        _.bindAll(this, 'render');
    },
    reset: function() {
        
    },
    render: function () {
        this.reset();
        $(this.el).html(ich.staticContactPageTemplate());
        return this;
    }
});