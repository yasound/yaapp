/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
$(document).ready(function () {
    Namespace('Yasound.App');

    // global initializations
    Yasound.App.FacebookShare = {
        picture: g_facebook_share_picture,
        link: g_facebook_share_link
    };
    
    Yasound.App.userAuthenticated = g_authenticated;
    Yasound.App.username = g_username;
    Yasound.App.isMobile = false;
    if( /Android|webOS|iPhone|iPad|iPod|BlackBerry/i.test(navigator.userAgent) ) {
        Yasound.App.isMobile = true;
    }    
    
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
    
    Backbone.View.prototype.close = function () {
        this.remove();
        this.unbind();
        if (this.onClose) {
            this.onClose();
        }
    };


    soundManager.url = '/media/js/sm/swf/'; // directory where SM2 .SWFs
    soundManager.preferFlash = true;
    soundManager.useHTML5Audio = true;
    soundManager.debugMode = true;
    soundManager.useFlashBlock = true;
    Yasound.App.MySound = undefined;

    Yasound.App.SoundConfig = {
        id: 'yasoundMainPlay',
        url: undefined,
        autoPlay: true,
        autoLoad: true,
        volume: 100, // volume is saved across different streams
        stream: true
    };

    // called in case of problem with flash player (flashblock for instance)
    soundManager.ontimeout(function () {
        if (!(typeof Yasound.App.MySound === "undefined")) {
            Yasound.App.MySound.destruct();
        }
        Yasound.App.MySound = undefined;
        $('#play i').removeClass('icon-stop').addClass('icon-play');
    });

    /**
     * Application controller
     */
    Yasound.App.Workspace = Backbone.Router.extend({
        routes: {
            "": "index",
            "radio/:uuid/*args": "radio",
            "radio/:uuid": "radio",
            "search/:query/": "search",
            "favorites/": "favorites",
            "top/": "top",
            "users/": "users",
            "profile/:username/": "profile",
            "settings/": "settings",
            "friends/": "friends",
            "notifications/": "notifications",
            "programming/": "programming",
            "legal/": "legal",
            "contact/": "contact",
            "*args": "index"
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
        clearView: function (showSubMenu) {
            this.buildCommonContext(showSubMenu);
            if (this.currentView) {
                this.currentView.reset();
                this.currentView.close();
                this.currentView = undefined;
            }
            $('#webapp-container').append("<div class='container' id='webapp-content'/>");
            $('body').scrollTop(0);
        },

        pushManager: new Yasound.App.PushManager({
            enablePush: g_enable_push
        }),

        // build common stuff for every views (radio)
        buildCommonContext: function (showSubMenu) {
            if (!this.commonContext) {
                this.commonContext = {};
                this.commonContext.streamFunction = function (model, stream_url) {
                    if (!(typeof Yasound.App.MySound === "undefined")) {
                        Yasound.App.MySound.destruct();
                    }
                    Yasound.App.SoundConfig.url = stream_url;
                    Yasound.App.MySound = soundManager.createSound(Yasound.App.SoundConfig);
                };

                this.commonContext.userMenuView = new Yasound.Views.UserMenu({}).render();
                this.commonContext.searchMenuView = new Yasound.Views.SearchMenu({}).render();
                this.commonContext.connectedUsersView = new Yasound.Views.ConnectedUsers({}).render();
                this.commonContext.publicStatsView = new Yasound.Views.PublicStats({});
                this.currentRadio.on('change:stream_url', this.commonContext.streamFunction);
            }
            
            if (!showSubMenu && this.commonContext.subMenuView) {
                this.commonContext.subMenuView.reset();
                this.commonContext.subMenuView.close();
                this.commonContext.subMenuView = undefined;
            }
            
            if (showSubMenu && !this.commonContext.subMenuView) {
                $('#submenu-container').append("<div id='submenu-content'/>");
                this.commonContext.subMenuView = new Yasound.Views.SubMenu({
                    el: '#submenu-content'
                }).render();
            }
        },
        
        index: function () {
            this.clearView(true);

            var genre =  this.commonContext.subMenuView.currentGenre();
            this.currentView = new Yasound.Views.HomePage({
                el: '#webapp-content'
            }).render(genre);
            
            this.commonContext.subMenuView.selectMenu('selection');
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

        programming: function () {
            this.clearView();

            this.currentView = new Yasound.Views.ProgrammingPage({
                el: '#webapp-content'
            }).render();
        },

        // search page
        search: function (query) {
            this.clearView(true);

            var radioSearchResults = new Yasound.Data.Models.RadioSearchResults({});
            radioSearchResults.setQuery(query);

            this.currentView = new Yasound.Views.SearchPage({
                el: '#webapp-content',
                collection: radioSearchResults
            }).render();
        },

        // owner favorites page
        favorites: function () {
            this.clearView(/* showSubMenu = */ true);

            var genre =  this.commonContext.subMenuView.currentGenre();

            this.currentView = new Yasound.Views.FavoritesPage({
                el: '#webapp-content'
            }).render(genre);
            this.commonContext.subMenuView.selectMenu('favorites');
        },
        
        // top radios
        top: function () {
            this.clearView(/* showSubMenu = */ true);

            var genre =  this.commonContext.subMenuView.currentGenre();

            this.currentView = new Yasound.Views.TopRadiosPage({
                el: '#webapp-content',
            }).render(genre);
            this.commonContext.subMenuView.selectMenu('top');
        },

        // owner friends page
        friends: function () {
            this.clearView(true);

            var friends = new Yasound.Data.Models.Friends({});

            this.currentView = new Yasound.Views.FriendsPage({
                collection: friends,
                el: '#webapp-content'
            }).render();
            this.commonContext.subMenuView.selectMenu('friends');
        },

        // all users page
        users: function () {
            this.clearView(/* showSubMenu = */ false);

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
            }).render();
        },

        // radio details page
        radio: function (uuid) {
            this.clearView();

            if (!this.radioContext) {
                var that = this;
                this.radioContext = {
                    currentSong: new Yasound.Data.Models.CurrentSong()
                };

                this.radioContext.currentSongView = new Yasound.Views.CurrentSong({
                    model: this.radioContext.currentSong,
                    radio: this.currentRadio,
                    el: $('#player')
                });
                this.radioContext.currentSongView.radio = this.currentRadio;

                this.currentRadio.on('change:id', function (model, id) {
                    model.currentSong = that.radioContext.currentSong;
                    that.radioContext.currentSong.set('radioId', id);
                    that.radioContext.currentSong.fetch();
                    that.radioContext.currentSong.set('buy_link', '/api/v1/radio/' + id + '/buy_link/');
                    that.pushManager.monitorRadio(model);
                });
            }

            this.currentView = new Yasound.Views.RadioPage({
                model: this.currentRadio,
                el: '#webapp-content'
            }).render();

            this.radioContext.radioUUID = 0;
            this.setCurrentRadioUUID(uuid);
        },
        
        legal: function() {
            this.clearView();
            this.currentView = new Yasound.Views.Static.LegalPage({
                el: '#webapp-content'
            }).render();
        },
        
        contact: function() {
            this.clearView();
            this.currentView = new Yasound.Views.Static.ContactPage({
                el: '#webapp-content'
            }).render();
        }
    });

    // Global object, useful to navigate in views
    Yasound.App.Router = new Yasound.App.Workspace();

    soundManager.onready(function () {
        Backbone.history.start({
            pushState: true,
            root: '/app/',
            silent: false
        });
    });

});