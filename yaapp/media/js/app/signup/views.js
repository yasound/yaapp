/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Views');

Yasound.Views.SignupPage = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this, 'render', 'templateLoaded');
    },

    onClose: function() {
    },

    reset: function() {
    },

    render: function(query) {
        this.reset();
        ich.loadRemoteTemplate('signup/signup.mustache', 'signupPageTemplate', this.templateLoaded);
        return this;
    },
    
    templateLoaded: function() {
        $(this.el).html(ich.signupPageTemplate());
    }
});