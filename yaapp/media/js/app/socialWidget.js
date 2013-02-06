/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
$(document).ready(function () {
    Namespace('Yasound.App');

    window.reload = function () {
        window.location = g_root;
    };

    // global initializations
    Yasound.App.FacebookShare = {
        picture: g_facebook_share_picture,
        link: g_facebook_share_link
    };

    Yasound.App.userAuthenticated = g_authenticated;
    Yasound.App.username = g_username;
    Yasound.App.page = g_page;
    Yasound.App.isMobile = false;
    Yasound.App.hasRadios = g_has_radios;
    Yasound.App.stickyViews = [];
    Yasound.App.uploadCount = 0;
    Yasound.App.root = g_root;
    Yasound.App.appName = g_app_name;
    Yasound.App.defaultRadioUUID = g_default_radio_uuid;
    Yasound.App.ignoreRadioCookie = g_ignore_radio_cookie;
    Yasound.App.showWelcomePopup = g_show_welcome_popup;
    Yasound.App.hd = g_hd_enabled;
    Yasound.App.RADIO_ORIGIN_YASOUND = 0; // constant, radio.origin=0 means radioways radio
    Yasound.App.RADIO_ORIGIN_RADIOWAYS = 1; // constant, radio.origin=1 means radioways radio
    Yasound.App.LanguageCode = g_language_code;
    Yasound.App.announcementId = g_announcement_id;
    Yasound.App.CONTENT_EL = '.content';
    Yasound.App.CONTENT_HTML = "<div class='content'><div class='container-fluid content-zone last'><div class='row-fluid'><div class='span12'><img class='loading-mask' src='/media/images/loading-white.gif'/></div></div></div></div>";

    if (cookies.get('radio') && !Yasound.App.ignoreRadioCookie) {
        Yasound.App.defaultRadioUUID = cookies.get('radio');
    }

    if( /Android|webOS|iPhone|iPad|iPod|BlackBerry/i.test(navigator.userAgent) ) {
        Yasound.App.isMobile = true;
    }
    if (g_bootstrapped_data) {
        Yasound.Utils.disableFX();
    } else {
        Yasound.Utils.enableFX();
    }

    Yasound.App.waitForSoundManager = false;

    if ($.browser.msie) {
        if ($.browser.version == '8.0' || $.browser.version == '7.0' || $.browser.version == '6.0') {
            g_enable_push = false;
        }
    }


    $.subscribe('/programming/upload_started', function () {
        Yasound.App.uploadCount = Yasound.App.uploadCount + 1;
    });
    $.subscribe('/programming/upload_stopped', function () {
        Yasound.App.uploadCount = Yasound.App.uploadCount - 1;
    });
    $.subscribe('/programming/upload_finished', function () {
        Yasound.App.uploadCount = Yasound.App.uploadCount - 1;
    });
    $.subscribe('/programming/upload_failed', function () {
        Yasound.App.uploadCount = Yasound.App.uploadCount - 1;
    });

    $(window).bind('beforeunload', function() {
        if (Yasound.App.uploadCount > 0) {
            return gettext('Unfinished uploads are pending, do you really want to leave Yasound?');
        }
    });
    var $win = $(window);
    $.fn.scrollBottom = function() {
        return $(document).height() - this.scrollTop() - this.height();
    };
    $win.scroll(function () {
        if ($win.scrollTop() > 500 && $win.scrollBottom()!==0) {
            $('#scroll-top-container').fadeIn(200);
        } else if ($win.scrollTop() < 500 ) {
            $('#scroll-top-container').fadeOut(200);
        }
    });
    $('#scroll-top-container').click(function (e) {
        e.preventDefault();
        $('html, body').animate({scrollTop: 0}, 400);
        return false;
    });


    /**
     * component initalization
     */
    $('.dropdown-toggle').dropdown();

    $('#btn-webapp').click(function(e) {
        e.preventDefault();
        Yasound.App.Router.navigate('', {
            trigger: true
        });
    });
    $('#btn-legal').click(function(e) {
        e.preventDefault();
        Yasound.App.Router.navigate('legal/', {
            trigger: true
        });
    });
    $('#btn-contact').click(function(e) {
        e.preventDefault();
        Yasound.App.Router.navigate('contact/', {
            trigger: true
        });
    });
    $('#btn-about').click(function(e) {
        e.preventDefault();
        Yasound.App.Router.navigate('about/', {
            trigger: true
        });
    });
    $('#btn-help').click(function(e) {
        e.preventDefault();
        Yasound.App.Router.navigate('help/', {
            trigger: true
        });
    });
    $('#btn-press').click(function(e) {
        e.preventDefault();
        Yasound.App.Router.navigate('press/', {
            trigger: true
        });
    });
    $('#btn-jobs').click(function(e) {
        e.preventDefault();
        Yasound.App.Router.navigate('jobs/', {
            trigger: true
        });
    });


    Backbone.View.prototype.close = function () {
        if (this.sticky) {
            this.el.parentNode.removeChild(this.el);
            Yasound.Utils.saveStickyView(this.stickyKey(), this);
        } else {
            if (this.beforeRemove) {
                this.beforeRemove();
            }
            this.remove();
            this.unbind();
            if (this.onClose) {
                this.onClose();
            }
        }
    };

    if (Yasound.App.appName === 'live') {
        var sessionid = cookies.get('sessionid');
        if (Yasound.App.userAuthenticated && sessionid) {
            Yasound.NativeBridge.Call('loginCompleted', sessionid);
        }
    }

    /**
     * Sound engine initialization
     */
    if (g_sound_player === 'soundmanager') {
        Yasound.App.player = Yasound.Player.SoundManager();
        Yasound.App.instantPlayer = Yasound.Player.InstantPlayer();
    } else if (g_sound_player === 'deezer') {
        Yasound.App.player = Yasound.Player.Deezer();
    }

    if (Yasound.App.appName === 'deezer') {
        //g_enable_push = false;

        $.ajaxPrefilter( function( options ) {
            if (options.url.indexOf('/api/') === 0) {
                options.url = "https://yasound.com" + options.url;
                options.xhrFields = {
                    withCredentials: true
               };
            }
        });

        $(document).on('DOMSubtreeModified', function() {
            var container = $('#main-content');
            var footer = $('#footer');
            var documentHeight = container.height() + footer.height() + 112;
            DZ.ready(function() {
                DZ.canvas.setSize(documentHeight);
            });
        });
    }

    $('#hommage a').on('click', function (e) {
        e.preventDefault();
        var uuid = $(e.target).data('uuid');
        Yasound.App.Router.navigate('radio/' + uuid + '/', {
            trigger: true
        });
        $('#anon-alert').hide();
    });

    /**
     * Application controller
     */
    Yasound.App.Workspace = Backbone.Router.extend({
        routes: {
            "": "index",
            "signup/": "signup",
            "signup/*args": "signup",
            "login/": "login",
            "lostpassword/": "passreset",
            "*args": "index"
        },

        initialize: function() {
            if (Yasound.App.appName == 'deezer') {
                this.bind('all', this._updateDeezerCanvas);
            }
            return this.bind('all', this._trackPageview);
        },

        _trackPageview: function() {
            var loc = window.location;
            var proto = loc.protocol;
            var host = loc.host;
            var begin = proto + '//' + host;
            var full = loc.href;
            var url = loc.href.substring(begin.length);
            return _gaq.push(['_trackPageview', url]);
        },

        currentRadio: new Yasound.Data.Models.Radio({
            uuid: 0
        }),
        currentView: undefined,

        setCurrentRadioUUID: function (uuid) {
            if (Yasound.App.userAuthenticated) {
                this.currentRadio.disconnect();
            }
            this.currentRadio.set({
                'slug': uuid,
                'id': 0
            }, {
                silent: true
            // do not send 'change' event now, fetch will do it right after
            });

            cookies.set('radio', uuid);

            var radio = this.currentRadio;
            this.currentRadio.fetch({
                success: function () {
                    if (Yasound.App.userAuthenticated) {
                        radio.connect();
                    }
                }
            });
        },

        // this function must be called between every routes
        clearView: function (selectedMenu) {
            var showSelectedGenre = false;
            if (selectedMenu === 'favorites' ||
                selectedMenu === 'selection' ||
                selectedMenu === 'top') {
                showSelectedGenre = true;
            }

            if (this.alreadyLoaded) {
                g_bootstrapped_data = undefined;
                Yasound.Utils.enableFX();
                $('#main-content .content').remove();
                $('#main-content').append(Yasound.App.CONTENT_HTML);
            }
            this.alreadyLoaded = true;

            if (!this.radioContext) {
                var that = this;
                this.radioContext = {
                    currentSong: new Yasound.Data.Models.CurrentSong()
                };

                this.currentRadio.on('change:id', function (model, id) {
                    var origin = model.get('origin');
                    model.currentSong = that.radioContext.currentSong;
                    that.radioContext.currentSong.set('radioId', id);
                    that.radioContext.currentSong.setOrigin(origin);
                    that.radioContext.currentSong.fetch();
                    that.radioContext.currentSong.set('buy_link', '/api/v1/radio/' + id + '/buy_link/');
                    that.pushManager.monitorRadio(model);
                    $.publish('/current_radio/change', model);
                });

                this.radioContext.radioUUID = 0;
                this.setCurrentRadioUUID(Yasound.App.defaultRadioUUID);
            }

            this.buildCommonContext(selectedMenu);
            if (this.currentView) {
                this.currentView.reset();
                this.currentView.close();
                this.currentView = undefined;
            }
            $('html, body').scrollTop(0);


            if (Yasound.App.showWelcomePopup) {
                // TODO : remove
                Yasound.App.showWelcomePopup = false;
            }
        },

        pushManager: new Yasound.App.PushManager({
            enablePush: g_enable_push
        }),

        // build common stuff for every views (radio)
        buildCommonContext: function (selectedMenu) {
            if (!this.commonContext) {
                this.commonContext = {};
                this.commonContext.errorHandler = new Yasound.App.ErrorHandler().render();
            }
        },

        index: function () {
            this.clearView();

            this.currentView = new Yasound.Views.RadioPage({
                model: this.currentRadio,
                el: Yasound.App.CONTENT_EL
            });

            this.radioContext.radioUUID = 0;
            this.setCurrentRadioUUID(g_default_radio_uuid);

            Yasound.Utils.enableFX();
        },


        signup: function() {
            this.clearView();

            this.currentView = new Yasound.Views.SignupPage({
                el: Yasound.App.CONTENT_EL
            }).render();
        },

        login: function() {
            this.clearView();

            this.currentView = new Yasound.Views.LoginPage({
                el: Yasound.App.CONTENT_EL
            }).render();
        },

        passreset: function() {
            this.clearView();

            this.currentView = new Yasound.Views.PassResetPage({
                el: Yasound.App.CONTENT_EL
            }).render();
        }

    });

    // Global object, useful to navigate in views
    Yasound.App.Router = new Yasound.App.Workspace();

    Backbone.history.start({
        pushState: true,
        root: Yasound.App.root,
        silent: false
    });
    $('#loading-mask').hide();
    $('#loading').hide();
});