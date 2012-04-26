Namespace('Yasound.Views');

Yasound.Views.SearchMenu = Backbone.View.extend({
    el: '#tbar-search',
    events: {
        'keypress #search-input': 'search'
    },
    search: function(e) {
        if (e.keyCode != 13) return;
        
        var value = $('#search-input', this.el).val();
        if (!value) return;

        $('#search-input', this.el).val('');
        e.preventDefault();

        Yasound.App.Router.navigate("search/" + value, {trigger: true});
    }
});
