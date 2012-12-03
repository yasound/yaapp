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
        'click .btn-register': 'onRegister',
        'click #profile-menu .my-profile': 'onMyProfile',
        'click #profile-menu .my-radios': 'onMyRadios',
        'click #profile-menu .my-settings': 'onMySettings',
        'click #profile-menu .about': 'onAbout',
        'click #profile-menu .legal': 'onLegal',
        'click #profile-menu .logout': 'onLogout'
    },

    initialize: function () {
        _.bindAll(this, 'render', 'hidePopupProfile');
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

    hidePopupProfile: function () {
        $('#profile-menu').parent().removeClass('open');
    },

    onRegister: function (e) {
        e.preventDefault();
        Yasound.App.Router.navigate('/signup/', {
            trigger: true
        });
    },

    onMyProfile: function (e) {
        e.preventDefault();
        this.hidePopupProfile();
        Yasound.App.Router.navigate('profile/' + Yasound.App.username + '/', {
            trigger: true
        });
        return false;
    },

    onMySettings: function (e) {
        e.preventDefault();
        this.hidePopupProfile();
        Yasound.App.Router.navigate('settings/', {
            trigger: true
        });
        return false;
    },

    onMyRadios: function (e) {
        e.preventDefault();
        this.hidePopupProfile();
        Yasound.App.Router.navigate('radios/', {
            trigger: true
        });
        return false;
    },

    onAbout: function (e) {
        e.preventDefault();
        this.hidePopupProfile();
        Yasound.App.Router.navigate('about/', {
            trigger: true
        });
        return false;
    },

    onLegal: function (e) {
        e.preventDefault();
        this.hidePopupProfile();
        Yasound.App.Router.navigate('legal/', {
            trigger: true
        });
        return false;
    },

    onLogout: function (e) {
        e.preventDefault();
        window.location = Yasound.App.root + 'logout';
        return false;
    }

});
