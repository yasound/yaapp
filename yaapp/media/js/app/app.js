$(document).ready(function() {
    Namespace('Yasound.App');

    
    /**
     * component initalization
     */
    $('.dropdown-toggle').dropdown();

    Backbone.View.prototype.close = function(){
        this.remove();
        this.unbind();
        if (this.onClose) {
            this.onClose();
        }
    }

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
    soundManager.ontimeout(function() {
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
            "radio/:uuid": "radio",
            "search/:query": "search",
            "favorites/": "favorites"
        },

        currentRadio: new Yasound.Data.Models.Radio({
            uuid: 0
        }),
        currentView: undefined,

        setCurrentRadioUUID: function(uuid) {
            this.currentRadio.disconnect();
            this.currentRadio.set({
                'uuid': uuid,
                'id': 0
            }, {
                silent: true // do not send 'change' event now, fetch will do it right after
            });

            var radio = this.currentRadio;
            this.currentRadio.fetch({
                success: function() {
                    radio.connect();
                }
            });
        },

        index: function() {
            this.clearView();
            
            // TODO: add a welcome page
        },

        // this function must be called between every routes
        clearView: function() {
            this.buildCommonContext();
            if (this.currentView) {
                this.currentView.reset();
                this.currentView.close();
                this.currentView = undefined;
            }
        },
        
        pushManager: new Yasound.App.PushManager({
            enablePush: g_enable_push
        }),

        // build common stuff for every views (radio)
        buildCommonContext: function() {
            if (!this.commonContext) {
                this.commonContext = {};
                this.commonContext.streamFunction = function(model, stream_url) {
                    if (!(typeof Yasound.App.MySound === "undefined")) {
                        Yasound.App.MySound.destruct();
                    }
                    Yasound.App.SoundConfig.url = stream_url;
                    Yasound.App.MySound = soundManager.createSound(Yasound.App.SoundConfig);
                };

                this.commonContext.userMenuView = new Yasound.Views.UserMenu({}).render();
                this.commonContext.searchMenuView = new Yasound.Views.SearchMenu({}).render();
                this.commonContext.userAuthenticated = g_authenticated;
                this.currentRadio.on('change:stream_url', this.commonContext.streamFunction);
            }
        },

        // search page
        search: function(query) {
            this.clearView();
            
            var radioSearchResults = new Yasound.Data.Models.RadioSearchResults({});
            radioSearchResults.setQuery(query);
            
            this.currentView = new Yasound.Views.SearchPage({
                tagName: 'div',
                className: 'row-fluid',
                collection: radioSearchResults
            });
            $('#webapp-content').prepend(this.currentView.render().el);
        },

        // ower favorites page
        favorites: function() {
            this.clearView();
            
            var radios = new Yasound.Data.Models.Favorites({});
            
            this.currentView = new Yasound.Views.FavoritesPage({
                tagName: 'div',
                className: 'row-fluid',
                collection: radios
            });
            $('#webapp-content').prepend(this.currentView.render().el);
        },
        
        // radio details page
        radio: function(uuid) {
            this.clearView();

            if (!this.radioContext) {
                var that = this;
                this.radioContext = {
                    currentSong: new Yasound.Data.Models.CurrentSong()
                };
                
                if (Yasound.App.Router.pushManager.enablePush) {
                    Yasound.App.Router.pushManager.on('song', function(msg) {
                        that.radioContext.currentSong.reset(msg);
                    });
                } else {
                    setInterval(function() {
                        that.radioContext.currentSong.fetch();
                    }, 10000);
                }

                this.radioContext.currentSongView = new Yasound.Views.CurrentSong({
                    model: this.radioContext.currentSong,
                    radio: this.currentRadio,
                    el: $('#webapp-player')
                })
                this.radioContext.currentSongView.radio = this.currentRadio;

                if (this.commonContext.userAuthenticated) {
                }
                this.currentRadio.on('change:id', function(model, id) {
                    model.currentSong = that.radioContext.currentSong;
                    that.radioContext.currentSong.set('radioId', id);
                    that.radioContext.currentSong.fetch();
                    that.radioContext.currentSong.set('buy_link', '/api/v1/radio/' + id + '/buy_link/');
                    that.pushManager.monitorRadio(model);
                });
            }

            this.currentView = new Yasound.Views.RadioPage({
                tagName: 'div',
                className: 'row-fluid',
                model: this.currentRadio,
                userAuthenticated: this.commonContext.userAuthenticated
            });
            $('#webapp-content').prepend(this.currentView.el);

            this.radioContext.radioUUID = 0;
            this.setCurrentRadioUUID(uuid);
        }
    });

    
    // Global object, useful to navigate in views
    Yasound.App.Router = new Yasound.App.Workspace();

    soundManager.onready(function() {
        Backbone.history.start({
            pushState: true,
            root: '/app/',
            silent: false
        });
    });

});