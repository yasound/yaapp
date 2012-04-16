$(document).ready(function() {
    Namespace('Yasound.App');

    Yasound.App.Workspace = Backbone.Router.extend({
        routes : {
            "" : "index",
            "radio/:id" : "radio",
            "help" : "help", // #help
            "search/:query" : "search", // #search/kiwis
            "search/:query/p:page" : "search" // #search/kiwis/p7
        },

        currentRadio : new Yasound.Data.Models.Radio({
            id : 0
        }),

        setCurrentRadioId : function(id) {
            this.currentRadio.set('id', id);
            this.currentRadio.fetch();
        },

        index : function() {
            $('#wall').html('Welcome');
        },

        help : function() {
            $('#wall').html('Help');
        },

        search : function(query, page) {
        },

        radio : function(id) {
            var radioView = new Yasound.Views.Radio({
                model : this.currentRadio,
                el : $('#radio')
            });
            var currentSong = new Yasound.Data.Models.CurrentSong();
            currentSong.set('radioId', id);
            setInterval(function() {
                currentSong.fetch();
            }, 10000);

            this.setCurrentRadioId(id);
            var wallEvents = new Yasound.Data.Models.WallEvents();
            wallEvents.radio = this.currentRadio;
            var list = new Yasound.Views.WallEvents({
                collection : wallEvents,
                el : $('#wall')
            });
            wallEvents.fetch();
            
            var currentSongView = new Yasound.Views.CurrentSong({
                model : currentSong,
                el : $('#track')
            })
        }

    });

    var router = new Yasound.App.Workspace();
    Backbone.history.start({
        pushState : false,
        root : '/app/',
        silent : false
    });

});