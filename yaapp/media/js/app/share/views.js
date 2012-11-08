/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Views');

Yasound.Views.Share = Backbone.View.extend({

    events: {
        "click #fb_share": "onFacebookShare",
        "mouseup #widget": "selectAll",
        "click #check-auto-play": "checkAutoplay",
        "click #check-large": "checkLarge",
        "mouseup #stream": "selectAll"
    },

    initialize: function() {
        this.large = true;
        this.autoPlay = true;
        _.bindAll(this, 'render',
            'generateSocialShare',
            'generateTwitterText',
            'radioUrl',
            'generateFacebookText',
            'refreshWidgetCode');
    },

    onClose: function() {
    },

    reset: function() {
    },

    render: function(radio) {
        this.reset();
        this.radio = radio;
        $(this.el).html(ich.sharePageTemplate(radio.toJSON()));

        this.generateSocialShare();
        this.refreshWidgetCode();
        return this;
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

    radioUrl: function () {
        if (!this.radio) {
            return '';
        }

        var protocol = window.location.protocol;
        var host = window.location.host;

        var url =  protocol + '//' + host + Yasound.App.root + 'radio/' + this.radio.get('uuid');
        return url;
    },

    generateFacebookText: function () {
        return this.generateTwitterText();
    },

    generateSocialShare: function () {
        if (!this.radio) {
            $('#tw_share').hide();
        } else {
            var twitterParams = {
                url: this.radioUrl(),
                text: this.generateTwitterText(),
                hashtags: 'yasound'
            };
            $('#tw_share').show();
            $('#tw_share').attr('href', "http://twitter.com/share?" + $.param(twitterParams));
            $('meta[name=description]').attr('description', this.generateFacebookText());
        }
    },

    onFacebookShare: function (e) {
        e.preventDefault();
        var link = Yasound.App.FacebookShare.link + 'radio/' + this.radio.get('uuid') + '/';
        var name = this.radio.get('name');
        var creatorName = this.radio.get('creator')['name'];
        if (creatorName !== '') {
            name =  name +  ' ' + gettext('by') + ' ' + this.radio.get('creator')['name'];
        }
        var obj = {
            method: 'feed',
            display: 'popup',
            link: link,
            picture: Yasound.App.FacebookShare.picture,
            name: name,
            caption: this.generateFacebookText(),
            description: ''
        };
        function callback (response) {
        }
        FB.ui(obj, callback);
    },

    selectAll: function (e) {
        $(e.target).select();
    },

    checkAutoplay: function (e) {
        if ($(e.target).attr('checked')) {
            this.autoPlay = true;
        } else {
            this.autoPlay = false;
        }
        this.refreshWidgetCode();
    },

    checkLarge: function (e) {
        if ($(e.target).attr('checked')) {
            this.large = true;
        } else {
            this.large = false;
        }
        this.refreshWidgetCode();
    },

    refreshWidgetCode: function () {
        var url = 'https://yasound.com/widget/' + this.radio.get('uuid') + '/';
        if (this.large) {
            url = url + 'large';
        }
        if (this.autoPlay) {
            url = url + '?autoplay=1';
        }
        var size = 380;
        if (this.large) {
            size = 280;
        }
        code = '<iframe frameborder="0" height="' + size + '" scrolling="no" src="' + url + '"></iframe>';
        $('#widget').val(code);
        this.code = code;
    }
});