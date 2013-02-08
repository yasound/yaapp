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
        'click #search-symbol': 'searchWithSymbol',
        'click .btn-register': 'onRegister',
        'click #profile-menu .my-profile': 'onMyProfile',
        'click #profile-menu .my-radios': 'onMyRadios',
        'click #profile-menu .my-settings': 'onMySettings',
        'click #profile-menu .logout': 'onLogout',
        'click #notifications-menu a': 'onNotifications',
        'click #brand-logo a.btn-logo': 'onHome',
        'click .btn-envelope': 'refreshNotificationsDigest',
        'click .btn-hd': 'refreshHD',
        'click #brand-menu .blog': 'onBlog',
        'click #brand-menu .about': 'onAbout',
        'click #brand-menu .faq': 'onFaq',
        'click #brand-menu .legal': 'onLegal',
        'click #brand-menu .press': 'onPress',
        'click #brand-menu .jobs': 'onJobs',
        'click .lost-password': 'onPassReset',
        'submit #login-form': 'submitLogin'
    },

    initialize: function () {
        _.bindAll(this,
            'render',
            'hidePopupProfile',
            'onNotification',
            'onNotificationUnreadCount',
            'hidePopupNotifications',
            'hidePopupSignup'
        );

        if (Yasound.App.Router.pushManager.enablePush) {
            Yasound.App.Router.pushManager.on('notification', this.onNotification);
            Yasound.App.Router.pushManager.on('notification_unread_count', this.onNotificationUnreadCount);
        }
    },

    onClose: function () {
    },

    render: function () {
        this.notificationsDigestView = new Yasound.Views.NotificationsDigest({
            el: '#notifications-menu'
        });

        this.giftsDigestView = new Yasound.Views.GiftsDigest({
            el: '#gifts-menu'
        });


        var isIpad = (navigator.userAgent.match(/iPhone/i)) || (navigator.userAgent.match(/iPod/i)) || (navigator.userAgent.match(/iPad/i));
        var f = jQuery(".jeu-concours").fancybox({
            'speedIn' : 200,
            'speedOut' : 200,
            'padding': 0,
            'margin': 0,
            'width' : 728,
            'height' : 392,
            'scrolling': 'no',
            'overlayShow' : true,
            onStart : function() {
                if (isIpad) {
                    jQuery('object').hide();
                }
            },
            onClosed : function() {
                if (isIpad) {
                    jQuery('object').show();
                }
            }
        });

        jQuery(".jeu-concours").trigger('click');

        jQuery(window).resize(function() {
            jQuery.fancybox.resize();
        });


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

    searchWithSymbol: function (e) {
        e.preventDefault();
        var value = $('#search-input', this.el).val();
        if (!value) {
            return;
        }

        $('#search-input', this.el).val('');
        Yasound.App.Router.navigate("search/" + value + '/', {
            trigger: true
        });
    },

    hidePopupProfile: function () {
        $('#profile-menu').parent().removeClass('open');
    },

    hidePopupNotifications: function () {
        $('#notifications-menu').parent().removeClass('open');
    },

    hidePopupSignup: function () {
        $('#signup-menu').parent().removeClass('open');
    },

    hidePopupBrand: function () {
        $('#brand-menu').parent().removeClass('open');
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

    onBlog: function (e) {
        e.preventDefault();
        this.hidePopupBrand();
        Yasound.App.Router.navigate('blog/', {
            trigger: true
        });
        return false;
    },

    onAbout: function (e) {
        e.preventDefault();
        this.hidePopupBrand();
        Yasound.App.Router.navigate('about/', {
            trigger: true
        });
        return false;
    },

    onFaq: function (e) {
        e.preventDefault();
        this.hidePopupBrand();
        Yasound.App.Router.navigate('faq/', {
            trigger: true
        });
        return false;
    },

    onLegal: function (e) {
        e.preventDefault();
        this.hidePopupBrand();
        Yasound.App.Router.navigate('legal/', {
            trigger: true
        });
        return false;
    },

    onPress: function (e) {
        e.preventDefault();
        this.hidePopupBrand();
        Yasound.App.Router.navigate('press/', {
            trigger: true
        });
        return false;
    },

    onJobs: function (e) {
        e.preventDefault();
        this.hidePopupBrand();
        Yasound.App.Router.navigate('jobs/', {
            trigger: true
        });
        return false;
    },

    onPassReset: function (e) {
        e.preventDefault();
        this.hidePopupSignup();
        Yasound.App.Router.navigate('lostpassword/', {
            trigger: true
        });
        return false;
    },

    onHome: function (e) {
        e.preventDefault();
        if ($('#brand-menu').parent().hasClass('open')) {
            this.hidePopupBrand();
            Yasound.App.Router.navigate('/', {
                trigger: true
            });
            return false;
        }
        return true;
    },

    onLogout: function (e) {
        e.preventDefault();
        window.location = Yasound.App.root + 'logout';
        return false;
    },

    submitLogin: function(e) {
        e.preventDefault();
        var form = $('#login-form', this.el);
        $('.error-msg', form).remove();
        $('input').removeClass('error');

        var url = form.attr('action');
        $.post(url, form.serializeArray(), function(data) {
            var success = data.success;
            if (!data.success) {
                colibri(gettext('Login error'));
                var errors = data.errors;
                if (errors) {
                    _.each(errors, function(value, key) {
                        var $input = $('input[name=' + key + ']', form);
                        $input.addClass('error');
                        $input.after('<div class="error-msg">' + value + '</div>');
                    });
                }
            } else {
                window.location = Yasound.App.root;
            }
        }).error(function() {
            colibri(gettext('Error while login in', 'colibri-error'));
        });
    },

    onNotification: function(notification) {
        colibri(gettext('New notification received'));
    },

    onNotifications: function(e) {
        e.preventDefault();
        this.hidePopupNotifications();
        Yasound.App.Router.navigate('notifications/', {
            trigger: true
        });
    },

    onNotificationUnreadCount: function(data) {
        var unreadCount = data.count;
        var el = $('.count-badge', this.el);
        el.html(unreadCount);
        if (unreadCount > 0) {
            el.removeClass('hidden');
        } else {
            el.addClass('hidden');
        }
    },

    refreshNotificationsDigest: function (e) {
        e.preventDefault();
        this.notificationsDigestView.render();
    },

    refreshHD: function (e) {
        e.preventDefault();
        this.giftsDigestView.render();
    }
});
