/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Views');

Yasound.Views.BlogPost = Backbone.View.extend({
    tagName: 'div',
    className: 'blog-post-container',
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
            $(this.el).hide().html(ich.blogPostTemplate(data)).fadeIn(200);
        } else {
            $(this.el).html(ich.blogPostTemplate(data));
        }
        return this;
    },

    onSelected: function (e) {
        e.preventDefault();
        Yasound.App.Router.navigate('blog/' + this.model.get('slug') + '/', {
            trigger: true
        });
    }
});

Yasound.Views.BlogPostTeaser = Backbone.View.extend({
    tagName: 'div',
    className: 'blog-post-container',
    events: {
        'click .blog-post-title': 'onSelected'
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
            $(this.el).hide().html(ich.blogPostTeaserTemplate(data)).fadeIn(200);
        } else {
            $(this.el).html(ich.blogPostTemplate(data));
        }
        return this;
    },

    onSelected: function (e) {
        e.preventDefault();
        Yasound.App.Router.navigate('blog/' + this.model.get('slug') + '/', {
            trigger: true
        });
    }
});

Yasound.Views.BlogPosts = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this, 'addOne', 'addAll');

        this.collection.bind('add', this.addOne, this);
        this.collection.bind('reset', this.addAll, this);
        this.collection.bind('beforeFetch', this.beforeFetch, this);
        this.views = [];
    },

    onClose: function() {
        this.clear();
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

        this.loadingMask.hide();

        if (this.collection.length === 0) {
            $('.empty', this.el).show();
        } else {
            $('.empty', this.el).hide();
        }
        this.collection.each(this.addOne);
    },

    clear: function() {
        _.map(this.views, function(view) {
            view.close();
        });
        this.views = [];
    },

    addOne: function(post) {
        var view = new Yasound.Views.BlogPostTeaser({
            model: post
        });
        $(this.el).append(view.render().el);
        this.views.push(view);
    }
});

Yasound.Views.BlogsPage = Backbone.View.extend({
    collection: new Yasound.Data.Models.BlogPosts({}),
    events: {
    },

    initialize: function() {
        _.bindAll(this, 'render');
    },

    onClose: function() {
        if (this.blogPostsView) {
            this.blogPostsView.close();
        }
    },

    reset: function() {
    },

    render: function() {
        this.reset();
        $(this.el).html(ich.blogPostsPageTemplate());

        this.blogPostsView = new Yasound.Views.BlogPosts({
            collection: this.collection,
            el: $('#blog-posts', this.el)
        });

        this.collection.fetch();

        return this;
    }
});

Yasound.Views.BlogPage = Backbone.View.extend({
    events: {
    },

    initialize: function() {
        _.bindAll(this, 'render');
    },

    onClose: function() {
        if (this.blogPostView) {
            this.blogPostView.close();
        }
        delete this.model;
    },

    reset: function() {
        if (this.model) {
            delete this.model;
        }
    },

    render: function(slug) {
        this.reset();

        this.model = new Yasound.Data.Models.BlogPost({
            slug: slug
        }),

        $(this.el).html(ich.blogPostPageTemplate());

        this.blogPostView = new Yasound.Views.BlogPost({
            model: this.model,
            el: $('.blog-post-container', this.el)
        });

        var that = this;
        this.model.fetch({
            success: function () {
                $('.blog-title').html(that.model.get('name'));
            }
         });

        return this;
    }
});

