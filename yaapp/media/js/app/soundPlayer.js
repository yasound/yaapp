/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Player');

Yasound.Player.SoundManager = function () {
    soundManager.url = '/media/js/sm/swf/'; // directory where SM2 .SWFs
    soundManager.preferFlash = true;
    soundManager.useHTML5Audio = true;
    soundManager.debugMode = false;
    soundManager.useFlashBlock = true;
    soundManager.flashVersion = 9;
    soundManager.useHighPerformance = true;
    soundManager.useFastPolling = true;

    var async = true;
    if (Yasound.App.isMobile) {
        async = false;
    }

    var mgr = {
        config : {
            id: 'yasoundMainPlay',
            url: '/',
            autoPlay: true,
            autoLoad: true,
            volume: 100,
            stream: true
        },
        hd: Yasound.App.hd,
        baseUrl: undefined,
        soundHandler: undefined,
        autoplay: false,
        manualStopped: false,

        isPlaying: function () {
            if (typeof mgr.soundHandler === "undefined" || mgr.soundHandler.playState != 1) {
                return false;
            }
            return true;
        },

        setBaseUrl: function(baseUrl) {
            mgr.baseUrl = baseUrl;
            if (mgr.isPlaying() || mgr.autoplay) {
                mgr.stop();
                mgr.play();
            }
        },

        setVolume: function (volume) {
            mgr.config.volume = volume;
            if (mgr.isPlaying()) {
                mgr.soundHandler.setVolume(volume);
            }
        },

        volume: function () {
            return mgr.config.volume;
        },

        stop: function () {
            mgr.autoplay = false;
            mgr.manualStopped = true;
            if (!(typeof mgr.soundHandler === "undefined")) {
                mgr.soundHandler.unload();
                $.publish('/player/stop');
            }
        },

        setAutoplay: function (autoplay) {
            if (!mgr.manualStopped) {
                mgr.autoplay = autoplay;
                mgr.play();
            } else {
                mgr.autoplay = false;
            }
        },

        play: function () {
            if (mgr.isPlaying()) {
                $.publish('/player/play');
                return;
            }

            var url = '/api/v1/streamer_auth_token/';
            var streamURL = mgr.baseUrl;
            if (Yasound.App.userAuthenticated) {
                $.ajax({
                    url: url,
                    async: async,
                    type: 'GET',
                    dataType: 'json',
                    success: function(data) {
                        var token = data.token;
                        var fullURL = streamURL + '/?token=' + token;
                        if (mgr.hd) {
                            fullURL = fullURL + '&hd=1';
                        }
                        mgr.config.url = fullURL;

                        if ((typeof mgr.soundHandler === "undefined")) {
                            mgr.soundHandler = soundManager.createSound(mgr.config);
                        } else {
                            mgr.soundHandler.play(mgr.config);
                        }
                        $.publish('/player/play');
                    },
                    failure: function() {
                    }
                });
            } else {
                mgr.config.url = mgr.baseUrl;
                if (!mgr.config.url) {
                    return;
                }

                if ((typeof mgr.soundHandler === "undefined")) {
                    mgr.soundHandler = soundManager.createSound(mgr.config);
                } else {
                    mgr.soundHandler.play(mgr.config);
                }
                $.publish('/player/play');
            }

        },

        setHD: function (hd) {
            if (hd == mgr.hd) {
                return;
            }
            mgr.hd = hd;
            if (mgr.isPlaying()) {
                mgr.stop();
                mgr.play();
            }
        },

        init: function (callback) {
            if (!callback) {
                callback = function () { };
            }

            var waitForSM = true;
            if ($.browser.msie) {
                if ($.browser.version == '8.0' || $.browser.version == '7.0' || $.browser.version == '6.0') {
                    waitForSM = false;
                }
            }

            if (waitForSM) {
                soundManager.onready(callback);
            } else {
                callback();
            }
        }
    };
    return mgr;
};


Yasound.Player.Deezer = function () {
    var mgr = {
        hd: false,
        firstLoad: true,
        currentSongBinded: false,
        deezerId: 0,
        playing: false,
        trackLoaded: false,
        autoplay: false,
        manualStopped: false,

        isPlaying: function () {
            if (DZ && DZ.player) {
                return DZ.player.isPlaying();
            }
            return false;
        },

        setBaseUrl: function(baseUrl) {
            if (!mgr.currentSongBinded) {
                Yasound.App.Router.radioContext.currentSong.on('change', mgr.refreshSong);
                mgr.currentSongBinded = true;
            }
        },

        refreshSong: function (song) {
            console.log('deezer -- refresh song');
            var title = song.rawTitle();
            var query = '/search?q=' + title + '&order=RANKING';
            console.log('query is "' + query + '"');
            DZ.api(query, function (response) {
                console.log('response is');
                console.log(response);

                var total = response.total;
                if (total > 0) {
                    console.log('found ' + total + ' items');
                    var item = response.data[0];
                    var deezerId = item.id;
                    mgr.deezerId = deezerId;
                    console.log('id is ' + deezerId);
                    DZ.player.addToQueue([deezerId]);
                }
            });
        },

        setVolume: function (volume) {
        },

        volume: function () {
            return 0;
        },

        stop: function () {
            mgr.autoplay = false;
            mgr.manualStopped = true;
            if (DZ && DZ.player) {
                DZ.player.pause();
            }
            $.publish('/player/stop');
        },

        setAutoplay: function (autoplay) {
            if (!mgr.manualStopped) {
                mgr.autoplay = autoplay;
                mgr.play();
            } else {
                mgr.autoplay = false;
            }
        },

        play: function () {
            if (DZ && DZ.player) {
                if (mgr.firstLoad && mgr.deezerId) {
                    DZ.player.playTracks([mgr.deezerId]);
                    mgr.firstLoad = false;
                } else {
                    DZ.player.play();
                }
            }
            $.publish('/player/play');
        },

        setHD: function (hd) {
            return;
        },

        init: function (callback) {
            if (!callback) {
                callback = function () { };
            }
            DZ.init({
                ajax : true
            });
            DZ.ready(function(sdk_options){
                DZ.canvas.setSize(1125);
                callback();
            });
        }
    };
    return mgr;
};