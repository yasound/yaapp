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

        }
    };
    return mgr;
};