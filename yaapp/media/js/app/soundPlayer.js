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
            if (!(typeof mgr.soundHandler === "undefined")) {
                mgr.soundHandler.unload();
                console.log('publishing /player/stop');
                $.publish('/player/stop');
            }
        },

        setAutoplay: function (autoplay) {
            mgr.autoplay = autoplay;
            mgr.play();
        },

        play: function () {
            if (mgr.isPlaying()) {
                console.log('publishing /player/play');
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
                        console.log('publishing /player/play');
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
                console.log('publishing /player/play');
            }

        },

        setHD: function (hd) {
            if (hd == mgr.hd) {
                return;
            }
            mgr.hd = hd;
            mgr.stop();
            mgr.play();
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
        currentSongBinded: false,
        deezerId: 0,
        playing: false,
        trackLoaded: false,
        autoplay: false,

        isPlaying: function () {
            return mgr.playing;
        },

        setBaseUrl: function(baseUrl) {
            if (!mgr.currentSongBinded) {
                Yasound.App.Router.radioContext.currentSong.on('change', mgr.refreshSong);
                mgr.currentSongBinded = true;
            }
        },

        refreshSong: function (song) {
            console.log('deezer -- refresh song');
            // TODO: load into deezer player
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
                    console.log('id is ' + deezerId);
                    if (!deezerId || deezerId === mgr.deezerId) {
                        console.log('stopping music');
                        mgr.stop();
                        return;
                    }
                    mgr.deezerId = deezerId;
                    mgr.trackLoaded = false;
                    if (mgr.isPlaying()) {
                        mgr.play();
                    }
                }
            });
        },

        setVolume: function (volume) {
        },

        volume: function () {
            return 0;
        },

        stop: function () {
            if (mgr.isPlaying()) {
                DZ.player.pause();
                mgr.playing = false;
                $.publish('/player/stop');
            }
        },

        setAutoplay: function (autoplay) {
            mgr.autoplay = autoplay;
            mgr.play();
        },

        play: function () {
            if (!mgr.trackLoaded) {
                if (mgr.deezerId !== 0) {
                    console.log('loading track ' + mgr.deezerId);
                    DZ.player.playTracks([mgr.deezerId], 0, function(response) {});
                    mgr.trackLoaded = true;
                }
            } else {
                if (DZ && DZ.player) {
                    DZ.player.play();
                }
            }
            mgr.playing = true;
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