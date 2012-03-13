

Yasound.Utils.DisplayLogWindow = function(logs){
    var win = new Ext.Window({
        title: 'Résultats',
        width: 500,
        height: 400,
        autoScroll: true,
        modal: true,
        preventBodyReset: true,
        html: '<pre>' + logs + '</pre>',
        buttonAlign: 'center',
        buttons: [{
            text: gettext('Close'),
            handler: function(){
                win.close();
            }
        }],
        draggable: true
    });
    win.on('show', function(){
        win.center();
    });
    win.show(this);
};