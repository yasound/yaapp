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
            "radio/:uuid" : "radio"
        },

        currentRadio : new Yasound.Data.Models.Radio({
            uuid : 0
        }),

        setCurrentRadioUUID : function(uuid) {
            this.currentRadio.set('uuid', uuid);
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
                this.commonContext.userAuthenticated = g_authenticated;
                this.currentRadio.on('change:stream_url', this.commonContext.streamFunction);
            }
        },
        
        radio : function(uuid) {
            this.buildCommonContext();
            
            if (!this.radioContext) {
                var that = this;
                this.radioContext = {
                    radioView : new Yasound.Views.Radio({
                        model : this.currentRadio,
                        el : $('#radio')
                    }),
                    wallInputView : new Yasound.Views.WallInput({
                        model : this.currentRadio,
                        el : $('#wall-input')
                    }),
                    currentSong : new Yasound.Data.Models.CurrentSong()
                };
                
                this.radioContext.wallPosted = function() {
                    that.radioContext.wallEvents.fetch();
                }

                this.radioContext.currentSongView = new Yasound.Views.CurrentSong({
                    model : this.radioContext.currentSong,
                    el : $('#player')
                })

                setInterval(function() {
                    that.radioContext.currentSong.fetch();
                }, 10000);

                if (this.commonContext.userAuthenticated) {
                    this.radioContext.wallEvents = new Yasound.Data.Models.WallEvents();
                    this.radioContext.wallEventsView = new Yasound.Views.WallEvents({
                        collection : this.radioContext.wallEvents,
                        el : $('#wall')
                    });

                    this.currentRadio.on('change:uuid', function(model, uuid) {
                        that.radioContext.wallInputView.radioUUID = uuid;
                        that.radioContext.wallInputView.render();
                    })

                    this.currentRadio.on('change:id', function(model, id) {
                        that.radioContext.wallEvents.setRadio(that.currentRadio);
                        that.radioContext.wallEvents.fetch();
                    })

                    
                    setInterval(function() {
                        that.radioContext.wallEvents.fetch();
                    }, 10000);

                }
                this.currentRadio.on('change:id', function(model, id) {
                    that.radioContext.currentSong.set('radioId', id);
                    that.radioContext.currentSong.fetch();
                    that.radioContext.currentSong.set('buy_link', '/api/v1/radio/' + id + '/buy_link/');
                });
            }
            
            this.radioContext.radioUUID = 0;
            this.setCurrentRadioUUID(uuid);

            if (this.commonContext.userAuthenticated) {
                $.unsubscribe('/wall/posted', this.radioContext.wallPosted);
                $.subscribe("/wall/posted", this.radioContext.wallPosted);

                this.radioContext.wallEventsView.clear();
                this.radioContext.wallInputView.render();
            }
        }
    });

    var router = new Yasound.App.Workspace();

    soundManager.onready(function() {
        Backbone.history.start({
            pushState : false,
            root : '/app/',
            silent : false
        });
    });

});