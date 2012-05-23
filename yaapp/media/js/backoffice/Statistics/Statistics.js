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
        collapsed: true,
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
        collapsed: true,
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
        collapsed: true,
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

Yasound.Statistics.UI.AnimatorsGraph = function () {
    var chart = Ext.ComponentMgr.create({
        height: 300,
        xtype: 'chartpanel',
        url: '/yabackoffice/metrics/graphs/animators/',
        fields: [ 'timestamp', 'animator_activity' ],
        xField: 'timestamp',
        yField: 'animator_activity'
    });
    return {
        title: gettext('Radio animators activity'),
        id: 'animators-graph',
        items: [ chart ],
        tools: [ {
            id: 'refresh',
            handler: function (event, toolEl, panel) {
                panel.reload(panel);
            }
        } ],
        reload: function (component) {
            chart.reload(chart);
        }
    }
}

Yasound.Statistics.UI.SharesGraph = function () {
    var chart = Ext.ComponentMgr.create({
        height: 300,
        xtype: 'stackedbarchart',
        store: new Ext.data.JsonStore({
            url: '/yabackoffice/metrics/graphs/shares/',
            root: 'data',
            idProperty: 'timestamp',
            fields: [ 'timestamp', 'share_facebook_activity', 'share_twitter_activity', 'share_email_activity' ]
        }),
        yField: 'timestamp',
        xAxis: new Ext.chart.NumericAxis({
            stackingEnabled: true
        }),
        series: [ {
            xField: 'share_facebook_activity',
            displayName: 'Facebook'
        }, {
            xField: 'share_twitter_activity',
            displayName: 'Twitter'
        }, {
            xField: 'share_email_activity',
            displayName: 'email'
        } ],
        reload: function(component) {
            component.store.load();
        }
    });

    return {
        title: gettext('Share activity'),
        id: 'shares-graph',
        items: [ chart ],
        tools: [ {
            id: 'refresh',
            handler: function (event, toolEl, panel) {
                panel.reload(panel);
            }
        } ],
        reload: function (component) {
            chart.reload(chart);
        }
    }
}

Yasound.Statistics.UI.Panel = function () {
    return {
        xtype: 'portal',
        title: gettext('Statistics'),
        id: 'statistics-panel',
        items: [
                {
                    columnWidth: .50,
                    style: 'padding:10px 0 10px 10px',
                    items: [ Yasound.Statistics.UI.AnimatorsGraph(), Yasound.Statistics.UI.SharesGraph(), Yasound.Statistics.UI.Metrics(),
                            Yasound.Statistics.UI.PastMonthMetrics(), Yasound.Statistics.UI.PastYearMetrics(), {
                                title: gettext('Latests radios'),
                                collapsed: true,
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
                                    collapsed: true,
                                    id: 'stats-latest-radios',
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

            var keyfigures = Ext.getCmp('stats-keyfigures');
            keyfigures.reload(keyfigures);

            var metrics = Ext.getCmp('stats-metrics');
            metrics.reload(metrics);

            var pastMonthMetrics = Ext.getCmp('stats-past-month-metrics');
            pastMonthMetrics.reload(pastMonthMetrics);

            var pastYearMetrics = Ext.getCmp('stats-past-year-metrics');
            pastYearMetrics.reload(pastYearMetrics);

            var animatorsGraph = Ext.getCmp('animators-graph');
            animatorsGraph.reload(animatorsGraph);

            var sharesGraph = Ext.getCmp('shares-graph');
            sharesGraph.reload(sharesGraph);
        }
    };
}