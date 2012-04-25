Namespace('Yasound.Views');

Yasound.Views.Radio = Backbone.View.extend({
    tagName : 'div',
    className : 'radio',
    events : {
        "click #btn-favorite": "addToFavorite",
        "click #btn-unfavorite": "removeFromFavorite"
    },

    initialize : function() {
        this.model.bind('change', this.render, this);
    },

    addToFavorite: function(e) {
        var url = '/api/v1/radio/' + this.model.get('id') + '/favorite/';
        $.post(url, {
            success: function() { 
                $('#btn-favorite', this.el).hide();
                $('#btn-unfavorite', this.el).show();
                $.publish('/radio/favorite');
            }
        });
        e.preventDefault();
    },
    
    removeFromFavorite: function(e) {
        var url = '/api/v1/radio/' + this.model.get('id') + '/not_favorite/';
        $.post(url, {
            success: function() { 
                $('#btn-unfavorite', this.el).hide();
                $('#btn-favorite', this.el).show();
                $.publish('/radio/not_favorite');
            }
        });
        e.preventDefault();
    },
    
    render : function() {
        $(this.el).html(ich.radioTemplate(this.model.toJSON()));
        if (this.model.get('favorite')) {
            $('#btn-favorite', this.el).hide();
            $('#btn-unfavorite', this.el).show();
        } else {
            $('#btn-unfavorite', this.el).hide();
            $('#btn-favorite', this.el).show();
        }
        return this;
    }
});

Yasound.Views.CurrentSong = Backbone.View.extend({
    tagName : 'div',
    className : 'track',
    volumeMouseDown : false,

    events : {
        "click #play" : "play",
        "click #inc" : "inc",
        "click #dec" : "dec",
        "click #like" : "like",
        "mousedown #volume-control" : "volumeControl",
        "mouseup" : 'mouseUp',
        "mousemove" : "mouseMove"
    },

    initialize : function() {
        this.model.bind('change', this.render, this);
    },
    
    generateTwitterText: function() {
        if (!this.radio) {
            return '';
        }
        
        var share = gettext('I am listening to');
        share += ' ' + this.model.get('name') + ', ';
        share += gettext('by') + ' ' + this.model.get('artist') + ' ';
        share += gettext('on') + ' ' + this.radio.get('name');
        return share;
    },
    
    generateFacebookText: function() {
        return this.generateTwitterText();
    },
    
    generateSocialShare: function() {
        if (!this.radio) {
            $('#tweet').hide();    
        } else {
            var twitterParams = { 
                    url:  '' + window.location, 
                    text: this.generateTwitterText(),
                    hashtags: 'yasound'
                };
            $('#tweet', this.el).show(); 
            $('#tweet', this.el).attr('href', "http://twitter.com/share?" + $.param(twitterParams));
            $('meta[name=description]').attr('description', this.generateFacebookText());
        }
    },
    
    render : function() {
        $(this.el).html(ich.trackTemplate(this.model.toJSON()));
        this.generateSocialShare();

        if (Yasound.App.MySound) {
            if (Yasound.App.MySound.playState == 1) {
                $('#play i').removeClass('icon-play').addClass('icon-stop');
            }
            $('#volume-position').css("width", Yasound.App.MySound.volume + "%");
        }
        return this;
    },

    play : function() {
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

    inc : function() {
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
    },

    dec : function() {
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
    },

    resizeVolumeBar : function(event) {
        if (typeof Yasound.App.MySound === "undefined") {
            return;
        }
        $('body').css('cursor', 'pointer');
        var $volumeControl = $('#volume-control');
        var position = event.pageX;
        var left = $volumeControl.position().left;
        var width = $volumeControl.width();

        var relativePosition = position - left;
        var soundVolume = Math.floor(relativePosition * 100 / width)
        var percentage = soundVolume + "%";
        $('#volume-position').css("width", percentage);

        Yasound.App.MySound.setVolume(soundVolume);
    },

    mouseUp : function(event) {
        if (this.volumeMouseDown) {
            $('body').css('cursor', 'auto');
            this.volumeMouseDown = false;
        }
    },

    mouseMove : function(event) {
        if (!this.volumeMouseDown) {
            return;
        }
        this.resizeVolumeBar(event);
    },

    volumeControl : function(event) {
        this.volumeMouseDown = true;
        this.resizeVolumeBar(event);
    },

    like : function(event) {
        var songId = this.model.get('id');
        var url = '/api/v1/song/' + songId + '/liker/';
        $.post(url);
    }
});

Yasound.Views.WallEvents = Backbone.View.extend({
    initialize : function() {
        _.bindAll(this, 'addOne', 'addAll');

        this.collection.bind('add', this.addOne);
        this.collection.bind('reset', this.addAll, this);
        this.views = [];
    },

    addAll : function() {
        this.collection.each(this.addOne);
    },

    clear : function() {
        _.map(this.views, function(view) {
            view.close();
        })
        this.views = [];
    },

    addOne : function(wallEvent) {
        var view = new Yasound.Views.WallEvent({
            model : wallEvent
        });

        $(this.el).prepend(view.render().el);
        this.views.push(view);

        if (this.views.length >= this.collection.limit) {
            this.views[0].close();
            this.views.splice(0, 1)
        }

        view.bind('all', this.rethrow, this);
    },

    rethrow : function() {
        this.trigger.apply(this, arguments);
    }

});

Yasound.Views.WallEvent = Backbone.View.extend({
    tagName : 'li',
    className : 'wall-event',

    events : {},

    initialize : function() {
        this.model.bind('change', this.render, this);
    },
    render : function() {
        var data = this.model.toJSON();
        var timeZone = '+01:00';
        if (moment().isDST()) {
            timeZone = '+02:00';
        }
        var date = moment(this.model.get('start_date') + timeZone);
        data.formatted_start_date = date.format('LLLL');

        if (this.model.get('type') == 'M') {
            $(this.el).hide().html(ich.wallEventTemplateMessage(data)).fadeIn(200);
        } else if (this.model.get('type') == 'S') {
            $(this.el).hide().html(ich.wallEventTemplateSong(data)).fadeIn(200);
        } else if (this.model.get('type') == 'L') {
            $(this.el).hide().html(ich.wallEventTemplateLike(data)).fadeIn(200);
        }
        return this;
    }
});

Yasound.Views.WallInput = Backbone.View.extend({
    tagName : 'div',
    events : {
        'click .btn' : 'submit'
    },
    
    submit : function(e) {
        var $button = $('.btn', this.el);
        $button.attr('disabled', 'disable')
        if (this.radioUUID) {
            var $input = $('input[type=text]', this.el)
            var message = $input.val();
            var url = '/api/v1/radio/' + this.radioUUID + '/post_message/';
            $.post(url, {
                message: message,
                success: function() { 
                    $input.val('');  
                    $button.removeAttr('disabled');
                    $.publish('/wall/posted');
                }
            });
        } else {
            alert('no radio!')
        }
        e.preventDefault();
    },
    
    initialize : function() {
    },

    render : function() {
        $(this.el).html(ich.wallInputTemplate());
        return this;
    }
});


Yasound.Views.RadioUsers = Backbone.View.extend({
    initialize : function() {
        _.bindAll(this, 'addOne', 'addAll');

        this.collection.bind('add', this.addOne);
        this.collection.bind('reset', this.addAll, this);
        this.views = [];
    },

    addAll : function() {
        this.collection.each(this.addOne);
    },

    clear : function() {
        _.map(this.views, function(view) {
            view.close();
        })
        this.views = [];
    },

    addOne : function(radioUser) {
        var view = new Yasound.Views.RadioUser({
            model : radioUser
        });

        $(this.el).prepend(view.render().el);
        this.views.push(view);

        if (this.views.length >= this.collection.limit) {
            this.views[0].close();
            this.views.splice(0, 1)
        }
    }
});

Yasound.Views.RadioUser = Backbone.View.extend({
    tagName : 'li',
    className : 'radio-user',
    events : {},
    initialize : function() {
        this.model.bind('change', this.render, this);
    },
    render : function() {
        var data = this.model.toJSON();
        $(this.el).hide().html(ich.radioUserTemplate(data)).fadeIn(200);
        return this;
    }
});
