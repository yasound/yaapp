"use strict";
/*
 * jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true,
 * evil: true, undef: true, white: true, newcap: true
 */
/* extern Ext, $ */

Namespace('Yasound.Views');

/**
 * RadioCell - display a radio in a list
 */
Yasound.Views.RadioCell = Backbone.View.extend({
    tagName: 'li',
    className: 'radio-cell',

    events: {
        'click .radio-cell': 'onRadio'
    },

    initialize: function () {
        this.model.bind('change', this.render, this);
    },
    onClose: function () {
        this.model.unbind('change', this.render);
    },
    render: function () {
        var data = this.model.toJSON();
        $(this.el).hide().html(ich.radioCellTemplate(data)).fadeIn(200);
        return this;
    },
    onRadio: function (e) {
        e.preventDefault();
        var uuid = this.model.get('uuid');
        Yasound.App.Router.navigate("radio/" + uuid + '/', {
            trigger: true
        });
    }
});

/**
 * User menu handler
 */
Yasound.Views.UserMenu = Backbone.View.extend({
    el: '#user-menu',
    events: {
        'click #btn-my-radio': 'myRadio',
        'click #btn-favorites': 'favorites'
    },
    myRadio: function (e) {
        e.preventDefault();
        var uuid = $('#btn-my-radio', this.el).attr('yasound:uuid');
        Yasound.App.Router.navigate("radio/" + uuid + '/', {
            trigger: true
        });
    },
    favorites: function (e) {
        e.preventDefault();
        Yasound.App.Router.navigate('favorites/', {
            trigger: true
        });
    }
});

/**
 * Song player
 */
Yasound.Views.CurrentSong = Backbone.View.extend({
    tagName: 'div',
    className: 'track',
    volumeMouseDown: false,

    events: {
        "click #play": "play",
        "click #inc": "inc",
        "click #dec": "dec",
        "click #like": "like",
        "click #track-image-link": "displayRadio",
        "mousedown #volume-control": "volumeControl",
        "mouseup": 'mouseUp',
        "mousemove": "mouseMove",
        "click #fb_share": "facebookShare"
    },

    initialize: function () {
        this.model.bind('change', this.render, this);
    },

    onClose: function () {
        this.model.unbind('change', this.render);
    },

    generateTwitterText: function () {
        if (!this.radio) {
            return '';
        }

        var share = gettext('I am listening to');
        share += ' ' + this.model.get('name') + ', ';
        share += gettext('by') + ' ' + this.model.get('artist') + ' ';
        share += gettext('on') + ' ' + this.radio.get('name');
        return share;
    },

    generateFacebookText: function () {
        return this.generateTwitterText();
    },

    generateSocialShare: function () {
        if (!this.radio) {
            $('#tweet').hide();
        } else {
            var twitterParams = {
                url: '' + window.location,
                text: this.generateTwitterText(),
                hashtags: 'yasound'
            };
            $('#tweet', this.el).show();
            $('#tweet', this.el).attr('href', "http://twitter.com/share?" + $.param(twitterParams));
            $('meta[name=description]').attr('description', this.generateFacebookText());
        }
    },

    render: function () {
        $(this.el).html(ich.trackTemplate(this.model.toJSON()));
        this.generateSocialShare();

        if (Yasound.App.MySound) {
            if (Yasound.App.MySound.playState == 1) {
                $('#play i').removeClass('icon-play').addClass('icon-stop');
            }
            $('#volume-position').css("width", Yasound.App.MySound.volume + "%");
        }
        
        // hide social buttons if current song is empty
        if (this.model.get('id')) {
            $('#tweet', this.el).show();
            $('#fb_share', this.el).show();
        } else {
            $('#tweet', this.el).hide();
            $('#fb_share', this.el).hide();
        }
        
        return this;
    },

    play: function () {
        if (typeof Yasound.App.MySound === "undefined") {
            Yasound.App.MySound = soundManager.createSound(Yasound.App.SoundConfig);
            Yasound.App.MySound.play();
            $('#play i').removeClass('icon-play').addClass('icon-stop');
            $('#volume-position').css("width", Yasound.App.MySound.volume + "%");
        } else {
            $('#play i').removeClass('icon-stop').addClass('icon-play');
            Yasound.App.MySound.destruct();
            Yasound.App.MySound = undefined;
        }
    },

    inc: function () {
        if (typeof Yasound.App.MySound === "undefined") {
            return;
        }
        if (Yasound.App.MySound.volume <= 90) {
            $('#volume-position').css("width", Yasound.App.MySound.volume + 10 + "%");
            Yasound.App.MySound.setVolume(Yasound.App.MySound.volume + 10);
        } else {
            $('#volume-position').css("width", "100%");
            Yasound.App.MySound.setVolume(100);
        }
        Yasound.App.SoundConfig.volume = Yasound.App.MySound.volume;
    },

    dec: function () {
        if (typeof Yasound.App.MySound === "undefined") {
            return;
        }
        if (Yasound.App.MySound.volume >= 10) {
            $('#volume-position').css("width", Yasound.App.MySound.volume - 10 + "%");
            Yasound.App.MySound.setVolume(Yasound.App.MySound.volume - 10);
        } else {
            $('#volume-position').css("width", "0%");
            Yasound.App.MySound.setVolume(0);
        }
        Yasound.App.SoundConfig.volume = Yasound.App.MySound.volume;
    },

    resizeVolumeBar: function (event) {
        if (typeof Yasound.App.MySound === "undefined") {
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

        Yasound.App.MySound.setVolume(soundVolume);
        Yasound.App.SoundConfig.volume = Yasound.App.MySound.volume;
    },

    mouseUp: function (event) {
        if (this.volumeMouseDown) {
            $('body').css('cursor', 'auto');
            this.volumeMouseDown = false;
        }
    },

    mouseMove: function (event) {
        if (!this.volumeMouseDown) {
            return;
        }
        this.resizeVolumeBar(event);
    },

    volumeControl: function (event) {
        this.volumeMouseDown = true;
        this.resizeVolumeBar(event);
    },

    like: function (event) {
        var songId = this.model.get('id');
        var url = '/api/v1/song/' + songId + '/liker/';
        $.post(url);
    },

    displayRadio: function (event) {
        event.preventDefault();
        var radio = Yasound.App.Router.currentRadio;
        if (radio) {
            var uuid = this.radio.get('uuid');
            if (uuid) {
                Yasound.App.Router.navigate("radio/" + uuid + '/', {
                    trigger: true
                });
            }
        }
    },

    facebookShare: function (event) {
        event.preventDefault();
        
        var link = Yasound.App.FacebookShare.link + 'radio/' + this.radio.get('uuid') + '/';
        var obj = {
            method: 'feed',
            link: link,
            picture: Yasound.App.FacebookShare.picture,
            name: gettext('Yasound share'),
            caption: this.generateFacebookText(),
            description: ''
        };
        console.log(obj)
        function callback (response) {
        }
        FB.ui(obj, callback);
    }
});
