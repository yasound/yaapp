/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.App');

Yasound.App.ErrorHandler = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this, 'render', 'onError', 'onSuccess');
    },

    onClose: function() {
    },

    reset: function() {
        if (this.resultsView) {
            this.resultsView.close();
            this.resultsViews = undefined;
        }
    },

    render: function() {
        this.reset();
        this.enableErrorHandling = true;
        $('body').ajaxError(this.onError);
        return this;
    },

    onError: function(e, jqxhr, settings, exception) {
        if (!this.enableErrorHandling) {
            return;
        }
        if (jqxhr.statusText === 'abort') {
            return;
        }

        if (jqxhr.status !== 0) {
            return;
        }

        $('body').ajaxSuccess(this.onSuccess);

        $('#modal-error').modal('show');
        $('#modal-error .btn-primary').one('click', function () {
            window.location = '/app/';
        });

        this.enableErrorHandling = false;
    },

    onSuccess: function() {
        this.enableErrorHandling = true;
        $('body').off('ajaxSuccess', this.onSuccess);
    }

});