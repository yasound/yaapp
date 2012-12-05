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

                var href = link.attr('href');
                if (href && href !== '' && href !=='#') {
                    return;
                } else {
                    e.preventDefault();
                }
            }
        });
        return this;
    }
});


Yasound.Views.GiftDigest = Backbone.View.extend({
    tagName: 'li',
    className: 'list-block',
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
            $(this.el).hide().html(ich.giftDigestTemplate(data)).fadeIn(200);
        } else {
            $(this.el).html(ich.giftDigestTemplate(data));
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

                var href = link.attr('href');
                if (href && href !== '' && href !=='#') {
                    return;
                } else {
                    e.preventDefault();
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


Yasound.Views.GiftsDigest = Backbone.View.extend({
    collection: new Yasound.Data.Models.GiftsDigest({}),
    events: {
    },

    initialize: function() {
        _.bindAll(this, 'render', 'addOne', 'addAll', 'clear', 'onServiceFetched', 'onPromocode', 'onPromocodeSubmit', 'sendPromocode', 'onHD', 'onDisplayAll');

        this.collection.bind('add', this.addOne, this);
        this.collection.bind('reset', this.addAll, this);
        this.views = [];
    },

    onClose: function() {
        this.collection.unbind('add', this.addOne);
        this.collection.unbind('reset', this.addAll);
    },

    reset: function() {
        if (this.query) {
            this.query.abort();
            this.query = undefined;
        }
    },

    render: function() {
        this.reset();
        this.expire = undefined;
        this.hd = undefined;

        if (Yasound.App.userAuthenticated) {
            var that = this;
            this.service = new Yasound.Data.Models.ServiceHD();
            this.service.fetch({
                success: that.onServiceFetched
            });
        } else {
            this.query = this.collection.fetch();
        }

        return this;
    },

    onServiceFetched: function (service) {
        if (service && service.get('expiration_date')) {
            this.expire = moment(service.get('expiration_date')).format('L');
            this.hd = service.get('active');
        }
        this.query = this.collection.fetch();
    },

    addAll: function () {
        $('.loading-mask', this.el).hide();
        this.clear();
        $(this.el).append(ich.giftDigestHDTemplate({'expire': this.expire, 'hd': this.hd}));
        $(this.el).append(ich.giftDigestPromocodeTemplate({}));

        $('#toggle-hd', this.el).on('change', this.onHD);
        $('.dropdown-promo .input-text', this.el).on('keypress', this.onPromocode);
        $('.dropdown-promo button', this.el).on('click', this.onPromocodeSubmit);

        this.collection.each(this.addOne);

        var totalCount = this.collection.totalCount;
        var remaining = totalCount - this.collection.length;
        if (remaining < 0) {
            remaining = 0;
        }

        $(this.el).append(ich.giftDigestLastTemplate({'remaining': remaining}));
        $('.list-foot a', this.el).on('click', this.onDisplayAll);
    },

    clear: function () {
        $('.loading-mask', this.el).show();
        _.map(this.views, function (view) {
            view.close();
        });
        this.views = [];
        $('.dropdown-promo .input-text', this.el).off('keypress', this.onPromocode);
        $('.dropdown-promo button', this.el).off('click', this.onPromocodeSubmit);
        $('#toggle-hd', this.el).off('change', this.onHD);
        $('.list-foot a', this.el).off('click', this.onDisplayAll);

        $('li', this.el).remove();

    },

    addOne: function (gift) {
        var view = new Yasound.Views.GiftDigest({
            model: gift
        });
        $(this.el).append(view.render().el);
        this.views.push(view);
    },

    onPromocode: function (e) {
        if (e.keyCode != 13) {
            return;
        }
        e.preventDefault();
        var value = $(e.target).val();
        if (!value) {
            return;
        }
        this.sendPromocode(value);

    },

    onPromocodeSubmit: function (e) {
        e.preventDefault();
        var value = $('.dropdown-promo .input-text', this.el).val();
        if (!value) {
            return;
        }
        this.sendPromocode(value);
    },

    sendPromocode: function(value) {
        var url = '/api/v1/premium/activate_promocode/';
        $.ajax({
            url: url,
            data: {
                code: value
            },
            dataType: 'json',
            type: 'POST',
            success: function(data) {
                $('#gifts-menu').parent().removeClass('open');
                if (!data.success) {
                    Yasound.Utils.dialog(gettext('Invalid code'), gettext('The provided code is invalid.'));
                } else {
                    Yasound.Utils.dialog(gettext('Code validated'), gettext('Your code is now validated, your gift will be available soon.'));
                }
            },
            failure: function() {

            }
        });
    },

    onHD: function (e, checked) {
        if ((typeof checked === "undefined")) {
            checked = $(e.target).attr('checked');
        }
        if (checked) {
            $('.btn-hd i').removeClass('asset-hd-off').addClass('asset-hd-on');
        } else {
            $('.btn-hd i').removeClass('asset-hd-on').addClass('asset-hd-off');
        }
        Yasound.App.player.setHD(checked);
    },

    onDisplayAll: function (e) {
        e.preventDefault();
        Yasound.App.Router.navigate('gifts/', {
            trigger: true
        });
    }
});