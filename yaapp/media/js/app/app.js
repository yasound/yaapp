$(document).ready(function() {
    Namespace('Yasound.App');

    Backbone.View.prototype.close = function(){
        this.remove();
        this.unbind();
      }
    
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
            this.currentRadio.disconnect();
            this.currentRadio.set('uuid', uuid);

            var radio = this.currentRadio;
            this.currentRadio.fetch({
                success: function() {
                    radio.connect();
                }
            });
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
                        el : $('#webapp-radio')
                    }),
                    wallInputView : new Yasound.Views.WallInput({
                        model : this.currentRadio,
                        el : $('#webapp-wall-input')
                    }),
                    currentSong : new Yasound.Data.Models.CurrentSong()
                };
                
                this.radioContext.wallPosted = function() {
                    that.radioContext.wallEvents.fetch();
                }

                this.radioContext.currentSongView = new Yasound.Views.CurrentSong({
                    model : this.radioContext.currentSong,
                    radio: this.currentRadio,
                    el : $('#webapp-player')
                })
                this.radioContext.currentSongView.radio = this.currentRadio;
                
                setInterval(function() {
                    that.radioContext.currentSong.fetch();
                }, 10000);

                if (this.commonContext.userAuthenticated) {
                    this.radioContext.wallEvents = new Yasound.Data.Models.WallEvents();
                    this.radioContext.wallEventsView = new Yasound.Views.WallEvents({
                        collection : this.radioContext.wallEvents,
                        el : $('#wall')
                    });

                    this.radioContext.radioUsers = new Yasound.Data.Models.RadioUsers();
                    this.radioContext.radioUsersView = new Yasound.Views.RadioUsers({
                        collection : this.radioContext.radioUsers,
                        el : $('#webapp-radio-users')
                    })
                    
                    this.currentRadio.on('change:uuid', function(model, uuid) {
                        that.radioContext.wallInputView.radioUUID = uuid;
                        that.radioContext.wallInputView.render();
                    })

                    this.currentRadio.on('change:id', function(model, id) {
                        that.radioContext.wallEvents.setRadio(that.currentRadio).fetch();
                        that.radioContext.radioUsers.setRadio(that.currentRadio).fetch();
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
            pushState : true,
            root : '/app/',
            silent : false
        });
    });

});