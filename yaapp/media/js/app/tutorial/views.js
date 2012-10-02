/*
 * jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true,
 * evil: true, undef: true, white: true, newcap: true
 */
/* extern Ext, $ */
Namespace('Yasound.Views');

/**
 * Generic static page
 */
Yasound.Views.TutorialWindow = Backbone.View.extend({
    initialize: function () {
        _.bindAll(this, 'render', 'templateLoaded', 'notifyServer');
    },
    reset: function() {

    },

    templateUrl: function (page) {
        return 'static/' + page + '.mustache';
    },

    templateName: function (page) {
        return 'static' + page + 'Template';
    },

    render: function () {
        this.reset();
        this.page = 'tutorial';
        ich.loadRemoteTemplate(this.templateUrl(this.page), this.templateName(this.page), this.templateLoaded);
        return this;
    },

    templateLoaded: function() {
        var that = this;
        $('#modal-window .modal-body').html(ich[this.templateName(this.page)]());
        $('#modal-window').modal({
            show: true,
            backdrop: true
        });

        var timer;
        timer = setTimeout(function() {
            that.notifyServer();
        }, 60*1000*3);

        $('#modal-window').one('hidden', function () {
            if (timer) {
                clearTimeout(timer);
                timer = undefined;
            }
            that.close();
        });
    },

    notifyServer: function () {
        var url = '/api/v1/user_watched_tutorial/';
        $.ajax({
           url: url,
           type: 'POST'
        });
    }
});

