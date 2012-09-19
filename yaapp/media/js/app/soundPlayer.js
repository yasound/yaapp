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

    var mgr = {
        config : {
            id: 'yasoundMainPlay',
            url: '/',
            autoPlay: true,
            autoLoad: true,
            volume: 100,
            stream: true
        },
        baseUrl: undefined,
        soundHandler: undefined,

        isPlaying: function () {
            if (typeof mgr.soundHandler === "undefined" || mgr.soundHandler.playState != 1) {
                return false;
            }
            return true;
        },

        setBaseUrl: function(baseUrl) {
            mgr.baseUrl = baseUrl;
            if (mgr.isPlaying()) {
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
            }
        },

        play: function (callback) {
            if (!callback) {
                callback = function() {};
            }

            var url = '/api/v1/streamer_auth_token/';
            var streamURL = mgr.baseUrl;
            if (Yasound.App.userAuthenticated) {
                $.ajax({
                    url: url,
                    type: 'GET',
                    dataType: 'json',
                    success: function(data) {
                        var token = data.token;
                        var fullURL = streamURL + '/?token=' + token;
                        mgr.config.url = fullURL;

                        if ((typeof mgr.soundHandler === "undefined")) {
                            mgr.soundHandler = soundManager.createSound(mgr.config);
                        } else {
                            mgr.soundHandler.play(mgr.config);
                        }
                        callback();
                    },
                    failure: function() {
                        callback();
                    }
                });
            } else {
                mgr.config.url = mgr.baseUrl;
                if ((typeof mgr.soundHandler === "undefined")) {
                    mgr.soundHandler = soundManager.createSound(mgr.config);
                } else {
                    mgr.soundHandler.play(mgr.config);
                }
                callback();
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
        currentSongBinded: false,
        deezerId: 0,
        playing: false,
        trackLoaded: false,

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
            var title = song.title();
            var query = '/search?q=' + title + '&order=RANKING';
            DZ.api(query, function (response) {
                var total = response.total;
                if (total > 0) {
                    var item = response.data[0];
                    var deezerId = item.id;
                    if (!deezerId || deezerId === mgr.deezerId) {
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
            }
        },

        play: function (callback) {
            if (!callback) {
                callback = function () {};
            }

            if (!mgr.trackLoaded) {
                if (mgr.deezerId !== 0) {
                    DZ.player.playTracks([mgr.deezerId], 0, function(response) {});
                    mgr.trackLoaded = true;
                }
            } else {
                if (DZ && DZ.player) {
                    DZ.player.play();
                }
            }
            mgr.playing = true;
        },

        init: function (callback) {
            if (!callback) {
                callback = function () { };
            }
            DZ.init({
                ajax : true
            });
            DZ.ready(function(sdk_options){
                callback();
            });
        }
    };
    return mgr;
};