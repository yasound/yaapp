Ext.BLANK_IMAGE_URL = '/media/extjs/resources/images/default/s.gif';
Ext.chart.Chart.CHART_URL = '/media/extjs/resources/charts.swf';
Ext.namespace("Yasound.Backoffice.UI", "Yasound.Backoffice.Handler", "Yasound.Backoffice.Data");
Ext.namespace("Yasound.Radios.UI", "Yasound.Radios.Handler", "Yasound.Radios.Data");
Ext.namespace("Yasound.Upload.UI", "Yasound.Upload.Handler", "Yasound.Upload.Data");
Ext.namespace("Yasound.SearchEngine.UI", "Yasound.SearchEngine.Handler", "Yasound.SearchEngine.Data");
Ext.namespace("Yasound.Invitations.UI", "Yasound.Invitations.Handler", "Yasound.Invitations.Data");
Ext.namespace("Yasound.Users.UI", "Yasound.Users.Handler", "Yasound.Users.Data");
Ext.namespace("Yasound.Statistics.UI", "Yasound.Statistics.Handler", "Yasound.Statistics.Data");
Ext.namespace("Yasound.Utils");
Ext.namespace("Yasound.Menus.UI", "Yasound.Menus.Handler", "Yasound.Menus.Data");
Ext.namespace("Yasound.Moderation.UI", "Yasound.Moderation.Handler", "Yasound.Moderation.Data");
Ext.namespace("Yasound.WallEvents.UI", "Yasound.WallEvents.Handler", "Yasound.WallEvents.Data");
Ext.namespace("Yasound.RadioActivityScoreSettings.UI", "Yasound.RadioActivityScoreSettings.Handler", "Yasound.RadioActivityScoreSettings.Data");
Ext.namespace("Yasound.Settings.UI", "Yasound.Settings.Handler", "Yasound.Settings.Data");
Ext.namespace("Yasound.Premium.UI", "Yasound.Premium.Handler", "Yasound.Premium.Data");
Ext.namespace("Yasound.Geoperm.UI", "Yasound.Geoperm.Handler", "Yasound.Geoperm.Data");

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

    var tabPanelRadios = {
        id: 'radios-tab',
        expanded: false,
        listeners: {
            'tabchange': function(tabPanel, tab){
                Ext.History.add(tabPanel.id + '/' + tab.id);
            }
        },
        items: [{
            title: gettext('Radios'),
            id: 'radios-top-panel',
            tabTip: gettext('Song management'),
            style: 'padding: 10px;',
            html: '<h1>Radio management</h1>',
            listeners: {
                'activate': function(p){
                    var tabPanel = p.findParentByType('grouptab');
                    var nextItem = p.nextSibling();
                    tabPanel.setActiveTab(nextItem);
                }
            }
        }, Ext.apply(Yasound.Radios.UI.RadiosPanel(), {
            iconCls: 'x-icon-templates'
        }), Ext.apply(Yasound.Backoffice.UI.UnmatchedSongsPanel(), {
            iconCls: 'x-icon-templates',
            tabTip: gettext('Unmatched songs')
        }),Ext.apply(Yasound.Backoffice.UI.MissingSongsPanel(), {
            iconCls: 'x-icon-templates',
            tabTip: gettext('Missing songs')
        }), Ext.apply(Yasound.Upload.UI.UploadSongsPanel(), {
            iconCls: 'x-icon-templates',
            tabTip: gettext('Upload new songs to yasound')
        }), Ext.apply(Yasound.Backoffice.UI.AllSongsPanel(), {
            iconCls: 'x-icon-templates',
            tabTip: gettext('All songs')
        })]
    };

    var tabPanelInvitations = {
        id: 'invitations-tab',
        expanded: false,
        listeners: {
            'tabchange': function(tabPanel, tab){
                Ext.History.add(tabPanel.id + '/' + tab.id);
            }
        },
        items: [{
            title: gettext('Invitations'),
            id: 'invitations-top-panel',
            style: 'padding: 10px;',
            listeners: {
                'activate': function(p){
                    var tabPanel = p.findParentByType('grouptab');
                    var nextItem = p.nextSibling();
                    tabPanel.setActiveTab(nextItem);
                }
            }
        }, Ext.apply(Yasound.Invitations.UI.Panel(), {
            iconCls: 'x-icon-templates'
        })]
    };

    var tabPanelModeration = {
            id: 'moderation-tab',
            expanded: false,
            listeners: {
                'tabchange': function(tabPanel, tab){
                    Ext.History.add(tabPanel.id + '/' + tab.id);
                }
            },
            items: [{
                title: gettext('Moderation'),
                id: 'moderation-top-panel',
                tabTip: gettext('Moderation'),
                style: 'padding: 10px;',
                html: '<h1>Moderation</h1>',
                listeners: {
                    'activate': function(p){
                        var tabPanel = p.findParentByType('grouptab');
                        var nextItem = p.nextSibling();
                        tabPanel.setActiveTab(nextItem);
                    }
                }
            }, Ext.apply(Yasound.Moderation.UI.UsersPanel(), {
                iconCls: 'x-icon-templates'
            }), Ext.apply(Yasound.Moderation.UI.RadiosPanel(), {
                iconCls: 'x-icon-templates'
            }), Ext.apply(Yasound.Moderation.UI.AbusePanel(), {
                iconCls: 'x-icon-templates'
            })]
        };

    var tabPanelUsers = {
            id: 'user-tab',
            expanded: false,
            listeners: {
                'tabchange': function(tabPanel, tab){
                    Ext.History.add(tabPanel.id + '/' + tab.id);
                }
            },
            items: [{
                title: gettext('Users'),
                id: 'user-top-panel',
                tabTip: gettext('Users'),
                style: 'padding: 10px;',
                html: '<h1>Users</h1>',
                listeners: {
                    'activate': function(p){
                        var tabPanel = p.findParentByType('grouptab');
                        var nextItem = p.nextSibling();
                        tabPanel.setActiveTab(nextItem);
                    }
                }
            }, Ext.apply(Yasound.Users.UI.UsersPanel(), {
                iconCls: 'x-icon-templates'
            }), Ext.apply(Yasound.Users.UI.HistoryPanel(), {
                iconCls: 'x-icon-templates'
            })]
        };

    var tabPanelStatistics = {
        id: 'statistics-tab',
        expanded: false,
        listeners: {
            'tabchange': function(tabPanel, tab){
                Ext.History.add(tabPanel.id + '/' + tab.id);
            }
        },
        items: [{
            title: gettext('Statistics'),
            id: 'statistics-top-panel',
            tabTip: gettext('Useful stats'),
            style: 'padding: 10px;',
            html: '<h1>Statistics</h1>',
            listeners: {
                'activate': function(p){
                    var tabPanel = p.findParentByType('grouptab');
                    var nextItem = p.nextSibling();
                    tabPanel.setActiveTab(nextItem);
                }
            }
        }, Ext.apply(Yasound.Statistics.UI.Panel(), {
            iconCls: 'x-icon-templates'
        }), Ext.apply(Yasound.Backoffice.UI.MostPopularSongsPanel(), {
            iconCls: 'x-icon-templates',
            tabTip: gettext('Most popular songs')
        }), Ext.apply(Yasound.Backoffice.UI.RejectedSongsPanel(), {
            iconCls: 'x-icon-templates',
            tabTip: gettext('Rejected songs')
        }), Ext.apply(Yasound.Statistics.UI.RadiosPanel(), {
            iconCls: 'x-icon-templates',
            tabTip: gettext('Radios stats')
        })]
    };

    var tabPanelMenus = {
            id: 'menus-tab',
            expanded: false,
            listeners: {
                'tabchange': function(tabPanel, tab){
                    Ext.History.add(tabPanel.id + '/' + tab.id);
                }
            },
            items: [{
                title: gettext('Menus'),
                id: 'menus-top-panel',
                style: 'padding: 10px;',
                listeners: {
                    'activate': function(p){
                        var tabPanel = p.findParentByType('grouptab');
                        var nextItem = p.nextSibling();
                        tabPanel.setActiveTab(nextItem);
                    }
                }
            }, Ext.apply(Yasound.Menus.UI.Panel(), {
                iconCls: 'x-icon-templates'
            })]
        };

    var tabPanelActivityScore = {
            id: 'activity-score-tab',
            expanded: false,
            listeners: {
                'tabchange': function(tabPanel, tab){
                    Ext.History.add(tabPanel.id + '/' + tab.id);
                }
            },
            items: [{
                title: gettext('Activity score factors'),
                id: 'activity-score-top-panel',
                tabTip: gettext('factors to compute radio activity score'),
                style: 'padding: 10px;',
                html: '<h1>Activity Score factors</h1>',
                listeners: {
                    'activate': function(p){
                        var tabPanel = p.findParentByType('grouptab');
                        var nextItem = p.nextSibling();
                        tabPanel.setActiveTab(nextItem);
                    }
                }
            }, Ext.apply(Yasound.RadioActivityScoreSettings.UI.Panel(), {
                iconCls: 'x-icon-templates'
            })]
        };

    var tabPanelPremium = {
            id: 'premium-tab',
            expanded: false,
            listeners: {
                'tabchange': function(tabPanel, tab){
                    Ext.History.add(tabPanel.id + '/' + tab.id);
                }
            },
            items: [{
                title: gettext('Premium'),
                id: 'premium-top-panel',
                tabTip: gettext('premium settings'),
                style: 'padding: 10px;',
                html: '<h1>Premium</h1>',
                listeners: {
                    'activate': function(p){
                        var tabPanel = p.findParentByType('grouptab');
                        var nextItem = p.nextSibling();
                        tabPanel.setActiveTab(nextItem);
                    }
                }
            }, Ext.apply(Yasound.Premium.UI.PromocodesPanel(), {
                iconCls: 'x-icon-templates'
            }), Ext.apply(Yasound.Premium.UI.PromocodesGroupUsagePanel(), {
                iconCls: 'x-icon-templates'
            })]
        };

    var tabPanelGeoperm = {
            id: 'geoperm-tab',
            expanded: false,
            listeners: {
                'tabchange': function(tabPanel, tab){
                    Ext.History.add(tabPanel.id + '/' + tab.id);
                }
            },
            items: [{
                title: gettext('Geo permissions'),
                id: 'geoperm-top-panel',
                tabTip: gettext('Geo permissions'),
                style: 'padding: 10px;',
                html: '<h1>Geo permissions</h1>',
                listeners: {
                    'activate': function(p){
                        var tabPanel = p.findParentByType('grouptab');
                        var nextItem = p.nextSibling();
                        tabPanel.setActiveTab(nextItem);
                    }
                }
            }, Ext.apply(Yasound.Geoperm.UI.Panel(), {
                iconCls: 'x-icon-templates'
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

    tabPanels.items.push(tabPanelRadios,
                         tabPanelInvitations,
                         tabPanelStatistics,
                         tabPanelModeration,
                         tabPanelUsers,
                         tabPanelMenus,
                         tabPanelActivityScore,
                         tabPanelPremium,
                         tabPanelGeoperm);

    var viewport = new Ext.Viewport({
        layout: 'fit',
        listeners: {
            beforerender: function(component){
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
