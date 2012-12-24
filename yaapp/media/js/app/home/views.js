/*
 * jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true,
 * evil: true, undef: true, white: true, newcap: true
 */
/* extern Ext, $ */
Namespace('Yasound.Views');


Yasound.Views.RadiosSlide = Backbone.View.extend({

    events: {
        'click a.asset-slide-right': 'onSlide',
        'click a.asset-slide-left': 'onSlide'
    },

    currentStep: 0,
    lastStep: 1,

    initialize: function() {
        _.bindAll(this, 'addOne', 'addAll', 'onSlide', 'resetSlide', 'getSlideOffset', 'onWindowResized');

        this.collection.bind('add', this.addOne, this);
        this.collection.bind('reset', this.addAll, this);
        this.collection.bind('beforeFetch', this.beforeFetch, this);
        this.views = [];

        $(window).bind('resize', this.onWindowResized);
    },
    onClose: function() {
        this.collection.unbind('beforeFetch', this.beforeFetch);
        this.collection.unbind('add', this.addOne);
        this.collection.unbind('reset', this.addAll);
    },

    beforeFetch: function() {
        if (this.loadingMask) {
            this.loadingMask.show();
        }
    },

    addAll: function() {
        if (!this.loadingMask) {
            var mask = this.$el.siblings('.loading-mask');
            this.loadingMask = mask;
        }

        this.loadingMask.remove();
        this.loadingMask = undefined;

        if (this.collection.length === 0) {
            $('.empty', this.el).show();
        } else {
            $('.empty', this.el).hide();
        }
        this.currentRadioIndex = 0;
        this.collection.each(this.addOne);
        this.resetSlide();
    },

    clear: function() {
        _.map(this.views, function(view) {
            view.close();
        });
        this.views = [];
        $('ul', this.el).remove();

        this.currentStep = 0;
        this.lastStep = 1;
        this.currentRadioIndex = 0;
        this.resetSlide();
        this.$('.block-slide').animate({ marginLeft: '-' + this.currentStep*this.getSlideOffset() + 'px' });
    },

    addOne: function(radio) {
        if (this.currentRadioIndex === 0 ) {
            this.cellsRange = $('<ul/>').appendTo(this.$('.block-slide'));
        } else if ( this.currentRadioIndex % 5 === 0) {
            this.cellsRange = $('<ul/>').appendTo(this.$('.block-slide'));
        }
        var view = new Yasound.Views.RadioCell({
            model: radio
        });
        this.cellsRange.append(view.render().el);
        this.views.push(view);
        this.currentRadioIndex++;
    },

    resetSlide: function() {
        var cells = this.$('li');
        if(cells.length > 0) {
            var cellWidth = $(cells.get(0)).outerWidth(true);
            this.$('.block-slide').width(cells.length*cellWidth + 'px');
        }
        this.lastStep = this.$('ul').length;
    },

    onSlide: function(e) {
        e.preventDefault();

        var previousStep = this.currentStep;
        var btn = $(e.currentTarget);

        if(btn.hasClass('asset-slide-right') && this.currentStep < this.lastStep-1) this.currentStep++;
        else if(btn.hasClass('asset-slide-left') && this.currentStep !== 0) this.currentStep--;

        if(this.currentStep === 0) this.$el.addClass('first');
        else this.$el.removeClass('first');

        if(this.currentStep === this.lastStep - 1) this.$el.addClass('last');
        else this.$el.removeClass('last');

        this.$('.block-slide').animate({ marginLeft: '-' + this.currentStep*this.getSlideOffset() + 'px' });

        if (previousStep < this.currentStep) {
            this.collection.requestNextPage();
        }
    },

    getSlideOffset: function() {
        var ranges = this.$('ul');
        if(ranges.length === 0) return 0;
        else return $(ranges.get(0)).outerWidth(true);
    },

    onWindowResized: function() {
        this.resetSlide();
        this.$('.block-slide').css('marginLeft', '-' + this.currentStep*this.getSlideOffset() + 'px');
    }

});


Yasound.Views.FriendActivity = Backbone.View.extend({
    tagName: 'li',
    events: {
        'click a': 'onLink'
    },

    initialize: function () {
        this.model.bind('change', this.render, this);
    },

    onClose: function () {
        this.model.unbind('change', this.render);
    },

    render: function () {
        var data = this.model.toJSON();
        if (Yasound.App.enableFX) {
            $(this.el).hide().html(ich.friendActivityTemplate(data)).fadeIn(200);
        } else {
            $(this.el).html(ich.friendActivityTemplate(data));
        }
        return this;
    },

    onLink: function (e) {
        e.preventDefault();

        var link = $(e.target);
        if (!link.is('a')) {
            link = $(e.target).parent('a');
        }

        var type = link.data('type');
        if (type === 'radio') {
            var uuid = link.data('id');
            Yasound.App.Router.navigate('radio/' + uuid + '/', {
                trigger: true
            });
        } else if (type === 'user') {
            var username = link.data('id');
            Yasound.App.Router.navigate('profile/' + username + '/', {
                trigger: true
            });
        }
    }

});

Yasound.Views.FriendsActivity = Backbone.View.extend({
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

    addOne: function (activity) {
        var found = _.find(this.views, function (view) {
            if (view.model.id == listener.id) {
                return true;
            }
        });

        if (found) {
            // do not insert duplicated content
            return;
        }

        var view = new Yasound.Views.FriendActivity({
            model: activity
        });

        $(this.el).prepend(view.render().el);
        this.views.push(view);

        if (this.views.length >= this.collection.limit) {
            this.views[0].close();
            this.views.splice(0, 1);
        }
    }
});

Yasound.Views.RadioActivity = Backbone.View.extend({
    tagName: 'li',
    events: {
        'click a': 'onLink'
    },

    initialize: function () {
        this.model.bind('change', this.render, this);
    },

    onClose: function () {
        this.model.unbind('change', this.render);
    },

    render: function () {
        var data = this.model.toJSON();
        if (Yasound.App.enableFX) {
            $(this.el).hide().html(ich.radioActivityTemplate(data)).fadeIn(200);
        } else {
            $(this.el).html(ich.radioActivityTemplate(data));
        }
        return this;
    },

    onLink: function (e) {
        e.preventDefault();
        var link = $(e.target);
        if (!link.is('a')) {
            link = $(e.target).parent('a');
        }

        var type = link.data('type');
        if (type === 'radio') {
            var uuid = link.data('id');
            Yasound.App.Router.navigate('radio/' + uuid + '/', {
                trigger: true
            });
        } else if (type === 'user') {
            var username = link.data('id');
            Yasound.App.Router.navigate('profile/' + username + '/', {
                trigger: true
            });
        }
    }
});

Yasound.Views.RadiosActivity = Backbone.View.extend({
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

    addOne: function (activity) {
        var found = _.find(this.views, function (view) {
            if (view.model.id == listener.id) {
                return true;
            }
        });

        if (found) {
            // do not insert duplicated content
            return;
        }

        var view = new Yasound.Views.RadioActivity({
            model: activity
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
 * Home page
 */
Yasound.Views.HomePage = Backbone.View.extend({

    events: {
        'click .app-alert .asset-close': 'onCloseAnnouncement'
    },

    initialize: function() {
        _.bindAll(this, 'render', 'onGenreChanged', 'updateGenreSlug');
        $.subscribe('/submenu/genre', this.onGenreChanged);

        this.selection = new Yasound.Data.Models.SelectedRadios({});
        this.favorites = new Yasound.Data.Models.Favorites({});
        this.popular = new Yasound.Data.Models.MostActiveRadios({});
        this.friendsActivity = new Yasound.Data.Models.FriendsActivity({});
        this.radiosActivity = new Yasound.Data.Models.RadiosActivity({});

        this.selection.perPage = 15;
        this.favorites.perPage = 15;
        this.popular.perPage = 15;
        this.friendsActivity.perPage = 5;
        this.radiosActivity.perPage = 5;
    },

    onClose: function() {
        $.unsubscribe('/submenu/genre', this.onGenreChanged);
    },

    reset: function() {
        if (this.selectionView) {
            this.selectionView.close();
            this.selectionView = undefined;
        }
        if (this.favoritesView) {
            this.favoritesView.close();
            this.favoritesView = undefined;
        }
        if (this.popularView) {
            this.popularView.close();
            this.popularView = undefined;
        }

        if (this.friendsActivityView) {
            this.friendsActivityView.close();
            this.friendsActivityView = undefined;
        }

        if (this.radiosActivityView) {
            this.radiosActivityView.close();
            this.radiosActivityView = undefined;
        }
    },

    render: function(genre) {
        this.reset();
        $(this.el).html(ich.homePageTemplate());

        var hideAnnouncementCookie = cookies.get('hideannouncement');
        if (hideAnnouncementCookie == Yasound.App.announcementId) {
            $('.app-alert').hide();
        } else{
            $('.app-alert').show();
        }

        this.selectionView = new Yasound.Views.RadiosSlide({
            collection: this.selection,
            el: $('#selection-slides', this.el)
        });

        if (Yasound.App.userAuthenticated) {
            this.favoritesView = new Yasound.Views.RadiosSlide({
                collection: this.favorites,
                el: $('#favorites-slides', this.el)
            });
            this.favorites.goTo(0);
            this.favorites.perPage = 5;

            this.friendsActivityView = new Yasound.Views.FriendsActivity({
                collection: this.friendsActivity,
                el: $('#friends-activity', this.el)

            });
            this.friendsActivity.fetch();

            this.radiosActivityView = new Yasound.Views.RadiosActivity({
                collection: this.radiosActivity,
                el: $('#radios-activity', this.el)
            });
            this.radiosActivity.fetch();
        }

        this.popularView = new Yasound.Views.RadiosSlide({
            collection: this.popular,
            el: $('#popular-slides', this.el)
        });

        this.selection.goTo(0);
        this.popular.goTo(0);

        this.selection.perPage = 5;
        this.popular.perPage = 5;

        this.updateGenreSlug(genre);
        return this;
    },

    updateGenreSlug: function (genre) {
        var found = (/^style_/).test(genre);
        if (found) {
            var prefix_length = 'style_'.length;
            var genre_slug = genre.substr(prefix_length, genre.length - prefix_length);
            Yasound.App.Router.navigate('selection/' + genre_slug + '/', {
                trigger: false
            });
        } else {
            Yasound.App.Router.navigate("", {
                trigger: false
            });
        }
    },

    onGenreChanged: function(e, genre) {
        this.updateGenreSlug(genre);
        if (genre === '') {
            this.selection.params.genre = undefined;
            this.favorites.params.genre = undefined;
            this.popular.params.genre = undefined;
        } else {
            this.selection.params.genre = genre;
            this.favorites.params.genre = genre;
            this.popular.params.genre = genre;
        }
        this.selectionView.clear();
        this.popularView.clear();

        this.selection.perPage = 15;
        this.popular.perPage = 15;

        this.selection.goTo(0);
        this.popular.goTo(0);

        if (Yasound.App.userAuthenticated) {
            this.favoritesView.clear();
            this.favorites.perPage = 15;
            this.favorites.goTo(0);
        }
    },

    onCloseAnnouncement: function (e) {
        e.preventDefault();
        cookies.set('hideannouncement', Yasound.App.announcementId);
    }
});
