$(document).ready(function() {
    Namespace('Yasound.App');
    $('.dropdown-toggle').dropdown();

    Backbone.View.prototype.close = function() {
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
        stream: true
    };

    soundManager.ontimeout(function() {
        if (!(typeof Yasound.App.MySound === "undefined")) {
            Yasound.App.MySound.destruct();
        }
        Yasound.App.MySound = undefined;
        $('#play i').removeClass('icon-stop').addClass('icon-play');
    });

    Yasound.App.Workspace = Backbone.Router.extend({
        routes: {
            "": "index",
            "radio/:uuid": "radio",
            "search/:query": "search"
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
                silent: true
            });

            var radio = this.currentRadio;
            this.currentRadio.fetch({
                success: function() {
                    radio.connect();
                }
            });
        },

        index: function() {
            $('#wall').html('Welcome');
        },

        help: function() {
            $('#wall').html('Help');
        },

        buildCommonContext: function() {
            if (!this.commonContext) {
                this.commonContext = {};
                this.commonContext.streamFunction = function(model, stream_url) {
                    console.log('streamFunction')
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

        search: function(query) {
            this.buildCommonContext();
            if (this.currentView) {
                this.currentView.reset();
                this.currentView.close();
                this.currentView = undefined;
            }
        },

        radio: function(uuid) {
            this.buildCommonContext();
            if (this.currentView) {
                this.currentView.reset();
                this.currentView.close();
                this.currentView = undefined;
            }

            if (!this.radioContext) {
                var that = this;
                this.radioContext = {
                    currentSong: new Yasound.Data.Models.CurrentSong()
                };

                this.radioContext.currentSongView = new Yasound.Views.CurrentSong({
                    model: this.radioContext.currentSong,
                    radio: this.currentRadio,
                    el: $('#webapp-player')
                })
                this.radioContext.currentSongView.radio = this.currentRadio;

                setInterval(function() {
                    that.radioContext.currentSong.fetch();
                }, 10000);

                if (this.commonContext.userAuthenticated) {
                }
                this.currentRadio.on('change:id', function(model, id) {
                    that.radioContext.currentSong.set('radioId', id);
                    that.radioContext.currentSong.fetch();
                    that.radioContext.currentSong.set('buy_link', '/api/v1/radio/' + id + '/buy_link/');
                });
            }

            if (!this.currentView) {
                this.currentView = new Yasound.Views.RadioPage({
                    tagName: 'div',
                    className: 'row-fluid',
                    model: this.currentRadio,
                    userAuthenticated: this.commonContext.userAuthenticated
                });
                $('#webapp-content').prepend(this.currentView.el);
            }

            this.radioContext.radioUUID = 0;
            this.setCurrentRadioUUID(uuid);
        }
    });

    Yasound.App.Router = new Yasound.App.Workspace();
    soundManager.onready(function() {
        Backbone.history.start({
            pushState: true,
            root: '/app/',
            silent: false
        });
    });

});