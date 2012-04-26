Namespace('Yasound.Views');

Yasound.Views.UserMenu = Backbone.View.extend({
    el: '#user-menu',
    events: {
        'click #btn-my-radio': 'onMyRadio',
    },
    onMyRadio: function(e) {
        e.preventDefault();
        var uuid = $('#btn-my-radio', this.el).attr('yasound:uuid');
        Yasound.App.Router.navigate("radio/" + uuid, {
            trigger: true
        });
    }
});

Yasound.Views.WallInput = Backbone.View.extend({
    tagName: 'div',
    events: {
        'click #submit': 'submit',
        'click #refresh': 'refreshWall'
    },

    submit: function(e) {
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

    refreshWall: function(e) {
        $.publish('/wall/posted');
        e.preventDefault();
    },

    initialize: function() {
    },

    render: function() {
        $(this.el).html(ich.wallInputTemplate());
        return this;
    }
});

Yasound.Views.Radio = Backbone.View.extend({
    tagName: 'div',
    className: 'radio',
    events: {
        "click #btn-favorite": "addToFavorite",
        "click #btn-unfavorite": "removeFromFavorite"
    },

    initialize: function() {
        this.model.bind('change', this.render, this);
    },
    onClose: function() {
        this.model.unbind('change', this.render);
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

    render: function() {
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
    tagName: 'div',
    className: 'track',
    volumeMouseDown: false,

    events: {
        "click #play": "play",
        "click #inc": "inc",
        "click #dec": "dec",
        "click #like": "like",
        "mousedown #volume-control": "volumeControl",
        "mouseup": 'mouseUp',
        "mousemove": "mouseMove"
    },

    initialize: function() {
        this.model.bind('change', this.render, this);
    },

    onClose: function() {
        this.model.unbind('change', this.render);
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
                url: '' + window.location,
                text: this.generateTwitterText(),
                hashtags: 'yasound'
            };
            $('#tweet', this.el).show();
            $('#tweet', this.el).attr('href', "http://twitter.com/share?" + $.param(twitterParams));
            $('meta[name=description]').attr('description', this.generateFacebookText());
        }
    },

    render: function() {
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

    play: function() {
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

    inc: function() {
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

    dec: function() {
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

    resizeVolumeBar: function(event) {
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

    mouseUp: function(event) {
        if (this.volumeMouseDown) {
            $('body').css('cursor', 'auto');
            this.volumeMouseDown = false;
        }
    },

    mouseMove: function(event) {
        if (!this.volumeMouseDown) {
            return;
        }
        this.resizeVolumeBar(event);
    },

    volumeControl: function(event) {
        this.volumeMouseDown = true;
        this.resizeVolumeBar(event);
    },

    like: function(event) {
        var songId = this.model.get('id');
        var url = '/api/v1/song/' + songId + '/liker/';
        $.post(url);
    }
});

Yasound.Views.WallEvents = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this, 'addOne', 'addAll');

        this.collection.bind('add', this.addOne);
        this.collection.bind('reset', this.addAll, this);
        this.views = [];
    },

    addAll: function() {
        this.collection.each(this.addOne);
    },

    clear: function() {
        _.map(this.views, function(view) {
            view.close();
        })
        this.views = [];
    },

    addOne: function(wallEvent) {
        var view = new Yasound.Views.WallEvent({
            model: wallEvent
        });

        $(this.el).prepend(view.render().el);
        this.views.push(view);

        if (this.views.length >= this.collection.limit) {
            this.views[0].close();
            this.views.splice(0, 1)
        }

        view.bind('all', this.rethrow, this);
    },

    rethrow: function() {
        this.trigger.apply(this, arguments);
    }

});

Yasound.Views.PaginatedWallEvents = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this, 'addOne', 'addAll');

        this.collection.bind('add', this.addOne, this);
        this.collection.bind('reset', this.addAll, this);
        this.views = [];
    },
    
    onClose: function() {
        this.collection.unbind('add', this.addOne);
        this.collection.unbind('reset', this.addAll);
    },

    addAll: function() {
        this.collection.each(this.addOne);
    },

    clear: function() {
        _.map(this.views, function(view) {
            view.close();
        })
        this.views = [];
    },

    addOne: function(wallEvent) {
        var currentId = wallEvent.id;

        var found = _.find(this.views, function(view) {
            if (view.model.id == wallEvent.id) {
                return true;
            }
        })
        if (found) {
            // do not insert duplicated content
            return;
        }

        var view = new Yasound.Views.WallEvent({
            model: wallEvent
        });

        var lastView = _.max(this.views, function(view) {
            return view.model.get('id');
        });
        var lastId = 0;
        if (lastView) {
            var lastId = lastView.model.id;
        }
        if (currentId >= lastId) {
            $(this.el).prepend(view.render().el);
            // in case of prepend, it means that the wall has been refreshed
            // with new item
            // so we remove the last one in order to avoid infinite addition to
            // the wall
            if (this.views.length >= this.collection.perPage) {
                this.views[0].close();
                this.views.splice(0, 1)
            }
        } else {
            $(this.el).append(view.render().el);
        }

        this.views.push(view);

    }
});

Yasound.Views.Pagination = Backbone.View.extend({
    events: {
        'click a.servernext': 'nextResultPage',
        'click a.serverprevious': 'previousResultPage',
        'click a.orderUpdate': 'updateSortBy',
        'click a.serverlast': 'gotoLast',
        'click a.page': 'gotoPage',
        'click a.serverfirst': 'gotoFirst',
        'click a.serverpage': 'gotoPage',
        'click .serverhowmany a': 'changeCount'

    },

    tagName: 'aside',

    initialize: function() {
        this.collection.on('reset', this.render, this);
        this.collection.on('change', this.render, this);
    },
    
    onClose: function() {
        this.collection.unbind('change', this.render);
        this.collection.unbind('reset', this.render);
    },

    render: function() {
        var info = this.collection.info();
        var page = info.page;
        var totalPages = info.totalPages;
        if (page < totalPages) {
            this.$el.html(ich.paginationTemplate());
        } else {
            this.$el.html('');
        }
    },

    updateSortBy: function(e) {
        e.preventDefault();
        var currentSort = $('#sortByField').val();
        this.collection.updateOrder(currentSort);
    },

    nextResultPage: function(e) {
        e.preventDefault();
        this.collection.requestNextPage();
    },

    previousResultPage: function(e) {
        e.preventDefault();
        this.collection.requestPreviousPage();
    },

    gotoFirst: function(e) {
        e.preventDefault();
        this.collection.goTo(this.collection.information.firstPage);
    },

    gotoLast: function(e) {
        e.preventDefault();
        this.collection.goTo(this.collection.information.lastPage);
    },

    gotoPage: function(e) {
        e.preventDefault();
        var page = $(e.target).text();
        this.collection.goTo(page);
    },

    changeCount: function(e) {
        e.preventDefault();
        var per = $(e.target).text();
        this.collection.howManyPer(per);
    }

});

Yasound.Views.WallEvent = Backbone.View.extend({
    tagName: 'li',
    className: 'wall-event',

    events: {},

    initialize: function() {
        this.model.bind('change', this.render, this);
    },
    
    onClose: function() {
        this.model.unbind('change', this.render);
    },
    
    render: function() {
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

Yasound.Views.RadioUsers = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this, 'addOne', 'addAll', 'clear');

        this.collection.bind('add', this.addOne);
        this.collection.bind('reset', this.addAll);
        this.views = [];
    },
    
    onClose: function() {
        this.collection.unbind('add', this.addOne);
        this.collection.unbind('reset', this.addAll);
    },

    addAll: function() {
        this.clear();
        this.collection.each(this.addOne);
    },

    clear: function() {
        _.map(this.views, function(view) {
            view.close();
        })
        this.views = [];
    },

    addOne: function(radioUser) {
        var view = new Yasound.Views.RadioUser({
            model: radioUser
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
    tagName: 'li',
    className: 'radio-user',
    events: {},
    initialize: function() {
        this.model.bind('change', this.render, this);
    },

    onClose: function() {
        this.model.unbind('change', this.render);
    },
    
    render: function() {
        var data = this.model.toJSON();
        $(this.el).hide().html(ich.radioUserTemplate(data)).fadeIn(200);
        return this;
    }
});

Yasound.Views.RadioPage = Backbone.View.extend({
    name: 'radiopage',
    radioUsers: new Yasound.Data.Models.RadioUsers({}),
    wallEvents: new Yasound.Data.Models.PaginatedWallEvents({}),
    intervalId: undefined,
    wallPosted: undefined,

    initialize: function() {
        this.model.bind('change', this.render, this);
    },
    
    onClose: function() {
        this.model.unbind('change', this.render);
    },

    reset: function() {
        if (this.wallPosted) {
            $.unsubscribe('/wall/posted', this.wallPosted);
        }
        if (this.intervalId) {
            clearInterval(this.intervalId);
        }
        if (this.wallInputView) {
            this.wallInputView.close();
        }
        if (this.radioView) {
            this.radioView.close();
        }
        if (this.radioUsersView) {
            this.radioUsersView.clear();
            this.radioUsersView.close();
        }
        if (this.wallEventsView) {
            this.wallEventsView.clear();
            this.wallEventsView.close();
        }
        if (this.paginationView) {
            this.paginationView.close();
        }

        this.wallEvents.reset();
        this.radioUsers.reset();
    },

    render: function() {
        this.reset();

        var that = this;
        var wallPosted = function() {
            that.wallEvents.page = 0;
            that.wallEvents.fetch();
        }
        this.wallPosted = wallPosted;
        $.subscribe("/wall/posted", wallPosted);

        $(this.el).html(ich.radioPageTemplate());

        this.wallInputView = new Yasound.Views.WallInput({
            model: this.model,
            el: $('#webapp-wall-input', this.el)
        });
        this.wallInputView.radioUUID = this.model.get('uuid');

        this.radioView = new Yasound.Views.Radio({
            model: this.model,
            el: $('#webapp-radio', this.el)
        })

        this.radioUsers.radio = this.model;
        this.radioUsersView = new Yasound.Views.RadioUsers({
            collection: this.radioUsers,
            el: $('#webapp-radio-users', this.el)
        });

        this.wallEventsView = new Yasound.Views.PaginatedWallEvents({
            collection: this.wallEvents,
            el: $('#wall', this.el)
        });
        this.wallEvents.setRadio(this.model);

        this.paginationView = new Yasound.Views.Pagination({
            collection: this.wallEvents,
            el: $('#pagination', this.el)
        });

        if (this.model.get('id')) {
            this.wallEvents.fetch();
            this.radioUsers.fetch();
        }

        this.wallInputView.render();
        this.radioView.render();
        this.wallEventsView.render();
        this.paginationView.render();

        this.intervalId = setInterval(function() {
            that.wallEvents.fetchFirst();
        }, 10000);
        
        return this;
    }
});
