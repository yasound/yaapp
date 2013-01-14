/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Data.Models');

Yasound.Data.Models.BlogPost = Backbone.Model.extend({
    idAttribute: 'slug',

    toJSON: function() {
        var data = Yasound.Data.Models.BlogPost.__super__.toJSON.apply(this);

        var timeZone = '+01:00';
        if (moment().isDST()) {
            timeZone = '+02:00';
        }
        // if start_date contains microsecond precision, we remove it
        var start_date = this.get('updated').substr(0, 19);
        var date = moment(start_date + timeZone);
        data.formatted_date= date.format('LL');
        return data;
    },

    url: function() {
        return '/api/v1/blog/' + this.get('slug') + '/?lang=' + g_language_code;
    },

    absoluteUrl: function () {
        var protocol = window.location.protocol;
        var host = window.location.host;
        var url =  protocol + '//' + host + Yasound.App.root + 'blog/' + this.get('slug');
        return url;
    }
});

Yasound.Data.Models.BlogPosts = Yasound.Data.Paginator.extend({
    model: Yasound.Data.Models.BlogPost,
    url: function() {
        return '/api/v1/blog/';
    }
});
