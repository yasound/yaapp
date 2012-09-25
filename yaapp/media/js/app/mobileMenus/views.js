/*
 * jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true,
 * evil: true, undef: true, white: true, newcap: true
 */
/* extern Ext, $ */

Namespace('Yasound.Views');

Yasound.Views.BaseMobileMenu = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this, 'render', 'toggleMenu');
        $(this.menuButton).on('click', this.toggleMenu);
    },

    onClose: function() {
    },

    render: function() {
        return this;
    },

    toggleMenu: function(e) {
        e.preventDefault();
        var menu = this.$el;
        $('html, body').animate({
            scrollTop: 0
        }, 400);
        if (menu.is(':visible')) {
            $('#webapp-content').show();
        } else {
            menu.siblings().hide();
        }
        menu.toggle();
    },

    goTo: function(e, url) {
        e.preventDefault();
        Yasound.App.Router.navigate(url, {
            trigger: true
        });
        this.$el.hide();
        $('#webapp-content').show();
    }

});
/**
 * Settings Menu
 */

Yasound.Views.MobileMenu = Yasound.Views.BaseMobileMenu.extend({
    el: '#mobile-menu-content',
    menuButton: '#mobile-menu-btn',

    events: {
        "click #phone-menu-profile": "myProfile",
        "click #phone-menu-myradios": "myRadios",
        "click #phone-menu-notifications": "notifications",
        "click #phone-menu-gifts": "gifts",
        "click #phone-menu-mysettings": "mySettings",
        "click #phone-menu-signout": "logout"
    },

    myRadios: function(e) {
        this.goTo(e, '/radios/');
    },

    myProfile: function(e) {
        this.goTo(e, '/profile/' + Yasound.App.username + '/');
    },

    mySettings: function(e) {
        this.goTo(e, '/settings/');
    },

    notifications: function(e) {
        this.goTo(e, '/notifications/');
    },

    gifts: function(e) {
        this.goTo(e, 'gifts/');
    },

    logout: function(e) {
        window.location = Yasound.App.root + 'logout';
    }
});

/**
 * Logo Menu
 */

Yasound.Views.MobileMenuLogo = Yasound.Views.BaseMobileMenu.extend({
    el: '#mobile-menu-content-logo',
    menuButton: '#mobile-menu-btn-logo',

    events: {
        "click #phone-menu-selection": "selection",
        "click #phone-menu-top": "top",
        "click #phone-menu-myfriends": "friends",
        "click #phone-menu-favorites": "favorites"
    },

    selection: function(e) {
        this.goTo(e, '/');
    },
    top: function(e) {
        this.goTo(e, '/top/');
    },
    friends: function(e) {
        this.goTo(e, '/friends/');
    },
    favorites: function(e) {
        this.goTo(e, '/favorites/');
    }
});

/**
 * Share Menu
 */

Yasound.Views.MobileMenuShare = Yasound.Views.BaseMobileMenu.extend({
    el: '#mobile-menu-content-share',
    menuButton: '#responsive-share-btn',

    render: function (data) {
        var that = Yasound.Views.MobileMenuShare.__super__.render.apply(this);
        $('#phone-menu-buy', this.el).attr('href', data.buy_link);
        return that;
    }
});