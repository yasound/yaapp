Namespace('Yasound.App');

var Class = function(methods) {
    var klass = function() {
        this.initialize.apply(this, arguments);
    };

    for ( var property in methods) {
        klass.prototype[property] = methods[property];
    }

    if (!klass.prototype.initialize)
        klass.prototype.initialize = function() {
        };

    return klass;
};

Yasound.App.PushManager = Class({
    enablePush: false,
    radio: undefined,
    radioPollingIntervalID: undefined,
    socket: undefined,

    initialize: function(options) {
        _.extend(this, options);
        _.extend(this, Backbone.Events);
        
        if (this.enablePush) {
            _.bindAll(this, 'onRadioEvent');

            this.socket = io.connect(g_push_url + 'radio');
            this.socket.on('radio_event', this.onRadioEvent);
        }
    },

    onRadioEvent: function(message) {
        raw_data = message.data;
        data = JSON.parse(raw_data);
        this.trigger(data.event_type, data.data);
    },

    unMonitorRadio: function() {
        if (this.enablePush) {
            this.socket.emit('unsubscribe', {
                'radio_id': this.radio.get('id')
            });
        }
    },

    monitorRadio: function(radio) {
        if (this.radio) {
            this.unMonitorRadio();
        }

        this.radio = radio;

        if (this.enablePush) {
            this.socket.emit('subscribe', {
                'radio_id': this.radio.get('id')
            });
        }
    }
})