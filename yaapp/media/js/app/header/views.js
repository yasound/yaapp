/*
 * jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true,
 * evil: true, undef: true, white: true, newcap: true
 */
/* extern Ext, $ */

Namespace('Yasound.Views');

Yasound.Views.Header = Backbone.View.extend({
    el: '#header',

    events: {
        'keypress #search-input' : 'search',
        'click .btn-register': 'register'
    },

    initialize: function () {
    },

    onClose: function () {
    },

    render: function () {
        return this;
    },

    search: function(e) {
        if (e.keyCode != 13) {
            return;
        }

        var value = $('#search-input', this.el).val();
        if (!value) {
            return;
        }

        $('#search-input', this.el).val('');
        e.preventDefault();

        Yasound.App.Router.navigate("search/" + value + '/', {
            trigger: true
        });
    },

    register: function (e) {
        e.preventDefault();
        Yasound.App.Router.navigate('/signup/', {
            trigger: true
        });
    }
});
