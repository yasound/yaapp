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
    /**
     * Sound engine initialization
     */
    if (g_sound_player == 'soundmanager') {
        Yasound.App.player = Yasound.Player.SoundManager();
    } else if (g_sound_player == 'deezer') {
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
            var container = $('#webapp-container-parent');
            var footer = $('#footer');
            var documentHeight = container.height() + footer.height() + 12;
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
            "radio/:uuid": "radio",
            "search/:query/": "search",
            "favorites/": "myFavorites",
            "favorites/:genre/": "myFavorites",
            "radios/": "myRadios",
            "radios/new/": "newRadio",
            "top/": "top",
            "top/:genre/": "top",
            "users/": "users",
            "profile/:username/": "profile",
            "profile/:username/favorites/": "userFavorites",
            "profile/:username/friends/": "userFriends",
            "profile/:username/followers/": "userFollowers",
            "profile/:username/radios/": "userRadios",
            "profile/:username/likes/": "userLikes",
            "settings/": "settings",
            "friends/": "myFriends",
            "notifications/": "notifications",
            "radio/:uuid/programming/": "programming",
            "radio/:uuid/edit/": "editRadio",
            "radio/:uuid/listeners/": "listeners",
            "signup/": "signup",
            "signup/*args": "signup",
            "login/": "login",
            "radio/:uuid/*args": "radio",
            "gifts/": "gifts",
            "legal/": "legal",
            "contact/": "contact",
            "about/": "about",
            "help/": "help",
            "jobs/": "jobs",
            "press/": "press",
            "selection/:genre/": "index",
            "*args": "index"
        },
        initialize: function() {
            if (Yasound.App.appName == 'deezer') {
                this.bind('all', this._updateDeezerCanvas);
            }
            return this.bind('all', this._trackPageview);
        },

        _updateDeezerCanvas: function () {
            DZ.ready(function(){
                DZ.canvas.setSize(1325);
            });
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
                'uuid': uuid,
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
                if (this.commonContext.teaserView) {
                    this.commonContext.teaserView.slideUp();
                }
            }
            this.alreadyLoaded = true;

            if (!this.radioContext) {
                var that = this;
                this.radioContext = {
                    currentSong: new Yasound.Data.Models.CurrentSong()
                };

                this.radioContext.currentSongView = new Yasound.Views.CurrentSong({
                    model: this.radioContext.currentSong,
                    radio: this.currentRadio,
                    el: $('#player')
                }).render();
                this.radioContext.currentSongView.radio = this.currentRadio;

                this.currentRadio.on('change:id', function (model, id) {
                    var origin = model.get('origin');
                    model.currentSong = that.radioContext.currentSong;
                    that.radioContext.currentSong.set('radioId', id);
                    that.radioContext.currentSong.setOrigin(origin);
                    that.radioContext.currentSong.fetch();
                    that.radioContext.currentSong.set('buy_link', '/api/v1/radio/' + id + '/buy_link/');
                    that.pushManager.monitorRadio(model);
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
            $('#webapp-container').append("<div class='container' id='webapp-content'/>");
            $('html, body').scrollTop(0);


            if (Yasound.App.showWelcomePopup) {
                // TODO : remove
                Yasound.App.showWelcomePopup = false;
            }

            this.commonContext.selectedGenreView.setVisible(showSelectedGenre, selectedMenu);

        },

        pushManager: new Yasound.App.PushManager({
            enablePush: g_enable_push
        }),

        // build common stuff for every views (radio)
        buildCommonContext: function (selectedMenu) {
            if (!this.commonContext) {
                this.commonContext = {};
                this.commonContext.errorHandler = new Yasound.App.ErrorHandler().render();
                this.commonContext.streamFunction = function (model, stream_url) {
                    Yasound.App.player.setBaseUrl(model, stream_url);
                };
                this.commonContext.mobileMenuView = new Yasound.Views.MobileMenu({}).render();
                this.commonContext.mobileMenuLogoView = new Yasound.Views.MobileMenuLogo({}).render();
                this.commonContext.searchMenuView = new Yasound.Views.SearchMenu({}).render();
                this.commonContext.connectedUsersView = new Yasound.Views.ConnectedUsers({}).render();

                if (Yasound.App.appName !== 'deezer') {
                    this.commonContext.publicStatsView = new Yasound.Views.PublicStats({});
                }

                // if (!Yasound.App.userAuthenticated) {
                //     if (!cookies.get('hideteaser')) {
                //         this.commonContext.teaserView = new Yasound.Views.Teaser({}).render();
                //     }
                // }
                this.commonContext.teaserView = new Yasound.Views.Teaser({}).render();
                this.currentRadio.on('change:stream_url', this.commonContext.streamFunction);


                this.commonContext.subMenuView = new Yasound.Views.SubMenu({
                    el: '#submenu-container',
                    model: this.radioContext.currentSong,
                    radio: this.currentRadio
                }).render();
                this.commonContext.selectedGenreView = new Yasound.Views.SelectedGenre({}).render();
            }
            this.commonContext.subMenuView.selectMenu(selectedMenu);
        },

        index: function (genre) {
            this.clearView('selection');

            if (genre) {
                this.commonContext.subMenuView.setCurrentGenre('style_' + genre);
            }

            var genre =  this.commonContext.subMenuView.currentGenre();

            this.currentView = new Yasound.Views.HomePage({
                el: '#webapp-content'
            }).render(genre);

            Yasound.Utils.enableFX();
        },

        settings: function () {
            this.clearView();

            this.currentView = new Yasound.Views.SettingsPage({
                el: '#webapp-content'
            }).render();
        },

        notifications: function () {
            this.clearView();

            this.currentView = new Yasound.Views.NotificationsPage({
                el: '#webapp-content'
            }).render();
        },

        programming: function (uuid) {
            this.clearView('my-radios');
            this.currentView = new Yasound.Views.ProgrammingPage({
                el: '#webapp-content'
            }).render(uuid);
        },

        editRadio: function (uuid) {
            this.clearView('my-radios');
            this.currentView = new Yasound.Views.EditRadioPage({
                el: '#webapp-content'
            }).render(uuid);
        },

        // search page
        search: function (query) {
            this.clearView('search');

            this.currentView = new Yasound.Views.SearchPage({
                el: '#webapp-content'
            }).render(query);
        },

        // owner favorites page
        myFavorites: function (genre) {
            this.clearView('favorites');

            if (genre) {
                this.commonContext.subMenuView.setCurrentGenre('style_' + genre);
            }

            var genre =  this.commonContext.subMenuView.currentGenre();

            this.currentView = new Yasound.Views.FavoritesPage({
                el: '#webapp-content'
            }).render(genre);
        },

        userFavorites: function (username) {
            this.clearView();
            this.currentView = new Yasound.Views.UserFavoritesPage({
                el: '#webapp-content'
            }).render('', username);
        },

        // top radios
        top: function (genre) {
            this.clearView('top');

            if (genre) {
                this.commonContext.subMenuView.setCurrentGenre('style_' + genre);
            }
            var genre =  this.commonContext.subMenuView.currentGenre();
            this.currentView = new Yasound.Views.TopRadiosPage({
                el: '#webapp-content'
            }).render(genre);
        },

        // owner friends page
        myFriends: function () {
            this.clearView('friends');

            this.currentView = new Yasound.Views.FriendsPage({
                el: '#webapp-content'
            }).render();
        },

        // user's friends
        userFriends: function (username) {
            this.clearView();

            this.currentView = new Yasound.Views.UserFriendsPage({
                el: '#webapp-content'
            }).render(username);
        },

        userFollowers: function (username) {
            this.clearView();

            this.currentView = new Yasound.Views.UserFollowersPage({
                el: '#webapp-content'
            }).render(username);
        },

        // user's radios
        userRadios: function (username) {
            this.clearView();

            this.currentView = new Yasound.Views.UserRadiosPage({
                el: '#webapp-content'
            }).render('', username);
        },

        // user's likes
        userLikes: function (username) {
            this.clearView();

            this.currentView = new Yasound.Views.UserLikesPage({
                el: '#webapp-content'
            }).render(username);
        },

        // radio listeners
        listeners: function (uuid) {
            this.clearView();

            this.currentView = new Yasound.Views.ListenersPage({
                el: '#webapp-content'
            }).render(uuid);
        },

        // all users page
        users: function () {
            this.clearView();

            var users = new Yasound.Data.Models.Users({});

            this.currentView = new Yasound.Views.UsersPage({
                collection: users,
                el: '#webapp-content'
            }).render();
        },

        // profile page
        profile: function (username) {
            this.clearView();

            this.currentView = new Yasound.Views.ProfilePage({
                model: new Yasound.Data.Models.User({username:username}),
                el: '#webapp-content'
            });
            this.currentView.model.fetch();
        },

        // radio details page
        radio: function (uuid) {
            Yasound.App.player.setAutoplay(true);
            this.clearView();

            this.currentView = new Yasound.Views.RadioPage({
                model: this.currentRadio,
                el: '#webapp-content'
            });

            this.radioContext.radioUUID = 0;
            this.setCurrentRadioUUID(uuid);

        },

        myRadios: function () {
            this.clearView('my-radios');

            var genre =  this.commonContext.subMenuView.currentGenre();

            this.currentView = new Yasound.Views.MyRadiosPage({
                el: '#webapp-content'
            }).render(genre);
        },

        newRadio: function () {
            this.clearView('my-radios');

            this.currentView = new Yasound.Views.NewRadioPage({
                el: '#webapp-content'
            }).render();
        },

        legal: function () {
            return this.staticPage('legal');
        },

        contact: function () {
            return this.staticPage('contact');
        },

        jobs: function () {
            return this.staticPage('jobs');
        },

        press: function () {
            return this.staticPage('press');
        },

        about: function () {
            return this.staticPage('about');
        },

        help: function () {
            return this.staticPage('help');
        },

        tutorial: function () {
            new Yasound.Views.TutorialWindow().render();
            return this.index();
        },

        staticPage: function(page) {
            this.clearView();

            page = page.replace('/', '');

            this.currentView = new Yasound.Views.StaticPage({
                el: '#webapp-content'
            }).render(page);
        },

        signup: function() {
            this.clearView();

            this.currentView = new Yasound.Views.SignupPage({
                el: '#webapp-content'
            }).render();
        },

        login: function() {
            this.clearView();

            this.currentView = new Yasound.Views.LoginPage({
                el: '#webapp-content'
            }).render();
        },

        gifts: function() {
            this.clearView();

            this.currentView = new Yasound.Views.GiftsPage({
                el: '#webapp-content'
            }).render();
        }


    });

    // Global object, useful to navigate in views
    Yasound.App.Router = new Yasound.App.Workspace();

    Yasound.App.player.init(function () {
        Backbone.history.start({
            pushState: true,
            root: Yasound.App.root,
            silent: false
        });
        $('#loading-mask').hide();
        $('#loading').hide();
    });
});