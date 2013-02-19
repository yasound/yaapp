/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Views.Jingles');

Yasound.Data.Models.Jingle = Backbone.Model.extend({
    idAttribute: "_id",
    url: function () {
        return '/api/v1/jingle/' + this.get('_id') + '/';
    },

    setSongRange: function(range) {
        schedule = [{
            type: 'between_songs',
            range: range
        }];
        this.set({
            'schedule': schedule
        });
    },

    toJSON: function() {
        var data = Yasound.Data.Models.Jingle.__super__.toJSON.apply(this);
        schedule = data.schedule;
        if (schedule && schedule.length >= 1) {
            range = schedule[0].range;
            var tpl = gettext('every <%range%> songs');
            var context = {
                range: range
            };
            schedule_str = Mustache.to_html(tpl, context);
            data.schedule_str = schedule_str;
        }
        return data;
    }

});

Yasound.Data.Models.Jingles = Yasound.Data.Paginator.extend({
    model: Yasound.Data.Models.Jingle,
    url: function() {
        return '/api/v1/jingle/radio/' + this.uuid + '/';
    },

    setUUID: function(uuid) {
        this.uuid = uuid;
        return this;
    }
});