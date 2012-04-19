Namespace('Yasound.Data.Models');

Yasound.Data.Models.Radio = Backbone.Model.extend({
    idAttribute: 'uuid',
    urlRoot : '/api/v1/public_radio/',
    
    connect: function() {
        var id = this.get('id');
        if (id > 0) {
            var url = '/api/v1/radio/' + id + '/connect/';
            $.post(url);
        }
    },
    
    disconnect: function() {
        var id = this.get('id');
        if (id > 0) {
            var url = '/api/v1/radio/' + id + '/disconnect/';
            $.post(url);
        }
    }
});

Yasound.Data.Models.CurrentSong = Backbone.Model.extend({
    url : function() {
        return '/api/v1/radio/' + this.get('radioId') + '/current_song/';
    }
});

Yasound.Data.Models.WallEvent = Backbone.Model.extend({
});

Yasound.Data.Models.WallEvents = Backbone.Collection.extend({
    model : Yasound.Data.Models.WallEvent,
    lastId : 0,
    limit : 25,
    url : function() {
        var lastId = this.findLastId();
        if (!lastId) {
            lastId = this.lastId;
        }
        return '/api/v1/radio/' + this.radio.get('id') + '/wall/?id__gt=' + lastId + '&limit=' + this.limit;
    },
    setRadio:function(radio) {
        this.reset();
        this.radio = radio;
        this.lastId = 0;
    },
    
    findLastId : function() {
        var lastObject = this.max(function(event) {
            return event.get('id');
        });
        if (lastObject) {
            this.lastId = lastObject.get('id');
            return lastObject.get('id');
        }
    },
    comparator : function(wallEvent) {
        return wallEvent.get("id");
    }
});
