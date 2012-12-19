/*
 * jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true,
 * evil: true, undef: true, white: true, newcap: true
 */
/* extern Ext, $ */

Namespace('Yasound.Views');

Yasound.Views.Footer = Backbone.View.extend({
    el: '.footer-player',

    events: {
        'click a.toggler': 'toggleMiniPlayer',
        'click a.cover': 'togglePlay',
        'click a.pl-star': 'toggleFavorite',
        'click a.pl-like': 'onLike',
        'click a.pl-cart': 'onBuy',
        'click .pl-volume': 'toggleVolume',
        'click .wrapper': 'gotoRadio'
    },

    initialize: function () {
        _.bindAll(this,
            'render',
            'renderRadio',
            'renderSong',
            'renderVolume',
            'onRadioChanged',
            'onPlayerStop',
            'toggleVolume',
            'onVolumeSlide',
            'gotoRadio',
            'onShare',
            'onFavoriteChanged');

        $.subscribe('/current_radio/change', this.onRadioChanged);
        $.subscribe('/current_radio/favorite_change', this.onFavoriteChanged);
        $.subscribe('/player/play', this.onPlayerPlay);
        $.subscribe('/player/stop', this.onPlayerStop);
        $('#modal-share').on('show', this.onShare);
    },

    onClose: function () {
        $.unsubscribe('/current_radio/change', this.onRadioChanged);
        $.unsubscribe('/player/play', this.onPlayerPlay);
        $.unsubscribe('/player/stop', this.onPlayerStop);
        $.unsubscribe('/current_radio/favorite_change', this.onFavoriteChanged);

        if (this.currentSong) {
            this.currentSong.unbind('change', this.renderSong, this);
        }
        $('#modal-share').off('show', this.onShare);
    },

    render: function () {
        this.renderRadio();
        this.renderSong();
        this.renderVolume();
        return this;
    },

    renderRadio: function() {
        if (this.radio) {
            $('.current-radio h2', this.el).text(this.radio.get('name'));
            $('.current-radio .cover img', this.el).attr('src', this.radio.get('picture'));
            if (this.radio.get('favorite')) {
                $('.pl-star', this.el).removeClass('off').addClass('on');
            } else {
                $('.pl-star', this.el).removeClass('on').addClass('off');
            }

        }
    },

    renderSong: function () {
        if (this.currentSong) {
            var data = this.currentSong.toJSON();
            $('.current-song h1', this.el).text(data.title_wrapped);
            $('.current-song img', this.el).attr('src', data.cover);
        }
    },

    renderVolume: function() {
        var volumeSlider = this.$('#volume-slider');
        volumeSlider.slider({
            orientation: "vertical",
            range: "min",
            min: 0,
            max: 100
        });
        volumeSlider.bind('slide', this.onVolumeSlide);
        volumeSlider.slider('value', Yasound.App.player.volume());
        this.setVolumeThreshold(Yasound.App.player.volume());
    },

    toggleMiniPlayer: function (e) {
        e.preventDefault();
        this.$el.toggleClass('mini');
    },

    onRadioChanged: function (e, radio) {
        if (this.currentSong) {
            this.currentSong.unbind('change', this.renderSong, this);
        }
        this.radio = radio;
        this.currentSong = radio.currentSong;

        this.currentSong.bind('change', this.renderSong, this);
        this.renderRadio();
    },

    onPlayerPlay: function () {
        $('.cover i').removeClass('play').addClass('pause');
    },

    onPlayerStop: function () {
        $('.cover i').removeClass('pause').addClass('play');
    },

    onFavoriteChanged: function (e, favorite) {
        this.radio.set('favorite', favorite);
        this.render();
    },

    onLike: function (e) {
        e.preventDefault();
        if (this.currentSong) {
            var songId = this.currentSong.get('id');
            var radioUUID = this.radio.get('uuid');

            var data = {
                'last_play_time': this.currentSong.get('last_play_time')
            };
            var url = '/api/v1/radio/' + radioUUID + '/likes/';
            $.ajax({
               url: url,
               type: 'POST',
               dataType: 'json',
               data: JSON.stringify(data)
            });
        }
    },

    onBuy: function (e) {
        e.preventDefault();
        if (!this.currentSong) {
            return;
        }
        var link = this.currentSong.get('buy_link');
        window.open(link);
    },

    togglePlay: function (e) {
        e.preventDefault();
        if (!Yasound.App.player.isPlaying()) {
            Yasound.App.player.play();
        } else {
            Yasound.App.player.stop();
        }
    },

    toggleFavorite: function (e) {
        e.preventDefault();
        var radio = this.radio;
        if (!radio) {
            return;
        }
        if (radio.get('favorite')) {
            radio.removeFromFavorite();
            $('.pl-star', this.el).removeClass('on').addClass('off');
        } else {
            radio.addToFavorite();
            $('.pl-star', this.el).removeClass('off').addClass('on');
        }
    },

    toggleVolume: function(e) {
        e.stopPropagation();
        var $target = this.$('.pl-volume');

        if($target.hasClass('open')) {
            $target.removeClass('open');
            $('html').unbind('click', this.toggleVolume);
        } else {
            $target.addClass('open');
            $('html').bind('click', this.toggleVolume);
        }
    },

    onVolumeSlide: function(e, ui) {
        this.setVolumeThreshold(ui.value);
        Yasound.App.player.setVolume(ui.value);
    },

    setVolumeThreshold: function(val) {

        var step = 25,
            classes = [],
            threshold;

        for(var i=0 ; i<=100 ; i=i+step) {
            classes.push('vol'+i);
            if(threshold === undefined && val <= i) threshold = i;
        }

        this.$('.pl-volume').removeClass(classes.join(' ')).addClass('vol' + threshold);

    },

    gotoRadio: function(e) {

        // Check if there is no link clicked.
        // Check if volume slider is not open.
        if($(e.target).closest('a').length === 0 && !this.$('.pl-volume').hasClass('open')) {
            Yasound.App.Router.navigate("radio/" + this.radio.get('uuid') + '/', {
                trigger: true
            });
        }
    },

    onShare: function (e) {
        if (this.currentSong.get('id')) {
            var el = $('#modal-share .modal-body');
            if (!this.shareView) {
                this.shareView = new Yasound.Views.Share({
                    el: el,
                    model: this.currentSong
                });
            }
            this.shareView.render(this.radio);
        } else {
            Yasound.Utils.dialog(gettext('Error'), gettext('Nothing to share'));
        }

    }

});
