$(document).ready(function() {
    soundManager.url = '/media/js/sm/swf/'; // directory where SM2 .SWFs
    // live
    soundManager.preferFlash = true;
    soundManager.useHTML5Audio = true;
    soundManager.debugMode = false;
    soundManager.useFlashBlock = true;
    soundManager.flashVersion = 9;
    var mySound;
    var soundConfig = {
        id : 'yasoundMainPlay',
        url : g_radio_url,
        autoPlay: g_auto_play,
        autoLoad: true,
        stream : true
    };

    soundManager.onready(function() {
        if (g_auto_play) {
            mySound = soundManager.createSound(soundConfig);
            $('#play i').removeClass('icon-play').addClass('icon-stop');
            $('#volume-position').css("width", mySound.volume + "%");
        } else {
            $('#play i').removeClass('icon-stop').addClass('icon-play');
        }
    });

    var isPlaying = function (soundHandler) {
        if (typeof soundHandler === "undefined" || soundHandler.playState != 1) {
            return false;
        }
        return true;
    };


    soundManager.ontimeout(function() {
        if (!(typeof mySound === "undefined")) {
            mySound.destruct();
        }
        mySound = undefined;
        $('#play i').removeClass('icon-stop').addClass('icon-play');
    });

    $('#play').click(function() {
        if (!isPlaying(mySound)) {
            if ((typeof mySound === "undefined")) {
                mySound = soundManager.createSound(soundConfig);
                mySound.play(soundConfig);
            } else {
                mySound.play(soundConfig);
            }
            $('#play i').removeClass('icon-play').addClass('icon-stop');
            $('#volume-position').css("width", mySound.volume + "%");
        } else {
            $('#play i').removeClass('icon-stop').addClass('icon-play');
            if (!(typeof mySound === "undefined")) {
                mySound.unload();
            }
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
    });

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
    });

    var getData = function() {
        // get last events
        $.ajax({
            url : '/api/v1/radio/' + g_radio_id + '/current_song/',
            dataType : 'json',
            data : undefined,
            success : function(data) {
                if (data) {
                    var name = data.name;
                    var artist = data.artist;
                    var album = data.album;
                    var cover = data.large_cover;

                    $('#track-name').text(name);
                    $('#track-artist').text(artist);
                    $('#track-album').text(album);

                    if (cover) {
                        $('#track-image').attr("src", cover);
                    } else {
                        $('#track-image').attr("src", '/media/images/default_image.png');
                    }

                }
            }
        });
    };

    $(document).everyTime(10 * 1000, 'event_timer', function(x) {
        if (typeof mySound === "undefined") {
            return;
        }
        getData();
    });
    getData();

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
        var soundVolume = Math.floor(relativePosition * 100 / width);
        var percentage = soundVolume + "%";
        $('#volume-position').css("width", percentage);

        mySound.setVolume(soundVolume);
    };

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
});
