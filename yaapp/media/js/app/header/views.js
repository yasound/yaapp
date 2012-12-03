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
        'click #profile-menu .logout': 'onLogout',
        'submit #login-form': 'submitLogin'
    },

    initialize: function () {
        _.bindAll(this, 'render', 'hidePopupProfile', 'onNotification', 'onNotificationUnreadCount');
        if (Yasound.App.Router.pushManager.enablePush) {
            Yasound.App.Router.pushManager.on('notification', this.onNotification);
            Yasound.App.Router.pushManager.on('notification_unread_count', this.onNotificationUnreadCount);
        }
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

    onNotificationUnreadCount: function(data) {
        var unreadCount = data.count;
        var el = $('.count-badge', this.el);
        el.html(unreadCount);
        if (unreadCount > 0) {
            el.removeClass('hidden');
        } else {
            el.addClass('hidden');
        }
    }
});
