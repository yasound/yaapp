/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Views.Jingles');

Yasound.Views.Jingles.Cell = Backbone.View.extend({
    tagName: 'tr',
    events: {
        'click .name': 'onEditName',
        'click .delete': 'onDelete'
    },

    initialize: function () {
        _.bindAll(this,
            'render',
            'start',
            'stop',
            'onStart',
            'onStop',
            'onRemove',
            'onProgress',
            'onFinished',
            'onFailed',
            'edit',
            'cancelEdit',
            'deleteJingle');

        this.model.bind('change', this.render, this);
        this.job = undefined;
        this.mode = 'view';
    },

    onClose: function () {
        this.stop();
        this.model.unbind('change', this.render);
        $.unsubscribe('/jingle/cancel_edit', this.cancelEdit);
    },

    render: function () {
        var data = this.model.toJSON();
        $(this.el).html(ich.jingleCellTemplate(data));

        $.subscribe('/jingle/cancel_edit', this.cancelEdit);

        return this;
    },

    upload: function(data, uuid) {
        this.data = data;
        this.data.formData = {
            'response_format': 'json',
            data: JSON.stringify({
                'radio_uuid': uuid,
                'name': this.model.get('name')
            })
        };

        this.data.onProgress = this.onProgress;
        this.data.onFinished = this.onFinished;
        this.data.onFailed = this.onFailed;

        this.start();
    },

    start: function() {
        this.job = this.data.submit();
        $.publish('/jingle/upload_started');
        $('#start', this.el).hide();
        $('#stop', this.el).show();
    },

    stop: function () {
        if (this.job) {
            this.job.abort();
            this.job = undefined;

            $.publish('/jingle/upload_stopped');

            $('#start', this.el).show();
            $('#stop', this.el).hide();
        }
    },

    onStart: function(e) {
        e.preventDefault();
        this.start();
    },

    onStop: function (e) {
        e.preventDefault();
        this.stop();
    },

    onRemove: function (e) {
        this.stop();
        this.trigger('remove', this);
        this.remove();
    },

    onFinished: function(e, data) {
        res =  data.result[0];
        $.publish('/jingle/upload_finished');
        $('.progress', this.el).remove();
        // this.trigger('remove', this);
        // this.remove();
    },

    onFailed: function(e, data) {
        $.publish('/jingle/upload_failed');
    },

    onProgress: function(e, data) {
        var percentage = (data.loaded*100) / data.total;
        var progress = parseInt(percentage, 10);
        $progress = $('.progress .bar', this.el);
        $progress.css('width', progress + '%');
    },

    onEditName: function (e) {
        if (this.mode === 'view') {
            e.preventDefault();
            $.publish('/jingle/cancel_edit', this);
            $('.name', this.el).html("<input type='text' value='" + this.model.get('name') + "'/>");
            $('.name input', this.el).focus();
            $('.name input').on('keydown', this.edit);
        }
    },

    edit: function (e) {
        if (e.keyCode == 13) {
            var val = $(e.target).val();
            if (val.length > 0) {
                this.model.set('name', val);
                this.model.save();
            }
            $('.name', this.el).html(this.model.get('name'));
            this.mode = 'view';
            return;
        } else if (e.keyCode == 27) {
            this.cancelEdit();
        }
        this.mode = 'edit';
    },

    cancelEdit: function (e, sender) {
        if (sender == this) {
            return;
        }
        $('.name input').off('keydown', this.edit);
        $('.name', this.el).html(this.model.get('name'));
        this.mode = 'view';
    },

    onDelete: function (e) {
        e.preventDefault();
        var that = this;
        Yasound.Utils.dialog({
            title: gettext('Warning'),
            content: gettext('Your jingle will be lost for ever, continue?'),
            closeButton: gettext('Yes, delete it'),
            cancelButton: gettext('Cancel'),
            onClose: function() {
                that.deleteJingle();
            }
        });
    },

    deleteJingle: function (e) {
        this.model.destroy();
        this.trigger('remove', this);
        this.remove();
    }
});


Yasound.Views.Jingles.List = Backbone.View.extend({
    initialize: function () {
        _.bindAll(this, 'render', 'addOne', 'addAll', 'onDestroy', 'onRemoveView');

        this.collection.bind('add', this.addOne, this);
        this.collection.bind('reset', this.addAll, this);
        this.collection.bind('destroy', this.onDestroy, this);
        this.views = [];
    },

    render: function() {
        return this;
    },

    onClose: function () {
        this.collection.unbind('add', this.addOne);
        this.collection.unbind('reset', this.addAll);
        this.collection.unbind('destroy', this.onDestroy);
    },

    addAll: function () {
        $('.loading-row', this.el).remove();
        this.collection.each(this.addOne);
    },

    clear: function () {
        _.map(this.views, function (view) {
            view.close();
        });
        this.views = [];
    },

    addOne: function (jingle) {
        var view = new Yasound.Views.Jingles.Cell({
            model: jingle
        });
        view.on('remove', this.onRemoveView);

        $(this.el).append(view.render().el);
        this.views.push(view);
        return view;
    },

    onDestroy: function(model) {
        this.clear();
        this.collection.fetch();
    },

    onRemoveView: function (view) {
        this.views = _.without(this.views, view);
        view.off('remove', this.onRemoveView);
    }

});


Yasound.Views.JinglesPage =  Backbone.View.extend({
    events: {
    },
    initialize: function() {
        _.bindAll(this, 'render');
    },

    onClose: function () {
        if (this.jingles) {
            delete this.jingles;
        }
        if (this.jinglesViews) {
            this.jingleViews.close();
            delete this.jingleViews;
        }
    },

    render: function(uuid) {
        $(this.el).html(ich.jinglesTemplate());

        this.jingles = new Yasound.Data.Models.Jingles({}).setUUID(uuid);
        this.jinglesView = new Yasound.Views.Jingles.List({
            el: $('#jingles', this.el),
            collection: this.jingles
        });

        this.jingles.fetch();

        var that = this;
        $('#file-upload-jingle', this.el).fileupload({
            dataType: 'json',
            add: function (e, data) {
                var warningTitle = gettext('Warning');
                var warningContent = gettext('You must own the copyright or have the necessary rights for any content you upload on Yasound');
                Yasound.Utils.dialog({
                    title: warningTitle,
                    content: warningContent,
                    closeButton: gettext('I agree'),
                    cancelButton: gettext('Cancel'),
                    onClose: function () {
                        var jingle = new Yasound.Data.Models.Jingle({
                            name: gettext('new jingle')
                        });
                        view = that.jinglesView.addOne(jingle);
                        view.upload(data, uuid);
                    }
                });

            },
            progressall: function (e, data) {
            },
            progress: function (e, data) {
                if (data.onProgress) {
                    data.onProgress(e, data);
                }
            },
            done: function (e, data) {
                if (data.onFinished) {
                    data.onFinished(e, data);
                }
            },
            fail: function (e, data) {
                if (data.onFailed) {
                    data.onFailed(e, data);
                }
            }
        });


        return this;
    }
});