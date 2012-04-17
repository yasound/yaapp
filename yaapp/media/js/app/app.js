$(document).ready(function() {
    Namespace('Yasound.App');

    soundManager.url = '/media/js/sm/swf/'; // directory where SM2 .SWFs
    soundManager.preferFlash = true;
    soundManager.useHTML5Audio = true;
    soundManager.debugMode = true;
    soundManager.useFlashBlock = true;
    Yasound.App.MySound = undefined;

    Yasound.App.SoundConfig = {
        id : 'yasoundMainPlay',
        url : undefined,
        autoPlay : true,
        autoLoad : true,
        stream : true
    };

    soundManager.ontimeout(function() {
        if (!(typeof Yasound.App.MySound === "undefined")) {
            Yasound.App.MySound.destruct();
        }
        Yasound.App.MySound = undefined;
        $('#play i').removeClass('icon-stop').addClass('icon-play');
    });

    Yasound.App.Workspace = Backbone.Router.extend({
        routes : {
            "" : "index",
            "radio/:id" : "radio"
        },

        currentRadio : new Yasound.Data.Models.Radio({
            id : 0
        }),

        setCurrentRadioId : function(id) {
            this.currentRadio.set('id', id);
            this.currentRadio.fetch();
        },

        index : function() {
            $('#wall').html('Welcome');
        },

        help : function() {
            $('#wall').html('Help');
        },

        search : function(query, page) {
        },

        radio : function(id) {
            if (!this.commonContext) {
                this.commonContext = {};
                this.commonContext.streamFunction = function(model, stream_url) {
                    if (!(typeof Yasound.App.MySound === "undefined")) {
                        Yasound.App.MySound.destruct();
                    }
                    Yasound.App.SoundConfig.url = stream_url;
                    Yasound.App.MySound = soundManager.createSound(Yasound.App.SoundConfig);
                    Yasound.App.MySound.play();
                    $('#play i').removeClass('icon-play').addClass('icon-stop');
                    $('#volume-position').css("width", Yasound.App.MySound.volume + "%");
                };

                this.currentRadio.on('change:stream_url', this.commonContext.streamFunction);
            }

            if (!this.radioContext) {
                this.radioContext = {
                    radioView : new Yasound.Views.Radio({
                        model : this.currentRadio,
                        el : $('#radio')
                    }),
                    currentSong : new Yasound.Data.Models.CurrentSong(),
                    wallEvents : new Yasound.Data.Models.WallEvents(),
                }
                this.radioContext.wallEventsView = new Yasound.Views.WallEvents({
                    collection : this.radioContext.wallEvents,
                    el : $('#wall')
                });

                this.radioContext.currentSongView = new Yasound.Views.CurrentSong({
                    model : this.radioContext.currentSong,
                    el : $('#player')
                })
                var that = this;
                setInterval(function() {
                    that.radioContext.currentSong.fetch();
                    that.radioContext.wallEvents.fetch();
                }, 10000);
            }
            this.radioContext.wallEventsView.clear();
            this.radioContext.currentSong.set('radioId', id);
            this.radioContext.currentSong.fetch();
            this.radioContext.currentSong.set('buy_link', '/api/v1/radio/' + id + '/buy_link/');
            this.setCurrentRadioId(id);
            this.radioContext.wallEvents.setRadio(this.currentRadio);
            this.radioContext.wallEvents.fetch();
        }
    });

    var router = new Yasound.App.Workspace();

    soundManager.onready(function() {
        console.debug('soundManager.onready');
        Backbone.history.start({
            pushState : false,
            root : '/app/',
            silent : false
        });
    });

});