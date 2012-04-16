$(document).ready(function() {
    Namespace('Yasound.App');
    Yasound.App.Workspace = Backbone.Router.extend({
        routes : {
            "" : "index",
            "help" : "help", // #help
            "search/:query" : "search", // #search/kiwis
            "search/:query/p:page" : "search" // #search/kiwis/p7
        },

        index : function() {
            var currentRadio = new Yasound.Data.Models.Radio({
                id : 75
            });
            var wallEvents = new Yasound.Data.Models.WallEvents();
            wallEvents.radio = currentRadio;
            var list = new Yasound.Views.WallEvents({
                collection: wallEvents,
                el: $('#wall')
            });
            list.addAll();
            
            wallEvents.fetch();
        },

        help : function() {
            alert('help');
        },

        search : function(query, page) {
        }
    });

    var router = new Yasound.App.Workspace();
    Backbone.history.start({
        pushState : false,
        root : '/app/',
        silent : false
    });

});