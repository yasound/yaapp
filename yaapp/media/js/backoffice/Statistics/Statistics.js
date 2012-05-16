//------------------------------------------
// Datastore
//------------------------------------------

//------------------------------------------
// Handlers
//------------------------------------------

//------------------------------------------
// UI
//------------------------------------------
Yasound.Statistics.UI.Metrics = function () {
    return {
        title: gettext('Metrics'),
        layout: 'fit',
        id: 'stats-metrics',
        autoScroll: true,
        reload: function (panel) {
            panel.load({
                url: '/yabackoffice/metrics/',
                text: gettext('Loading...')
            });
        },
        tools: [ {
            id: 'refresh',
            handler: function (event, toolEl, panel) {
                panel.reload(panel);
            }
        } ]
    };
};

Yasound.Statistics.UI.PastMonthMetrics = function () {
    return {
        title: gettext('Last month metrics'),
        layout: 'fit',
        id: 'stats-past-month-metrics',
        autoScroll: true,
        reload: function (panel) {
            panel.load({
                url: '/yabackoffice/past_month_metrics/',
                text: gettext('Loading...')
            });
        },
        tools: [ {
            id: 'refresh',
            handler: function (event, toolEl, panel) {
                panel.reload(panel);
            }
        } ]
    };
};

Yasound.Statistics.UI.PastYearMetrics = function () {
    return {
        title: gettext('Last 12 months metrics'),
        layout: 'fit',
        id: 'stats-past-year-metrics',
        autoScroll: true,
        reload: function (panel) {
            panel.load({
                url: '/yabackoffice/past_year_metrics/',
                text: gettext('Loading...')
            });
        },
        tools: [ {
            id: 'refresh',
            handler: function (event, toolEl, panel) {
                panel.reload(panel);
            }
        } ]
    };
};
Yasound.Statistics.UI.Panel = function () {
    return {
        xtype: 'portal',
        title: gettext('Statistics'),
        id: 'statistics-panel',
        items: [ {
            columnWidth: .50,
            style: 'padding:10px 0 10px 10px',
            items: [ Yasound.Statistics.UI.Metrics(), Yasound.Statistics.UI.PastMonthMetrics(), Yasound.Statistics.UI.PastYearMetrics(), {
                title: gettext('Latests radios'),
                layout: 'fit',
                tools: [ {
                    id: 'refresh',
                    handler: function (event, toolEl, panel) {
                        Ext.getCmp('stats-latest-radios').getStore().reload();
                    }
                } ],
                items: [ {
                    xtype: 'radiogrid',
                    url: '/yabackoffice/radios?rtype=latest',
                    id: 'stats-latest-radios',
                    enablePagination: true,
                    enableFilters: false,
                    height: 400
                } ]
            }, {
                title: gettext('Biggest radios'),
                layout: 'fit',
                tools: [ {
                    id: 'refresh',
                    handler: function (event, toolEl, panel) {
                        Ext.getCmp('stats-biggest-radios').getStore().reload();
                    }
                } ],
                items: [ {
                    xtype: 'radiogrid',
                    url: '/yabackoffice/radios?rtype=biggest',
                    id: 'stats-biggest-radios',
                    enablePagination: true,
                    enableFilters: false,
                    height: 400
                } ]
            } ]
        }, {
            columnWidth: .50,
            style: 'padding:10px 0 10px 10px',
            items: [ {
                title: gettext('Key figures'),
                layout: 'fit',
                id: 'stats-keyfigures',
                reload: function (panel) {
                    panel.load({
                        url: '/yabackoffice/keyfigures/',
                        text: gettext('Loading...')
                    });
                },
                tools: [ {
                    id: 'refresh',
                    handler: function (event, toolEl, panel) {
                        panel.reload(panel);
                    }
                } ],
            } ]
        } ],
        updateData: function (component) {
            Ext.getCmp('stats-latest-radios').getStore().reload();
            Ext.getCmp('stats-biggest-radios').getStore().reload();

            var keyfigures = Ext.getCmp('stats-keyfigures');
            keyfigures.reload(keyfigures);

            var metrics = Ext.getCmp('stats-metrics');
            metrics.reload(metrics);

            var pastMonthMetrics = Ext.getCmp('stats-past-month-metrics');
            pastMonthMetrics.reload(pastMonthMetrics);

            var pastYearMetrics = Ext.getCmp('stats-past-year-metrics');
            pastYearMetrics.reload(pastYearMetrics);
        }
    };
}