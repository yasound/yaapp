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

        if (jqxhr.status === 0) {
            $('body').ajaxSuccess(this.onSuccess);

            $('#modal-error').modal('show');
            $('#modal-error .btn-primary').one('click', function () {
                window.location = Yasound.App.root;
            });

            this.enableErrorHandling = false;
        } else if (jqxhr.status === 401) {
            $('body').ajaxSuccess(this.onSuccess);

            $('#modal-error-disconnected').modal('show');
            $('#modal-error-disconnected .btn-primary').one('click', function () {
                Yasound.App.Router.navigate("login/", {
                    trigger: true
                });
                $('#modal-error-disconnected').modal('hide');
            });
            this.enableErrorHandling = true;
        }

    },

    onSuccess: function() {
        this.enableErrorHandling = true;
        $('body').off('ajaxSuccess', this.onSuccess);
    }

});