$(document).ready(function() {
    Namespace('Yasound.App');

    soundManager.url = '/media/js/sm/swf/'; // directory where SM2 .SWFs
    soundManager.preferFlash = true;
    soundManager.useHTML5Audio = true;
    soundManager.debugMode = true;
    soundManager.useFlashBlock = true;
    var mySound = undefined;

    soundManager.ontimeout(function() {
        if (!(typeof mySound === "undefined")) {
            mySound.destruct();
        }
        mySound = undefined;
        $('#play i').removeClass('icon-stop').addClass('icon-play');
    });

    $('#play').click(function() {
        if (typeof mySound === "undefined") {
            mySound = soundManager.createSound(soundConfig);
            mySound.play();
            $('#play i').removeClass('icon-play').addClass('icon-stop');
            $('#volume-position').css("width", mySound.volume + "%");
        } else {
            $('#play i').removeClass('icon-stop').addClass('icon-play');
            mySound.destruct();
            mySound = undefined;
        }
    });

    $('#inc').click(function() {
        if (typeof mySound === "undefined") {
            return;
        }
        if (mySound.volume <= 90) {
            $('#volume-position').css("width", mySound.volume + 10 + "%");
            mySound.setVolume(mySound.volume + 10);
        } else {
            $('#volume-position').css("width", "100%");
            mySound.setVolume(100);
        }
    })
    $('#dec').click(function() {
        if (typeof mySound === "undefined") {
            return;
        }
        if (mySound.volume >= 10) {
            $('#volume-position').css("width", mySound.volume - 10 + "%");
            mySound.setVolume(mySound.volume - 10);
        } else {
            $('#volume-position').css("width", "0%");
            mySound.setVolume(0);
        }
    })

    var resizeVolumeBar = function(event) {
        if (typeof mySound === "undefined") {
            return;
        }
        $('body').css('cursor', 'pointer');
        var $volumeControl = $('#volume-control');
        var position = event.pageX;
        var left = $volumeControl.position().left;
        var width = $volumeControl.width();

        var relativePosition = position - left;
        var soundVolume = Math.floor(relativePosition * 100 / width)
        var percentage = soundVolume + "%";
        $('#volume-position').css("width", percentage);

        mySound.setVolume(soundVolume);
    }

    var volumeMouseDown = false;
    $('#volume-control').mousedown(function(event) {
        volumeMouseDown = true;
        resizeVolumeBar(event);
    });
    $(document).mouseup(function(event) {
        if (volumeMouseDown) {
            $('body').css('cursor', 'auto');
            volumeMouseDown = false;
        }
    });

    $(document).mousemove(function(event) {
        if (!volumeMouseDown) {
            return;
        }
        resizeVolumeBar(event);
    });

    $('#player').height($('#radio').height());

    Yasound.App.Workspace = Backbone.Router.extend({
        routes : {
            "" : "index",
            "radio/:id" : "radio",
            "help" : "help", // #help
            "search/:query" : "search", // #search/kiwis
            "search/:query/p:page" : "search" // #search/kiwis/p7
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
            if (!this.radioContext) {
                this.radioContext = {
                    radioView : new Yasound.Views.Radio({
                        model : this.currentRadio,
                        el : $('#radio')
                    }),
                    currentSong : new Yasound.Data.Models.CurrentSong(),
                    wallEvents : new Yasound.Data.Models.WallEvents()
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
                }, 10000);
            }
            this.radioContext.currentSong.set('radioId', id);
            this.radioContext.currentSong.fetch();
            this.setCurrentRadioId(id);
            this.radioContext.wallEvents.radio = this.currentRadio;
            this.radioContext.wallEvents.fetch();

        }
    });

    var router = new Yasound.App.Workspace();

    soundManager.onready(function() {
        Backbone.history.start({
            pushState : false,
            root : '/app/',
            silent : false
        });
        // mySound = soundManager.createSound(soundConfig);
        // mySound.play();
        // $('#volume-position').css("width", mySound.volume + "%");
    });

});