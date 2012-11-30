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
        'click a.cover': 'togglePlay'
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
    },

    render: function () {
        if (this.radio) {
            $('h2', this.el).text(this.radio.get('name'));

            var currentSong = this.radio.currentSong;
            if (currentSong) {
                var data = currentSong.toJSON();
                $('h1', this.el).text(data.title_wrapped);
            }
        }

        return this;
    },

    toggleMiniPlayer: function (e) {
        e.preventDefault();
        this.$el.toggleClass('mini');
    },

    onRadioChanged: function (e, radio) {
        this.radio = radio;
        this.render();
    },

    onPlayerPlay: function () {
        $('.cover i').removeClass('play').addClass('pause');
    },

    onPlayerStop: function () {
        $('.cover i').removeClass('pause').addClass('play');
    },

    togglePlay: function (e) {
        e.preventDefault();
        if (!Yasound.App.player.isPlaying()) {
            Yasound.App.player.play();
        } else {
            Yasound.App.player.stop();
        }
    }

});
