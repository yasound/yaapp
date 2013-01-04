Namespace('Yasound.Utils');

Yasound.Utils.momentDate = function(rawDate) {
    var timeZone = '+01:00';
    if (moment().isDST()) {
        timeZone = '+02:00';
    }
    // if start_date contains microsecond precision, we remove it
    var date = rawDate.substr(0, 19);
    return moment(date + timeZone);
};

Yasound.Utils.formatDate = function(rawDate) {
    return Yasound.Utils.momentDate(rawDate).format('LLLL');
};

Yasound.Utils.humanizeDate = function(rawDate) {
    return Yasound.Utils.momentDate(rawDate).fromNow();
};

Yasound.Utils.containerHeight = function () {
    var containerHeight = 100;
    if (Yasound.App.appName === 'deezer') {
        var container = $('#webapp-container-parent');
        containerHeight = container.height();
    } else {
        var viewportHeight = $(window).height();
        var headerHeight = $('#header').height();
        containerHeight = viewportHeight - headerHeight;
    }
    return containerHeight;
};

Yasound.Utils.cellsPerPage = function() {
    var containerHeight = Yasound.Utils.containerHeight();
    var cellHeight = 144;
    var rows =  Math.ceil(containerHeight / cellHeight);
    return rows*6 * 2;
};

Yasound.Utils.userCellsPerPage = function() {
    var containerHeight = Yasound.Utils.containerHeight();
    var cellHeight = 158;
    var rows =  Math.ceil(containerHeight / cellHeight);
    return rows*5 * 2;
};

Yasound.Utils.saveStickyView = function(key, view) {
    Yasound.App.stickyViews[key] = view;
};

Yasound.Utils.getStickyView = function (key) {
    return Yasound.App.stickyViews[key];
};

Yasound.Utils.submitForm = function (options) {
    options = options || {};
    if (!options.form) {
        return;
    }
    var form = options.form;
    var url = options.url;
    if (!url) {
        url = form.attr('action');
    }
    options.successMessage = options.successMessage || gettext('Data saved with success');
    options.errorMessage = options.errorMessage || gettext('Error while saving data');

    $('.error-msg', form).remove();
    $('input', form).removeClass('error');

    var button = $("button[type='submit']", form);
    button.attr('disabled', 'disabled');
    var savedText = button.html();
    $.post(url, form.serializeArray(), function(data) {
        var success = data.success;
        if (!data.success) {
            colibri(options.errorMessage, 'colibri-error');
            var errors = data.errors;
            if (errors) {
                _.each(errors, function(value, key) {
                    var $input = $('[name=' + key + ']', form);
                    $input.addClass('error');
                    $input.after('<div class="error-msg">' + value + '</div>');
                });

                if (options.error) {
                    options.error();
                }
            }
        } else {
            colibri(options.successMessage);
            if (options.success) {
                options.success();
            }
        }
        button.removeAttr('disabled');
    }).error(function() {
        colibri(options.errorMessage, 'colibri-error');
        button.removeAttr('disabled');
    });
};

Yasound.Utils.disableFX = function() {
    Yasound.App.enableFX = false;
};

Yasound.Utils.enableFX = function () {
    if (Yasound.App.isMobile) {
        // fadeIn/fadeOut sucks on iPad
        Yasound.App.enableFX = false;
        return;
    }

    if ($.browser.msie) {
        if ($.browser.version == '8.0' || $.browser.version == '7.0' || $.browser.version == '6.0') {
            Yasound.App.enableFX = false;
            return;
        }
    }
    Yasound.App.enableFX = true;
};

Yasound.Utils.dialog = function (options, body) {
    var d = {};
    if ( (typeof options) === (typeof d) ) {
        title = options.title || gettext('Information');
        content = options.content || gettext('Information');
        closeButton = options.closeButton || gettext('Close');
        cancelButton = options.cancelButton || false;
        onClose = options.onClose || function () {};
        $('#modal-dialog h3').html(title);
        $('#modal-dialog p').html(content);
        $('#modal-dialog .btn-primary').html(closeButton);

        if (cancelButton) {
            $('#modal-dialog .btn-cancel').show();
            $('#modal-dialog .btn-cancel').html(cancelButton);
        } else {
            $('#modal-dialog .btn-cancel').hide();
        }
        $('#modal-dialog').modal('show');
        $('#modal-dialog .btn-primary').one('click', onClose);
    } else {
        $('#modal-dialog h3').html(options);
        $('#modal-dialog p').html(body);
        $('#modal-dialog .btn-cancel').hide();
        $('#modal-dialog').modal('show');
    }
};

Yasound.Utils.getUrlVars = function() {
    var vars = [], hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for(var i = 0; i < hashes.length; i++) {
        hash = hashes[i].split('=');
        vars.push(hash[0]);
        vars[hash[0]] = hash[1];
    }
    return vars;
};
