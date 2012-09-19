/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Views');

Yasound.Views.NewRadioPage = Backbone.View.extend({
    events: {
        "change input[type='file']": "onFileChange",
        "submit #new-radio-form": "submit",
        "click .radio-creation-image img": "selectImage"
    },

    initialize: function() {
        _.bindAll(this, 'render', 'templateLoaded', 'submit', 'onFileChange');
    },

    onClose: function() {},

    reset: function() {},

    render: function() {
        this.reset();
        ich.loadRemoteTemplate('newRadio/newRadioPage.mustache', 'newRadioPageTemplate', this.templateLoaded);
        return this;
    },

    templateLoaded: function() {
        $(this.el).html(ich.newRadioPageTemplate());
        var that = this;

        $('#upload-photo').fileupload({
            dataType: 'json',
            add: function (e, data) {
                that.pictureData = data;
            }
        });

    },

    submit: function(e) {
        e.preventDefault();
        var that = this;
        var form = $('#new-radio-form', this.el);
        $('.error-msg', form).remove();
        $('input').removeClass('error');

        var url = window.location.href;
        $.post(url, form.serializeArray(), function(data) {
            var success = data.success;
            if (!data.success) {
                if (data.message) {
                    colibri(data.message, 'colibri-error');
                } else {
                    colibri(gettext('Error while creating radio'));
                }
                var errors = data.errors;
                if (errors) {
                    _.each(errors, function(value, key) {
                        var $input = $('input[name=' + key + ']', form);
                        $input.addClass('error');
                        $input.after('<div class="error-msg">' + value + '</div>');
                    });
                }
            } else {
                $('#upload-photo').fileupload('option', 'url', data.upload_photo_url);
                if (that.pictureData) {
                    that.pictureData.submit();
                }
                Yasound.App.Router.navigate(data.url, {
                    trigger: true
                });
            }
        }).error(function() {
            colibri(gettext('Error while login in'), 'colibri-error');
        });
    },

    selectImage: function (e) {
        e.preventDefault();
        $('#upload-photo').trigger('click');
    },

    onFileChange: function (e) {
        var that = this;
        $('.radio-creation-image img', that.el).remove();
        window.loadImage(e.target.files[0], function (img) {
            $('.radio-creation-image', that.el).append(img);
        }, {maxWidth: 216});
    }
});
