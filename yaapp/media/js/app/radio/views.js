/*
 * jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true,
 * evil: true, undef: true, white: true, newcap: true
 */
/* extern Ext, $ */
Namespace('Yasound.Views');

Yasound.Views.WallInput = Backbone.View.extend({
    tagName: 'div',
    events: {
        "click #submit"                 : "submit",
        "click #refresh"                : "refreshWall",
        "keypress #wall-input-textarea" : "onWallInputChanged"
    },

    submit: function (e) {
        var $button = $('.btn', this.el);
        $button.attr('disabled', 'disable');
        if (this.radioUUID) {
            var $input = $('textarea[type=textarea]', this.el);
            var message = $input.val();
            if (message.length > 0) {
                var url = '/api/v1/radio/' + this.radioUUID + '/post_message/';
                $.post(url, {
                    message: message,
                    success: function () {
                        $input.val('');
                        $.publish('/wall/posted');
                    }
                });
            }
        } else {
            alert('no radio!');
        }
        e.preventDefault();
    },

    onWallInputChanged: function (e) {
        var val = $(e.target).val();
        if (val.length > 0) {
            $('#submit').removeAttr('disabled');
        }
    },

    refreshWall: function (e) {
        $.publish('/wall/posted');
        e.preventDefault();
    },

    initialize: function () {
    },

    render: function () {
        $(this.el).html(ich.wallInputTemplate());
        return this;
    }
});

Yasound.Views.Radio = Backbone.View.extend({
    tagName: 'div',
    className: 'radio',
    events: {
        "click #btn-favorite": "addToFavorite",
        "click #btn-unfavorite": "removeFromFavorite",
        "click #user": "selectUser",
        "click #radio-actions-container #like-btn": "onLike",
        "click #radio-actions-container #settings-btn": "onSettings",
        "click #radio-actions-container #programming-btn": "onProgramming",
        "click #radio-actions-container #broadcast-btn": "onBroadcast"
    },

    initialize: function () {
        this.model.bind('change', this.render, this);
    },
    onClose: function () {
        this.model.unbind('change', this.render);
    },

    addToFavorite: function (e) {
        var url = '/api/v1/radio/' + this.model.get('id') + '/favorite/';
        var that = this;
        $.post(url, {
            success: function () {
                $('#btn-favorite', that.el).hide();
                $('#btn-unfavorite', that.el).show();
                $.publish('/radio/favorite');
            }
        });
        e.preventDefault();
    },

    removeFromFavorite: function (e) {
        var url = '/api/v1/radio/' + this.model.get('id') + '/not_favorite/';
        var that = this;
        $.post(url, {
            success: function () {
                $('#btn-unfavorite', that.el).hide();
                $('#btn-favorite', that.el).show();
                $.publish('/radio/not_favorite');
            }
        });
        e.preventDefault();
    },
    selectUser: function (event) {
        event.preventDefault();
        Yasound.App.Router.navigate("profile/" + this.model.get('creator').username + '/', {
            trigger: true
        });
    },

    render: function () {
        $(this.el).html(ich.radioTemplate(this.model.toJSON()));
        if (this.model.get('favorite')) {
            $('#btn-favorite', this.el).hide();
            $('#btn-unfavorite', this.el).show();
        } else {
            $('#btn-unfavorite', this.el).hide();
            $('#btn-favorite', this.el).show();
        }
        return this;
    },

    onLike: function (e) {
        e.preventDefault();
        if (this.model.currentSong) {
            this.model.currentSong.like();
        }
    },

    onSettings: function (e) {
        e.preventDefault();
        Yasound.App.Router.navigate("radio/" + this.model.get('uuid') + '/edit/', {
            trigger: true
        });
    },

    onProgramming: function (e) {
        e.preventDefault();
        Yasound.App.Router.navigate("radio/" + this.model.get('uuid') + '/programming/', {
            trigger: true
        });
    },

    onBroadcast: function (e) {
        e.preventDefault();
        var that = this;
        var $textarea = $('#modal-broadcast textarea');

        $('#modal-broadcast').modal('show');
        $('#modal-broadcast').one('shown', function() {
            $textarea.focus();
        });

        $('#modal-broadcast .btn-primary').one('click', function () {
            $('#modal-broadcast').modal('hide');
            that.model.broadcast($textarea.val());
        });
    }
});

Yasound.Views.RadioInfos = Backbone.View.extend({
    tagName: 'div',
    events: {
    },

    initialize: function () {
        this.model.bind('change', this.render, this);
    },
    onClose: function () {
        this.model.unbind('change', this.render);
    },

    render: function () {
        $(this.el).html(ich.radioInfosTemplate(this.model.toJSON()));
        return this;
    }
});

Yasound.Views.TrackInRadio = Backbone.View.extend({
    tagName: 'div',
    className: 'track',
    events: {
    },

    initialize: function () {
        this.model.bind('change', this.render, this);
    },
    onClose: function () {
        this.model.unbind('change', this.render);
    },
    render: function () {
        $(this.el).html(ich.trackInRadioTemplate(this.model.toJSON()));
        return this;
    }
});

Yasound.Views.PaginatedWallEvents = Backbone.View.extend({
    initialize: function () {
        _.bindAll(this, 'addOne', 'addAll', 'beforeFetch');

        this.collection.bind('beforeFetch', this.beforeFetch, this);
        this.collection.bind('add', this.addOne, this);
        this.collection.bind('reset', this.addAll, this);
        this.views = [];
    },

    onClose: function () {
        this.collection.unbind('beforeFetch', this.beforeFetch);
        this.collection.unbind('add', this.addOne);
        this.collection.unbind('reset', this.addAll);
    },

    beforeFetch: function() {
        if (this.loadingMask) {
            $(this.el).append(this.loadingMask);
        }
    },

    addAll: function() {
        var mask = $('.loading-mask', this.el);
        if (!this.loadingMask) {
            this.loadingMask = mask;
        }
        mask.remove();
        this.collection.each(this.addOne);
        if (this.collection.length === 0) {
            $('.empty').show();
        } else {
            $('.empty').hide();
        }
    },

    clear: function () {
        _.map(this.views, function (view) {
            view.close();
        });
        // remove all existing items inside the view (bootstraped data for instance)
        $(this.el).html('');
        this.views = [];
    },

    addOne: function (wallEvent) {
        var currentId = wallEvent.id;

        var found = _.find(this.views, function (view) {
            if (view.model.id == wallEvent.id) {
                return true;
            }
        });
        if (found) {
            // do not insert duplicated content
            return;
        }
        wallEvent.set('creator', this.collection.radio.get('creator').owner);
        var view = new Yasound.Views.WallEvent({
            model: wallEvent
        });

        var insertOnTop = false;
        if (this.views.length > 0) {
            var lastId = parseInt(this.views[0].model.get('id'), 10);
            currentId = parseInt(wallEvent.id, 10);
            if (currentId > lastId) {
                insertOnTop = true;
            }
        }

        if (insertOnTop) {
            $(this.el).prepend(view.render().el);
            // in case of prepend, it means that the wall has been refreshed
            // with new item
            // so we remove the last one in order to avoid infinite addition to
            // the wall
            if (this.views.length >= this.collection.perPage) {
                var lastView = this.views.pop();
                lastView.close();
            }
            this.views.splice(0,0, view);
        } else {
            $(this.el).append(view.render().el);
            this.views.push(view);
        }
    },

    removeView: function(view) {
        view.close();
        this.views = _.without(this.views, view);
    }
});


Yasound.Views.WallEvent = Backbone.View.extend({
    tagName: 'li',
    className: 'wall-event',
    events: {
        'click h2 a': 'selectUser',
        'click #report-abuse-btn': 'reportAbuse',
        'click #delete-btn': 'deleteMessage'
    },

    initialize: function () {
        this.model.bind('change', this.render, this);
    },

    onClose: function () {
        this.model.unbind('change', this.render);
    },

    render: function () {
        var data = this.model.toJSON();
        var timeZone = '+01:00';
        if (moment().isDST()) {
            timeZone = '+02:00';
        }
        // if start_date contains microsecond precision, we remove it
        var start_date = this.model.get('start_date').substr(0, 19);
        var date = moment(start_date + timeZone);
        data.formatted_start_date= date.format('LLL');

        if (this.model.get('type') == 'M') {
            if (Yasound.App.enableFX) {
                $(this.el).hide().html(ich.wallEventTemplateMessage(data)).fadeIn(200);
            } else {
                $(this.el).html(ich.wallEventTemplateMessage(data));
            }
        } else if (this.model.get('type') == 'S') {
            if (Yasound.App.enableFX) {
                $(this.el).hide().html(ich.wallEventTemplateSong(data)).fadeIn(200);
            } else {
                $(this.el).html(ich.wallEventTemplateSong(data));
            }
        } else if (this.model.get('type') == 'L') {
            if (Yasound.App.enableFX) {
                $(this.el).hide().html(ich.wallEventTemplateLike(data)).fadeIn(200);
            } else {
                $(this.el).html(ich.wallEventTemplateLike(data));
            }
        }
        return this;
    },

    selectUser: function (event) {
        event.preventDefault();
        Yasound.App.Router.navigate("profile/" + this.model.get('user_username') + '/', {
            trigger: true
        });
    },

    reportAbuse: function (e) {
        e.preventDefault();
        var that = this;
        $('#modal-report-abuse').modal('show');
        $('#modal-report-abuse .btn-primary').one('click', function () {
            $('#modal-report-abuse').modal('hide');
            that.model.reportAbuse();
        });
    },

    deleteMessage: function (e) {
        e.preventDefault();
        var that = this;
        $('#modal-delete-message').modal('show');
        $('#modal-delete-message .btn-primary').one('click', function () {
            $('#modal-delete-message').modal('hide');
            that.model.deleteMessage();
        });
    }
});

Yasound.Views.RadioUsers = Backbone.View.extend({
    initialize: function () {
        _.bindAll(this, 'addOne', 'addAll', 'clear');

        this.collection.bind('add', this.addOne);
        this.collection.bind('reset', this.addAll);
        this.views = [];
    },

    onClose: function () {
        this.collection.unbind('add', this.addOne);
        this.collection.unbind('reset', this.addAll);
    },

    addAll: function () {
        this.clear();
        this.collection.each(this.addOne);
    },

    clear: function () {
        _.map(this.views, function (view) {
            view.close();
        });
        this.views = [];
    },

    addOne: function (radioUser) {
        var found = _.find(this.views, function (view) {
            if (view.model.id == radioUser.id) {
                return true;
            }
        });

        if (found) {
            // do not insert duplicated content
            return;
        }

        var view = new Yasound.Views.RadioUser({
            model: radioUser
        });

        $(this.el).prepend(view.render().el);
        this.views.push(view);

        if (this.views.length >= this.collection.limit) {
            this.views[0].close();
            this.views.splice(0, 1);
        }
    }
});

/**
 * User connected to radio cell
 */
Yasound.Views.RadioUser = Backbone.View.extend({
    tagName: 'li',
    className: 'radio-user',
    events: {
        'click a': 'selectUser'
    },
    initialize: function () {
        this.model.bind('change', this.render, this);
    },

    beforeRemove: function () {
        $('.user', this.el).tooltip('hide');
    },

    onClose: function () {
        this.model.unbind('change', this.render);
    },

    render: function () {
        var data = this.model.toJSON();
        $(this.el).html(ich.radioUserTemplate(data));
        $('.user', this.el).tooltip({title: data.name});

        return this;
    },

    selectUser: function (event) {
        event.preventDefault();
        Yasound.App.Router.navigate("profile/" + this.model.get('username') + '/', {
            trigger: true
        });
    }
});

Yasound.Views.RadioPage = Backbone.View.extend({
    radioUsers: new Yasound.Data.Models.RadioUsers({}),
    wallEvents: new Yasound.Data.Models.PaginatedWallEvents({}),
    intervalId: undefined,
    wallPosted: undefined,

    events: {
        "click .audience-btn": "displayListeners"
    },

    initialize: function () {
        _.bindAll(this, 'removeWallEvent');
        this.model.bind('change', this.render, this);
    },

    onClose: function () {
        this.model.unbind('change', this.render);
        Yasound.App.Router.pushManager.off('wall_event');
    },

    reset: function () {
        this.radioUsers.unbind('add', this.onRadioUsersChanged, this);
        this.radioUsers.unbind('remove', this.onRadioUsersChanged, this);
        this.radioUsers.unbind('reset', this.onRadioUsersChanged, this);

        if (this.wallPosted) {
            $.unsubscribe('/wall/posted', this.wallPosted);
        }
        if (this.intervalId) {
            clearInterval(this.intervalId);
        }
        if (this.radioInfosView) {
            this.radioInfosView.close();
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

    render: function () {
        this.reset();

        $(this.el).html(ich.radioPageTemplate());

        this.radioUsers.bind('add', this.onRadioUsersChanged, this);
        this.radioUsers.bind('remove', this.onRadioUsersChanged, this);
        this.radioUsers.bind('reset', this.onRadioUsersChanged, this);

        var that = this;
        var wallPosted = function () {
            that.wallEvents.page = 0;

            if (!Yasound.App.Router.pushManager.enablePush) {
                that.wallEvents.fetch();
            }
        };
        this.wallPosted = wallPosted;
        $.subscribe("/wall/posted", wallPosted);


        this.wallInputView = new Yasound.Views.WallInput({
            model: this.model,
            el: $('#webapp-wall-input', this.el)
        });
        this.wallInputView.radioUUID = this.model.get('uuid');
        this.wallInputView.render();

        this.radioView = new Yasound.Views.Radio({
            model: this.model,
            el: $('#webapp-radio', this.el)
        });

        this.radioInfosView = new Yasound.Views.RadioInfos({
            model: this.model,
            el: $('#radio-infos', this.el)
        });

        this.trackView = new Yasound.Views.TrackInRadio({
            model: this.model.currentSong,
            el: $('#webapp-track', this.el)
        });


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
            el: $('#pagination-wall', this.el)
        }).setTitle(gettext('Next messages'));

        this.wallEventsView.clear();


        if (Yasound.App.appName == 'deezer') {
            this.wallEvents.perPage = 10;
        }

        if (this.model.get('id')) {
            if (g_bootstrapped_data) {
                this.wallEvents.reset(g_bootstrapped_data.wall_events);
            } else {
                this.wallEvents.goTo(0);
            }
            this.radioUsers.fetch();
        }

        this.radioView.render();
        this.trackView.render();
        this.wallEventsView.render();
        this.paginationView.render();
        this.radioInfosView.render();

        if (Yasound.App.Router.pushManager.enablePush) {
            Yasound.App.Router.pushManager.on('wall_event', function (msg) {
                that.wallEvents.reset(msg);
            });
            Yasound.App.Router.pushManager.on('wall_event_deleted', function (msg) {
                that.removeWallEvent(msg);
            });
        }

        this.intervalId = setInterval(function () {
            if (!Yasound.App.Router.pushManager.enablePush) {
                that.wallEvents.fetchFirst();
            }
            that.radioUsers.fetch();
        }, 10000);

        return this;
    },

    removeWallEvent: function(message) {
        var viewToRemove;
        _.each(this.wallEventsView.views, function(view) {
            if (view.model.get('id') === message.id) {
                viewToRemove = view;
            }
        });

        if (!viewToRemove) {
            return;
        }
        this.wallEventsView.removeView(viewToRemove);
    },

    onRadioUsersChanged: function (collection) {
        $('.audience-nbr', this.el).html(collection.length);
        if (collection.length === 0) {
            $('.audience-btn', this.el).hide();
        } else {
            $('.audience-btn', this.el).show();
        }
    },

    displayListeners: function (e) {
        e.preventDefault();
        Yasound.App.Router.navigate("radio/" + this.model.get('uuid') + '/listeners/', {
            trigger: true
        });
    }
});

Yasound.Views.UserRadiosPage = Backbone.View.extend({
    collection: new Yasound.Data.Models.UserRadios({}),

    events: {
        'click #back-btn': 'onBack'
    },

    initialize: function() {
        _.bindAll(this, 'render', 'onGenreChanged', 'onBack');
        $.subscribe('/submenu/genre', this.onGenreChanged);
    },

    onClose: function() {
        $.unsubscribe('/submenu/genre', this.onGenreChanged);
    },

    reset: function() {
        if (this.resultsView) {
            this.resultsView.close();
            this.resultsViews = undefined;
        }
    },

    render: function(genre, username) {
        this.reset();
        $(this.el).html(ich.userRadiosPageTemplate());
        this.collection.perPage = Yasound.Utils.cellsPerPage();
        if (username) {
            this.collection.setUsername(username);
            this.username = username;
            this.user = new Yasound.Data.Models.User({username:username}),
            this.userView = new Yasound.Views.User({
                model: this.user,
                el: $('#user-profile', this.el)
            });
            this.user.fetch();
        }

        this.resultsView = new Yasound.Views.SearchResults({
            collection: this.collection,
            el: $('#results', this.el)
        });

        this.paginationView = new Yasound.Views.Pagination({
            collection: this.collection,
            el: $('#pagination', this.el)
        });

        this.onGenreChanged('', genre);
        return this;
    },

    onGenreChanged: function(e, genre) {
        if (genre === '') {
            this.collection.params.genre = undefined;
        } else {
            this.collection.params.genre = genre;
        }
        this.resultsView.clear();
        this.collection.goTo(0);
    },

    onBack: function(e) {
        e.preventDefault();
        Yasound.App.Router.navigate("profile/" + this.username + '/', {
            trigger: true
        });
    }
});

Yasound.Views.ListenersPage = Backbone.View.extend({
    collection: new Yasound.Data.Models.Listeners({}),

    events: {
        'click #back-btn': 'onBack'
    },

    initialize: function() {
        _.bindAll(this, 'render', 'onBack');
    },

    onClose: function() {
    },

    reset: function() {
        if (this.resultsView) {
            this.resultsView.close();
            this.resultsViews = undefined;
        }
    },

    render: function(uuid) {
        this.reset();
        this.uuid = uuid;
        $(this.el).html(ich.listenersPageTemplate());
        this.collection.uuid = uuid;
        this.collection.perPage = Yasound.Utils.cellsPerPage();

        this.resultsView = new Yasound.Views.Friends({
            collection: this.collection,
            el: $('#results', this.el)
        });

        this.collection.fetch();
        return this;
    },

    onBack: function(e) {
        e.preventDefault();
        Yasound.App.Router.navigate("radio/" + this.uuid + '/', {
            trigger: true
        });
    }
});

Yasound.Views.EditRadioPage = Backbone.View.extend({
    events: {
        "click #programming-btn": "onProgramming",
        "click #listen-btn": "onListen",
        "submit #edit-radio": "onSubmit"
    },

    initialize: function () {
        _.bindAll(this, 'render', 'templateLoaded');
    },

    onClose: function () {
    },

    reset: function () {
    },

    render: function (uuid) {
        this.reset();
        this.uuid = uuid;
        var params = {
            uuid: uuid
        };
        ich.loadRemoteTemplate('radio/editRadioPage.mustache', 'editRadioPageTemplate', this.templateLoaded, params);
        return this;
    },

    templateLoaded: function() {
        $(this.el).html(ich.editRadioPageTemplate());
        $("select").uniform();
        var that = this;
        var $progress = $('#progress .bar', this.el);
        $progress.parent().hide();
        $('#file-upload').fileupload({
            dataType: 'json',
            add: function (e, data) {
                $progress.parent().show();
                data.submit();
            },
            progressall: function (e, data) {
                var progress = parseInt( (data.loaded*100) / data.total, 10);
                $progress.css('width', progress + '%');
            },

            done: function (e, data) {
                var result = data.result[0];
                if (result.error) {
                    var error = result.error;
                    $('#modal-upload-error .modal-body p', that.el).html(error);
                    $('#modal-upload-error', that.el).modal('show');
                } else {
                    var url = result.url;
                    var now = moment();
                    url = url + '?' + now.unix();
                    $('#radio-picture-image', that.el).attr('src', url);
                }
                $progress.css('width', '0%');
                $progress.parent().hide();
            },
            fail: function (e, data) {
            }
        });
    },

    onSubmit: function (e) {
        e.preventDefault();
        var form = $('#edit-radio', this.el);
        var successMessage = gettext('Radio settings updated');
        var errorMessage = gettext('Error while saving settings');

        Yasound.Utils.submitForm({
            form: form,
            successMessage: successMessage,
            errorMessage: errorMessage
        });
    },

    onProgramming: function (e) {
        e.preventDefault();
        Yasound.App.Router.navigate("radio/" + this.uuid + '/programming/', {
            trigger: true
        });
    },

    onListen: function (e) {
        e.preventDefault();
        Yasound.App.Router.navigate("radio/" + this.uuid, {
            trigger: true
        });
    }
});
