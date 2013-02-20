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

        setBaseUrl: function(radio, baseUrl) {
            mgr.baseUrl = baseUrl;
            mgr.radio = radio;
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
            if (!streamURL) {
                return;
            }

            if (Yasound.App.userAuthenticated && mgr.radio && mgr.radio.get('origin') === Yasound.App.RADIO_ORIGIN_YASOUND) {
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

Yasound.Player.InstantPlayer = function () {
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
            id: 'yasoundInstantPlay',
            url: '/',
            autoPlay: true,
            autoLoad: true,
            volume: 100,
            stream: true
        },
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
            }
        },

        play: function (streamURL) {
            if (mgr.isPlaying()) {
                return;
            }
            mgr.config.url = streamURL;
            if (!mgr.config.url) {
                return;
            }
            mgr.setVolume(Yasound.App.player.volume());

            if ((typeof mgr.soundHandler === "undefined")) {
                mgr.soundHandler = soundManager.createSound(mgr.config);
            } else {
                mgr.soundHandler.play(mgr.config);
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


Yasound.Player.PreviewPlayer = function () {
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
            id: 'yasoundInstantPlay',
            url: '/',
            autoPlay: true,
            autoLoad: true,
            volume: 100,
            stream: false,
            onfinish: function () {
                mgr.onFinished();
            }
        },
        resumeAtEnd: false,
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

        setVolume: function (volume) {
            mgr.config.volume = volume;
            if (mgr.isPlaying()) {
                mgr.soundHandler.setVolume(volume);
            }
        },

        volume: function () {
            return mgr.config.volume;
        },

        stop: function (disableCb) {
            mgr.autoplay = false;
            mgr.manualStopped = true;
            if (!(typeof mgr.soundHandler === "undefined")) {
                mgr.soundHandler.unload();
            }
            if (!disableCb) {
                mgr.onFinished();
            }
        },

        play: function (streamURL, finishCallback) {
            mgr.finishCallback = finishCallback;
            mgr.stop(true);
            if (Yasound.App.player.isPlaying()) {
                Yasound.App.player.stop();
                mgr.resumeAtEnd = true;
            } else {
                mgr.resumeAtEnd = false;
            }
            if (mgr.isPlaying()) {
                return;
            }
            mgr.config.url = streamURL;
            if (!mgr.config.url) {
                return;
            }
            mgr.setVolume(Yasound.App.player.volume());

            if ((typeof mgr.soundHandler === "undefined")) {
                mgr.soundHandler = soundManager.createSound(mgr.config);
            } else {
                mgr.soundHandler.play(mgr.config);
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
        },

        onFinished: function () {
            if (mgr.resumeAtEnd) {
                Yasound.App.player.play();
            }
            if (mgr.finishCallback) {
                mgr.finishCallback();
            }
        }
    };
    return mgr;
};


Yasound.Player.Deezer = function () {
    soundManager.url = '/media/js/sm/swf/'; // directory where SM2 .SWFs
    soundManager.preferFlash = true;
    soundManager.useHTML5Audio = true;
    soundManager.debugMode = false;
    soundManager.useFlashBlock = true;
    soundManager.flashVersion = 9;
    soundManager.useHighPerformance = true;
    soundManager.useFastPolling = true;

    var mgr = {
        soundManagerReady: false,
        smConfig: {
            id: 'yasoundMainPlay',
            url: '/',
            autoPlay: true,
            autoLoad: true,
            volume: 1,
            stream: true
        },
        hd: false,
        radio: undefined,
        radioHasChanged: false,
        deezerId: 0,
        deezerAlbumId: 0,
        deezerArtistId: 0,
        playing: false,
        trackLoaded: false,
        autoplay: false,
        noTrackFound: true,
        previousTitle: '',
        manualStopped: false,
        firstLoad: true,

        isPlaying: function () {
            if (DZ && DZ.player) {
                return DZ.player.isPlaying();
            }
            return false;
        },

        loadExternalTrack: function() {
            var url = '/api/v1/radio/' + mgr.radio.get('uuid') + '/gdu/';
            $.ajax({
                url: url,
                type: 'POST',
                data: {
                    csrfmiddlewaretoken: cookies.get('csrftoken')
                },
                dataType: 'json',
                success: function(data) {
                    // load url into deezer
                    var downloadUrl = data.url;
                    var artist = data.artist;
                    var name = data.name;
                    var trackList = [{
                        url: downloadUrl,
                        format: 'mp3',
                        artist: artist,
                        title: name
                    }];
                    DZ.player.playExternalTracks(trackList);
                },
                failure: function() {
                }
            });
        },

        setBaseUrl: function(radio, baseUrl) {
            mgr.radio = radio;
            Yasound.App.Router.radioContext.currentSong.on('change:name', mgr.refreshSong);
            // console.log('radio has changed');
            mgr.notifyStreamer(baseUrl);

            if (mgr.firstLoad) {
                mgr.firstLoad = false;
            } else {
                mgr.radioHasChanged = true;
            }
        },

        notifyStreamer: function (url) {
            console.log('notifyStreamer called with ' + url);
            if (!mgr.soundManagerReady) {
                console.log('manager not ready, exiting');
                return;
            }
            mgr.smConfig.url = url;
            var handle = soundManager.createSound(mgr.smConfig);
            handle.play();
            console.log('done!')
            var timerId = setInterval(function () {
                console.log('unloading manager');
                if (handle) {
                    handle.unload();
                }
                clearInterval(timerId);
            }, 5000);
        },

        refreshSong: function (song) {
            // console.log('deezer -- refresh song');
            Yasound.App.Router.radioContext.currentSong.off('change:name', mgr.refreshSong);

            var title = song.rawTitleWithoutAlbum();
            if (title === mgr.previewTitle) {
                Yasound.App.Router.radioContext.currentSong.on('change:name', mgr.refreshSong);
                return;
            }
            mgr.previewTitle = title;

            var query = '/search?q=' + title + '&order=RANKING';
            // console.log('query is "' + query + '"');
            DZ.api(query, mgr.searchCallback);
            Yasound.App.Router.radioContext.currentSong.on('change:name', mgr.refreshSong);
        },

        searchCallback: function (response) {
            // console.log('response is');
            // console.log(response);
            var total = response.total;
            if (total > 0) {
                // console.log('found ' + total + ' items');
                var item = response.data[0];
                var deezerId = item.id;
                var deezerArtistId = 0;
                var deezerAlbumId = 0;
                if (item.artist) {
                    deezerArtistId = item.artist.id;
                }
                if (item.album) {
                    deezerAlbumId = item.album.id;
                }
                mgr.onSongFound(deezerId, deezerAlbumId, deezerArtistId);


            } else {
                mgr.onSongNotFound();
            }
        },

        onSongFound: function (deezerId, deezerAlbumId, deezerArtistId) {
            mgr.noTrackFound = false;

            mgr.deezerId = deezerId;
            mgr.deezerAlbumId = deezerAlbumId;
            mgr.deezerArtistId = deezerArtistId;

            $.publish('/player/deezer/songFound', mgr);

            // console.log('id is ' + deezerId);

            if (mgr.radioHasChanged) {
                // console.log('radio has changed, loading track now!');
                DZ.player.playTracks([deezerId]);
                mgr.radioHasChanged = false;
            } else {
                // console.log('same radio, do not load track now, adding it to queue');
                DZ.player.addToQueue([deezerId]);
            }
        },

        onSongNotFound: function () {
            mgr.noTrackFound = true;

            mgr.deezerId = 0;
            mgr.deezerAlbumId = 0;
            mgr.deezerArtistId = 0;

            $.publish('/player/deezer/songNotFound', mgr);

            // console.log('no track found');
            if (mgr.radioHasChanged) {
                // console.log('radio has changed, stopping player');
                DZ.player.pause();
            } else {
                // console.log('same radio, do nothing');
            }
            // console.log('calling loadExternalTrack');
            mgr.loadExternalTrack();
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
            return;
        },

        setHD: function (hd) {
            return;
        },

        init: function (callback) {
            if (!callback) {
                callback = function () { };
            }
            soundManager.onready(function () {
                mgr.soundManagerReady = true;
            });
            DZ.init({
                ajax : true
            });
            DZ.ready(function(sdk_options){
                Yasound.App.deezerLikeOperations = Yasound.Deezer.LikeOperations();
                Yasound.App.deezerExportOperations = Yasound.Deezer.ExportOperations();
                DZ.canvas.setSize(1125);
                callback();
            });
        }
    };
    return mgr;
};