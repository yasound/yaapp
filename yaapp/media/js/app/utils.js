Namespace('Yasound.Utils');

Yasound.Utils.momentDate = function(rawDate) {
    var timeZone = '+01:00';
    if (moment().isDST()) {
        timeZone = '+02:00';
    }
    // if start_date contains microsecond precision, we remove it
    var date = rawDate.substr(0, 19);
    return moment(date + timeZone);
}

Yasound.Utils.formatDate = function(rawDate) {
    return Yasound.Utils.momentDate(rawDate).format('LLLL');
}

Yasound.Utils.humanizeDate = function(rawDate) {
    return Yasound.Utils.momentDate(rawDate).fromNow();
}

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
}

Yasound.Utils.saveStickyView = function(key, view) {
    Yasound.App.stickyViews[key] = view;
}

Yasound.Utils.getStickyView = function (key) {
    return Yasound.App.stickyViews[key];
}