/*
 * jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true,
 * evil: true, undef: true, white: true, newcap: true
 */
/* extern Ext, $ */
Namespace('Yasound.Views');

/**
 * Generic static page
 */
Yasound.Views.StaticPage = Backbone.View.extend({
    initialize: function () {
        _.bindAll(this, 'render', 'templateLoaded');
    },
    reset: function() {

    },

    templateUrl: function (page) {
        return 'static/' + page + '.mustache';
    },

    templateName: function (page) {
        return 'static' + page + 'Template';
    },

    render: function (page) {
        this.reset();
        this.page = page;
        ich.loadRemoteTemplate(this.templateUrl(page), this.templateName(page), this.templateLoaded);
        return this;
    },

    templateLoaded: function() {
        var page = this.page;
        $(this.el).html(ich[this.templateName(page)]());
    }
});

