/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.App');

var Class = function (methods) {
    var klass = function () {
        this.initialize.apply(this, arguments);
    };

    for ( var property in methods) {
        klass.prototype[property] = methods[property];
    }

    if (!klass.prototype.initialize) {
        klass.prototype.initialize = function () {
        };
    }
    return klass;
};

Yasound.App.PushManager = Class({
    enablePush: false,
    radio: undefined,
    radioPollingIntervalID: undefined,
    socketRadio: undefined,
    socketUser: undefined,

    initialize: function (options) {
        _.extend(this, options);
        _.extend(this, Backbone.Events);

        if (this.enablePush) {
            _.bindAll(this, 'onRadioEvent', 'onUserEvent');

            this.socketRadio = io.connect(g_push_url + 'radio');
            this.socketRadio.on('radio_event', this.onRadioEvent);

            this.socketUser = io.connect(g_push_url + 'me');
            this.socketUser.on('user_event', this.onUserEvent);

            var cookieSession = cookies.get('sessionid');
            this.socketUser.emit('subscribe', {'sessionid': cookieSession});

        }
    },

    onRadioEvent: function (message) {
        var raw_data = message.data;
        var data = JSON.parse(raw_data);
        this.trigger(data.event_type, JSON.parse(data.data));
    },

    unMonitorRadio: function () {
        if (this.enablePush) {
            this.socketRadio.emit('unsubscribe', {
                'radio_id': this.radio.get('id')
            });
        }
    },

    monitorRadio: function (radio) {
        if (this.radio) {
            this.unMonitorRadio();
        }

        this.radio = radio;

        if (this.enablePush) {
            this.socketRadio.emit('subscribe', {
                'radio_id': this.radio.get('id')
            });
        }
    },

    onUserEvent: function (message) {
        var raw_data = message.data;
        var data = JSON.parse(raw_data);
        this.trigger(data.event_type, JSON.parse(data.data));
    }

});
