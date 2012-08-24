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

Yasound.Utils.cellsPerPage = function() {
    var viewportHeight = $(window).height();
    var headerHeight = $('#header').height();
    var containerHeight = viewportHeight - headerHeight;

    var cellHeight = 217;

    var rows =  Math.ceil(containerHeight / cellHeight);
    return rows*4;
};

Yasound.Utils.userCellsPerPage = function() {
    var viewportHeight = $(window).height();
    var headerHeight = $('#header').height();
    var containerHeight = viewportHeight - headerHeight;

    var cellHeight = 158;

    var rows =  Math.ceil(containerHeight / cellHeight);
    return rows*5;
};

Yasound.Utils.saveStickyView = function(key, view) {
    Yasound.App.stickyViews[key] = view;
};

Yasound.Utils.getStickyView = function (key) {
    return Yasound.App.stickyViews[key];
};

Yasound.Utils.submitForm = function (options) {
    var options = options || {};
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
    }).error(function() {
        colibri(options.errorMessage, 'colibri-error');
    });
};

Yasound.Utils.disableFX = function() {
    Yasound.App.enableFX = false;
}

Yasound.Utils.enableFX = function () {
    if ($.browser.msie) {
        if ($.browser.version == '8.0' || $.browser.version == '7.0' || $.browser.version == '6.0') {
            Yasound.App.enableFX = false;
            return;
        }
    }
    Yasound.App.enableFX = true;
}
