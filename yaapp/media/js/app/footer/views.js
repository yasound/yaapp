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
        'click a.pl-cart': 'onBuy'
    },

    initialize: function () {
        _.bindAll(this,
            'render',
            'onRadioChanged',
            'onPlayerStop');
        $.subscribe('/current_radio/change', this.onRadioChanged);
        $.subscribe('/player/play', this.onPlayerPlay);
        $.subscribe('/player/stop', this.onPlayerStop);
    },

    onClose: function () {
        $.unsubscribe('/current_radio/change', this.onRadioChanged);
        $.unsubscribe('/player/play', this.onPlayerPlay);
        $.unsubscribe('/player/stop', this.onPlayerStop);

        if (this.currentSong) {
            this.currentSong.unbind('change', this.render, this);
        }
    },

    render: function () {
        if (this.radio) {
            $('h2', this.el).text(this.radio.get('name'));

            if (this.currentSong) {
                var data = this.currentSong.toJSON();
                $('h1', this.el).text(data.title_wrapped);
            }

            if (this.radio.get('favorite')) {
                $('.pl-star', this.el).removeClass('off').addClass('on');
            } else {
                $('.pl-star', this.el).removeClass('on').addClass('off');
            }

        }

        return this;
    },

    toggleMiniPlayer: function (e) {
        e.preventDefault();
        this.$el.toggleClass('mini');
    },

    onRadioChanged: function (e, radio) {
        if (this.currentSong) {
            this.currentSong.unbind('change', this.render, this);
        }
        this.radio = radio;
        this.currentSong = radio.currentSong;

        this.currentSong.bind('change', this.render, this);
        this.render();
    },

    onPlayerPlay: function () {
        $('.cover i').removeClass('play').addClass('pause');
    },

    onPlayerStop: function () {
        $('.cover i').removeClass('pause').addClass('play');
    },

    onLike: function (e) {
        e.preventDefault();
        if (this.currentSong) {
            var songId = this.currentSong.get('id');
            var url = '/api/v1/song/' + songId + '/liker/';
            $.publish('/song/like', this.currentSong);
            $.post(url);
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
    }

});
