/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Views');

Yasound.Views.Gift = Backbone.View.extend({
    tagName: 'li',
    className: 'gift',
    events: {
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
            $(this.el).hide().html(ich.giftTemplate(data)).fadeIn(200);
        } else {
            $(this.el).html(ich.giftTemplate(data));
        }

        var that = this;
        var link = $('a', this.el);
        link.on('click', function(e) {
            var url = link.data('ajax-url');
            if (url) {
                e.preventDefault();
                Yasound.App.Router.navigate(url, {
                    trigger: true
                });
            } else {
                var completed_url = link.data('completed-url');
                if (completed_url) {
                    e.preventDefault();

                    $('img', that.el).toggle();
                    $.ajax({
                        url: completed_url,
                        type: 'POST',
                        dataType: 'json',
                        contentType: 'application/json',
                        success: function(data) {
                            if (!(data.success)) {
                                Yasound.Utils.dialog(gettext('Error'), data.message);
                            } else {
                                Yasound.Utils.dialog(gettext('Thank you'), data.message);
                            }
                            $('img', that.el).toggle();
                        },
                        failure: function() {
                            Yasound.Utils.dialog(gettext('Error'), gettext('Error while communicating with Yasound, please retry late'));
                            $('img', that.el).toggle();
                        }
                    });
                }
            }
        });
        return this;
    }
});

Yasound.Views.Gifts = Backbone.View.extend({
    initialize: function () {
        _.bindAll(this, 'addOne', 'addAll', 'clear');

        this.collection.bind('add', this.addOne, this);
        this.collection.bind('reset', this.addAll, this);
        this.mode = 'unread';
        this.views = [];
    },

    onClose: function () {
        this.collection.unbind('add', this.addOne);
        this.collection.unbind('reset', this.addAll);
    },

    addAll: function () {
        $('.loading-mask', this.el).hide();
        this.collection.each(this.addOne);
        $('li', this.el).filter(':odd').removeClass('gift-even').addClass('gift-odd');
        $('li', this.el).filter(':even').removeClass('gift-even').addClass('gift-even');
    },

    clear: function () {
        $('.loading-mask', this.el).show();
        _.map(this.views, function (view) {
            view.close();
        });
        this.views = [];
    },

    addOne: function (gift) {
        var view = new Yasound.Views.Gift({
            model: gift
        });
        $(this.el).append(view.render().el);
        this.views.push(view);
    }
});

Yasound.Views.GiftsPage = Backbone.View.extend({
    events: {
    },

    initialize: function() {
        _.bindAll(this, 'render', 'templateLoaded');
    },

    onClose: function() {},

    reset: function() {},

    render: function() {
        this.reset();
        ich.loadRemoteTemplate('gifts/gift.mustache', 'giftTemplate');
        ich.loadRemoteTemplate('gifts/giftsPage.mustache', 'giftsPageTemplate', this.templateLoaded);
        return this;
    },

    templateLoaded: function() {
        $(this.el).html(ich.giftsPageTemplate());

        this.gifts = new Yasound.Data.Models.Gifts({});
        this.giftsView = new Yasound.Views.Gifts({
            collection: this.gifts,
            el: $('#gifts', this.el)
        });

        this.gifts.fetch();
    }
});

Yasound.Views.GiftsPopup = Backbone.View.extend({
    gifts: new Yasound.Data.Models.Gifts({}),

    events: {
    },

    initialize: function() {
        _.bindAll(this, 'render');
    },

    onClose: function() {
        this.giftsView.close();
    },

    reset: function() {
        if (this.query) {
            this.query.abort();
            this.query = undefined;
        }
    },

    render: function() {
        this.reset();
        if (!this.giftsView) {
            this.giftsView = new Yasound.Views.Gifts({
                collection: this.gifts,
                el: $('#gifts', this.el)
            });
        }
        this.giftsView.clear();
        this.query = this.gifts.fetch();
        return this;
    }
});
