Namespace('Yasound.Views');

Yasound.Views.Radio = Backbone.View.extend({
    tagName : 'div',
    className : 'radio',
    events : {},

    initialize : function() {
        this.model.bind('change', this.render, this);
    },

    render : function() {
        $(this.el).html(ich.radioTemplate(this.model.toJSON()));
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

    render : function() {
        $(this.el).html(ich.trackTemplate(this.model.toJSON()));
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
            view.remove();
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
            this.views[0].remove();
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
        $(this.el).hide().html(ich.wallEventTemplate(this.model.toJSON())).fadeIn(200);
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
