"use strict";
/*
 * jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true,
 * evil: true, undef: true, white: true, newcap: true
 */
/* extern Ext, $ */
Namespace('Yasound.Views');

Yasound.Views.WallInput = Backbone.View.extend({
    tagName: 'div',
    events: {
        'click #submit': 'submit',
        'click #refresh': 'refreshWall'
    },

    submit: function (e) {
        var $button = $('.btn', this.el);
        $button.attr('disabled', 'disable');
        if (this.radioUUID) {
            var $input = $('input[type=text]', this.el);
            var message = $input.val();
            var url = '/api/v1/radio/' + this.radioUUID + '/post_message/';
            $.post(url, {
                message: message,
                success: function () {
                    $input.val('');
                    $button.removeAttr('disabled');
                    $.publish('/wall/posted');
                }
            });
        } else {
            alert('no radio!');
        }
        e.preventDefault();
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
        "click #webapp-radio-title h1": "selectUser"
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
    }
});

Yasound.Views.WallEvents = Backbone.View.extend({
    initialize: function () {
        _.bindAll(this, 'addOne', 'addAll');

        this.collection.bind('add', this.addOne);
        this.collection.bind('reset', this.addAll, this);
        this.views = [];
    },

    addAll: function () {
        this.collection.each(this.addOne);
    },

    clear: function () {
        _.map(this.views, function (view) {
            view.close();
        });
        this.views = [];
    },

    addOne: function (wallEvent) {
        var view = new Yasound.Views.WallEvent({
            model: wallEvent
        });

        $(this.el).prepend(view.render().el);
        this.views.push(view);

        if (this.views.length >= this.collection.limit) {
            this.views[0].close();
            this.views.splice(0, 1);
        }

        view.bind('all', this.rethrow, this);
    },

    rethrow: function () {
        this.trigger.apply(this, arguments);
    }

});

Yasound.Views.PaginatedWallEvents = Backbone.View.extend({
    initialize: function () {
        _.bindAll(this, 'addOne', 'addAll');

        this.collection.bind('add', this.addOne, this);
        this.collection.bind('reset', this.addAll, this);
        this.views = [];
    },

    onClose: function () {
        this.collection.unbind('add', this.addOne);
        this.collection.unbind('reset', this.addAll);
    },

    addAll: function () {
        this.collection.each(this.addOne);
    },

    clear: function () {
        _.map(this.views, function (view) {
            view.close();
        });
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

        var view = new Yasound.Views.WallEvent({
            model: wallEvent
        });
        
        var insertOnTop = false;
        if (this.views.length > 0) {
            var lastId = parseInt(this.views[0].model.get('id'));
            var currentId = parseInt(wallEvent.id);
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

    initialize: function () {
        _.bindAll(this, 'scroll');

        $(window).on('scroll', this.scroll);
        this.collection.on('reset', this.render, this);
        this.collection.on('change', this.render, this);
    },

    onClose: function () {
        $(window).off('scroll', this.scroll);
        this.collection.unbind('change', this.render);
        this.collection.unbind('reset', this.render);
    },

    render: function () {
        var info = this.collection.info();
        var page = info.page;
        var totalPages = info.totalPages;
        if (page < totalPages) {
            this.$el.html(ich.paginationTemplate());
        } else {
            this.$el.html('');
        }
    },

    updateSortBy: function (e) {
        e.preventDefault();
        var currentSort = $('#sortByField').val();
        this.collection.updateOrder(currentSort);
    },

    nextResultPage: function (e) {
        e.preventDefault();
        this.collection.requestNextPage();
    },

    previousResultPage: function (e) {
        e.preventDefault();
        this.collection.requestPreviousPage();
    },

    gotoFirst: function (e) {
        e.preventDefault();
        this.collection.goTo(this.collection.information.firstPage);
    },

    gotoLast: function (e) {
        e.preventDefault();
        this.collection.goTo(this.collection.information.lastPage);
    },

    gotoPage: function (e) {
        e.preventDefault();
        var page = $(e.target).text();
        this.collection.goTo(page);
    },

    changeCount: function (e) {
        e.preventDefault();
        var per = $(e.target).text();
        this.collection.howManyPer(per);
    },
    scroll: function (event) {
        var height = $(document).height();
        var scrollHeight = $(window).scrollTop() + $(window).height();

        if (scrollHeight >= height) {
            this.collection.requestNextPage();
        }
    }
});

Yasound.Views.WallEvent = Backbone.View.extend({
    tagName: 'li',
    className: 'wall-event',
    events: {
        'click h2 a': 'selectUser'
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
        data.formatted_start_date = date.format('LLLL');

        if (this.model.get('type') == 'M') {
            $(this.el).hide().html(ich.wallEventTemplateMessage(data)).fadeIn(200);
        } else if (this.model.get('type') == 'S') {
            $(this.el).hide().html(ich.wallEventTemplateSong(data)).fadeIn(200);
        } else if (this.model.get('type') == 'L') {
            $(this.el).hide().html(ich.wallEventTemplateLike(data)).fadeIn(200);
        }
        return this;
    },

    selectUser: function (event) {
        event.preventDefault();
        Yasound.App.Router.navigate("profile/" + this.model.get('user_username') + '/', {
            trigger: true
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
        'click h5 a': 'selectUser'
    },
    initialize: function () {
        this.model.bind('change', this.render, this);
    },

    onClose: function () {
        this.model.unbind('change', this.render);
    },

    render: function () {
        var data = this.model.toJSON();
        $(this.el).html(ich.radioUserTemplate(data));
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
    name: 'radiopage',
    radioUsers: new Yasound.Data.Models.RadioUsers({}),
    wallEvents: new Yasound.Data.Models.PaginatedWallEvents({}),
    intervalId: undefined,
    wallPosted: undefined,
    
    initialize: function () {
        this.model.bind('change', this.render, this);
    },

    onClose: function () {
        this.model.unbind('change', this.render);
        Yasound.App.Router.pushManager.off('wall_event');
    },

    reset: function () {
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

    render: function () {
        this.reset();

        var that = this;
        var wallPosted = function () {
            that.wallEvents.page = 0;

            if (!Yasound.App.Router.pushManager.enablePush) {
                that.wallEvents.fetch();
            }
        };
        this.wallPosted = wallPosted;
        $.subscribe("/wall/posted", wallPosted);

        $(this.el).html(ich.radioPageTemplate());

        if (Yasound.App.userAuthenticated) {
            this.wallInputView = new Yasound.Views.WallInput({
                model: this.model,
                el: $('#webapp-wall-input', this.el)
            });
            this.wallInputView.radioUUID = this.model.get('uuid');
            this.wallInputView.render();
        }
        this.radioView = new Yasound.Views.Radio({
            model: this.model,
            el: $('#webapp-radio', this.el)
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
            el: $('#pagination', this.el)
        });

        if (this.model.get('id')) {
            this.wallEvents.goTo(0);
            this.radioUsers.fetch();
        }

        this.radioView.render();
        this.wallEventsView.render();
        this.paginationView.render();

        if (Yasound.App.Router.pushManager.enablePush) {
            Yasound.App.Router.pushManager.on('wall_event', function (msg) {
                that.wallEvents.reset(msg);
            });
        }

        this.intervalId = setInterval(function () {
            if (!Yasound.App.Router.pushManager.enablePush) {
                that.wallEvents.fetchFirst();
            }
            that.radioUsers.fetch();
        }, 10000);

        return this;
    }
});
