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
