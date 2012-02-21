Ext.BLANK_IMAGE_URL = '/media/extjs/resources/images/default/s.gif';
Ext.namespace("Yasound.Backoffice.UI", "Yasound.Backoffice.Handler", "Yasound.Backoffice.Data");
Ext.namespace("Yasound.Utils");


//------------------------------------------
// Datastore
//------------------------------------------

//------------------------------------------
// Handlers
//------------------------------------------

Yasound.Backoffice.Handler.HandleUrlToken = function(token){
    if (token) {
        var parts = token.split('/');
        var parent = Ext.getCmp(parts[0]);
        if (parent) {
            var component_id = parts[1];
            var argumentCount = parts.length - 2;
            var component = Ext.getCmp(component_id);
            
            var args = [];
            args.push(component);
            
            if (argumentCount > 0) {
                var i;
                for (i = 0; i < argumentCount; i++) {
                    var arg = parts[2 + i];
                    args.push(arg);
                }
            }
            parent.getLayout().setActiveItem(component_id);
            component.setVisible(true);
            if (component && component.updateData) {
                component.updateData.apply(this, args);
            }
        }
    }
};

//------------------------------------------
// UI
//------------------------------------------
Ext.onReady(function(){
    var loadingMask = Ext.get('loading-mask');
    var loading = Ext.get('loading');
    //  Hide loading message
    loading.hide();
    loadingMask.hide();
    Ext.QuickTips.init();
    Ext.History.init();
    
    var tabPanelSongs = {
        id: 'songs-tab',
        expanded: false,
        listeners: {
            'tabchange': function(tabPanel, tab){
                Ext.History.add(tabPanel.id + '/' + tab.id);
            }
        },
        items: [{
            title: gettext('Songs'),
            id: 'songs-top-panel',
            tabTip: gettext('Song management'),
            style: 'padding: 10px;',
            html: '<h1>Song management</h1>',
            listeners: {
                'activate': function(p){
                    var tabPanel = p.findParentByType('grouptab');
                    var nextItem = p.nextSibling();
                    tabPanel.setActiveTab(nextItem);
                }
            }
        }, Ext.apply(Yasound.Backoffice.UI.UnmatchedSongsPanel(), {
            iconCls: 'x-icon-templates',
            tabTip: gettext('Unmatched songs')
        })]
    };

    var tabPanels = {
        xtype: 'grouptabpanel',
        id: 'group-panel',
        headerAsText: true,
        border: false,
        region: 'center',
        tabWidth: 200,
        activeGroup: 0,
        items: []
    };
    
    tabPanels.items.push(tabPanelSongs);

    var viewport = new Ext.Viewport({
        layout: 'fit',
        listeners: {
            afterrender: function(component){
                var params = document.URL.split('#');
                if (params.length > 1) {
                    var token = params[1];
                    Yasound.Backoffice.Handler.HandleUrlToken.defer(1000, this, [token]);
                }
            }
            
        },
        items: [{
            layout: 'border',
            border: false,
            items: [{
                region: 'north',
                xtype: 'panel',
                border: false,
                contentEl: 'header'
            }, {
                xtype: 'panel',
                region: 'center',
                layout: 'fit',
                items: [tabPanels]
            }]
        }]
    });
    
    // Handle this change event in order to restore the UI to the appropriate history state
    Ext.History.on('change', function(token){
    	Yasound.Backoffice.Handler.HandleUrlToken(token);
    });
});

Ext.EventManager.on(window, 'beforeunload', function(e){
    //e.stopEvent();
});
