window.ich.loadRemoteTemplate = function (path, name, callback, data) {
    if (!callback) {
        callback = function() {};
    }
    if (data) {
        delete window.ich[name];
        delete window.ich.templates[name];
        jQuery.get(Yasound.App.root + "tpl/" + path + "/", data, function (data) {
            window.ich.addTemplate(name, data);
            callback();
        });
        return;
    }

    if (!ich.templates[name]) {
        jQuery.get(Yasound.App.root + "tpl/" + path + "/", data, function (data) {
            window.ich.addTemplate(name, data);
            callback();
        });
    } else {
        callback();
    }
};