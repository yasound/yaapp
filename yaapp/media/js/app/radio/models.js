/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Data.Models');


Yasound.Data.Models.WallEvent = Backbone.Model.extend({
    idAttribute: 'event_id',

    reportAbuse: function () {
        var url = '/api/v1/report_message/' + this.id + '/';
        $.ajax({
           url: url,
           type: 'POST'
        });
    },

    deleteMessage: function () {
        var url = '/api/v1/delete_message/' + this.id + '/';
        $.ajax({
           url: url,
           type: 'DELETE'
        });
    },

    toJSON: function() {
        var data = Yasound.Data.Models.WallEvent.__super__.toJSON.apply(this);

        var timeZone = '+01:00';
        if (moment().isDST()) {
            timeZone = '+02:00';
        }
        // if start_date contains microsecond precision, we remove it
        var start_date = this.get('updated').substr(0, 19);
        var date = moment(start_date + timeZone);
        data.formatted_date= date.format('LLL');

        var formatted_likers;
        var likers = data.likers_digest;
        if (likers) {
            var tpl = '';
            var context = {};
            if (likers.length === 1) {
                tpl = gettext('<%name%> liked this song!');
                context = {
                    name: likers[0].name
                };
            } else if (likers.length == 2) {
                tpl = gettext('<%name1%> and <%name2%> liked this song!');
                context = {
                    name1: likers[0].name,
                    name2: likers[1].name
                };
            } else if (likers.length == 3) {
                tpl = gettext('<%name1%>, <%name2%> and <%name3%> liked this song!');
                context = {
                    name1: likers[0].name,
                    name2: likers[1].name,
                    name3: likers[2].name
                };
            } else if (likers.length >= 3) {
                var other =  data.like_count - 3;
                if (other <= 0) {
                    tpl = gettext('<%name1%>, <%name2%> and <%name3%> liked this song!');
                } else if (other === 1) {
                    tpl = gettext('<%name1%>, <%name2%>, <%name3%> and another person liked this song!');
                } else {
                    tpl = gettext('<%name1%>, <%name2%> and <%name3%> and <%other%> people liked this song!');
                }
                context = {
                    name1: likers[0].name,
                    name2: likers[1].name,
                    name3: likers[2].name,
                    other: other
                };
            }
            formatted_likers = Mustache.to_html(tpl, context);
            data.formatted_likers = formatted_likers;
        }

        return data;
    }

});

Yasound.Data.Models.WallEvents = Backbone.Paginator.requestPager.extend({
    model: Yasound.Data.Models.WallEvent,
    url: '/api/v1/radio/0/wall/',
    perPageAttribute: 'limit',
    skipAttribute: 'offset',
    perPage: 15,
    page:0,

    parse: function(response) {
        var results = response.objects;
        this.totalCount = response.meta.total_count;
        this.totalPages = this.totalCount / this.perPage;
        return results;
    },
    setRadio: function(radio) {
        this.radio = radio;
        this.url = '/api/v1/radio/' + this.radio.get('uuid') + '/wall/';

        return this;
    },

    fetchFirst: function() {
        var savedPage = this.page;
        this.page = 0;
        var that = this;
        this.fetch({
            success: function() {
                that.page = savedPage;
            },
            error: function() {
                that.page = savedPage;
            }
        });
    }
});

Yasound.Data.Models.RadioUsers = Yasound.Data.Paginator.extend({
    model: Yasound.Data.Models.User,
    perPage: 10,
    url: function() {
        return '/api/v1/radio/' + this.radio.get('id') + '/current_user/';
    },

    setRadio: function(radio) {
        this.reset();
        this.radio = radio;
        return this;
    }
});

Yasound.Data.Models.RadioFans = Yasound.Data.Paginator.extend({
    model: Yasound.Data.Models.User,
    url: function() {
        return '/api/v1/radio/' + this.uuid + '/favorites/';
    }
});

Yasound.Data.Models.UserRadios = Yasound.Data.Paginator.extend({
    model: Yasound.Data.Models.Radio,
    setUsername: function(username) {
        this.url = '/api/v1/user/' + username + '/radios/';
        return this;
    }
});

Yasound.Data.Models.Listeners = Yasound.Data.Paginator.extend({
    model: Yasound.Data.Models.User,
    url: function() {
        return '/api/v1/radio/' + this.uuid + '/listeners/';
    }
});