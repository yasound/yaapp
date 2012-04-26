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
                    radioPage: new Yasound.Views.RadioPage({
                        el: $('#webapp-content'),
                        model: this.currentRadio,
                        userAuthenticated: this.commonContext.userAuthenticated
                    }),                  
                    currentSong : new Yasound.Data.Models.CurrentSong()
                };
                
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
                }
                this.currentRadio.on('change:id', function(model, id) {
                    that.radioContext.currentSong.set('radioId', id);
                    that.radioContext.currentSong.fetch();
                    that.radioContext.currentSong.set('buy_link', '/api/v1/radio/' + id + '/buy_link/');
                });
            }
            
            this.radioContext.radioUUID = 0;
            this.setCurrentRadioUUID(uuid);
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