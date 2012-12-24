/*
 * jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true,
 * evil: true, undef: true, white: true, newcap: true
 */
/* extern Ext, $ */
Namespace('Yasound.Data.Models');

Yasound.Data.Models.SelectedRadios = Yasound.Data.Paginator.extend({
    model: Yasound.Data.Models.Radio,
    url: '/api/v1/radio_recommendations/'
});

Yasound.Data.Models.Activity = Backbone.Model.extend({
    idAttribute: '_id',

    toJSON: function() {
        var data = Yasound.Data.Models.Activity.__super__.toJSON.apply(this);

        var timeZone = '+01:00';
        if (moment().isDST()) {
            timeZone = '+02:00';
        }
        // if start_date contains microsecond precision, we remove it
        var start_date = this.get('created').substr(0, 19);
        var date = moment(start_date + timeZone);
        data.formatted_date= date.format('LLL');
        return data;
    }
});

Yasound.Data.Models.FriendsActivity = Yasound.Data.Paginator.extend({
    model: Yasound.Data.Models.Activity,
    url: function() {
        return '/api/v1/friends_activity/';
    }
});

Yasound.Data.Models.RadiosActivity = Yasound.Data.Paginator.extend({
    model: Yasound.Data.Models.Activity,
    url: function() {
        return '/api/v1/radios_activity/';
    }
});