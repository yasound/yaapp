//------------------------------------------
// Datastore
//------------------------------------------

//------------------------------------------
// Handlers
//------------------------------------------
Yasound.Statistics.ExportMetrics = function () {
    var maskingAjax = new Ext.data.Connection({});

    maskingAjax.request({
        disableCaching: true,
        url: String.format('/yabackoffice/metrics/export/'),
        form: Ext.fly('frmDummy'),
        method: 'POST',
        timeout: 1000 * 60 * 5,
        isUpload: true
    });
};

Yasound.Statistics.ExportPastMonthMetrics = function () {
    var maskingAjax = new Ext.data.Connection({});

    maskingAjax.request({
        disableCaching: true,
        url: String.format('/yabackoffice/past_month_metrics/export/'),
        form: Ext.fly('frmDummy'),
        method: 'POST',
        timeout: 1000 * 60 * 5,
        isUpload: true
    });
};

Yasound.Statistics.ExportPastYearMetrics = function () {
    var maskingAjax = new Ext.data.Connection({});

    maskingAjax.request({
        disableCaching: true,
        url: String.format('/yabackoffice/past_year_metrics/export/'),
        form: Ext.fly('frmDummy'),
        method: 'POST',
        timeout: 1000 * 60 * 5,
        isUpload: true
    });
};



//------------------------------------------
// UI
//------------------------------------------
Yasound.Statistics.UI.Metrics = function () {
    return {
        title: gettext('Metrics'),
        collapsed: false,
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
        }, {
            id: 'save',
            handler: function (event, toolEl, panel) {
                Yasound.Statistics.ExportMetrics();
            }
        }]
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
        }, {
            id: 'save',
            handler: function (event, toolEl, panel) {
                Yasound.Statistics.ExportPastMonthMetrics();
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
        }, {
            id: 'save',
            handler: function (event, toolEl, panel) {
                Yasound.Statistics.ExportPastYearMetrics();
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
    };
};

Yasound.Statistics.UI.ListenGraph = function () {
    var chart = Ext.ComponentMgr.create({
        height: 300,
        xtype: 'chartpanel',
        url: '/yabackoffice/metrics/graphs/listen/',
        fields: [ 'timestamp', 'listen_activity' ],
        xField: 'timestamp',
        yField: 'listen_activity'
    });
    return {
        title: gettext('Listen activity'),
        id: 'listen-graph',
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
    };
};

Yasound.Statistics.UI.PostsGraph = function () {
    var chart = Ext.ComponentMgr.create({
        height: 300,
        xtype: 'chartpanel',
        url: '/yabackoffice/metrics/graphs/posts/',
        fields: [ 'message_count', 'user_count' ],
        xField: 'message_count',
        yField: 'user_count',
        xTitle: gettext('Number of messages'),
        yTitle: gettext('Users')
    });
    return {
        title: gettext('Message count per user'),
        id: 'posts-graph',
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
    };
};

Yasound.Statistics.UI.LikesGraph = function () {
    var chart = Ext.ComponentMgr.create({
        height: 300,
        xtype: 'chartpanel',
        url: '/yabackoffice/metrics/graphs/likes/',
        fields: [ 'like_count', 'user_count' ],
        xField: 'like_count',
        yField: 'user_count',
        xTitle: gettext('Number of likes'),
        yTitle: gettext('Users')
    });
    return {
        title: gettext('Likes per user'),
        id: 'likes-graph',
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
    };
};

Yasound.Statistics.UI.SharesGraph = function () {
    var chart = Ext.ComponentMgr.create({
        height: 300,
        xtype: 'stackedcolumnchart',
        store: new Ext.data.JsonStore({
            url: '/yabackoffice/metrics/graphs/shares/',
            root: 'data',
            idProperty: 'timestamp',
            fields: [ 'timestamp', 'share_facebook_activity', 'share_twitter_activity', 'share_email_activity' ]
        }),
        xField: 'timestamp',
        yAxis: new Ext.chart.NumericAxis({
            stackingEnabled: false
        }),
        series: [ {
            yField: 'share_facebook_activity',
            displayName: 'Facebook'
        }, {
            yField: 'share_twitter_activity',
            displayName: 'Twitter'
        }, {
            yField: 'share_email_activity',
            displayName: 'email'
        } ],
        reload: function (component) {
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
    };
};

Yasound.Statistics.UI.KeyFigures = function () {
    return {
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
        } ]
    };
};

Yasound.Statistics.UI.RadioTags = function () {
    return {
        title: gettext('Radio tags'),
        layout: 'fit',
        id: 'stats-radio-tags',
        reload: function (panel) {
            panel.load({
                url: '/yabackoffice/radio_tags/',
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
        items: [
                {
                    columnWidth: 0.33,
                    style: 'padding:10px 0 10px 10px',
                    items: [ Yasound.Statistics.UI.AnimatorsGraph(), Yasound.Statistics.UI.PostsGraph(), Yasound.Statistics.UI.LikesGraph(), Yasound.Statistics.UI.PastMonthMetrics(),
                            Yasound.Statistics.UI.PastYearMetrics(), Yasound.Statistics.UI.RadioTags() ]
                }, {
                    columnWidth: 0.33,
                    style: 'padding:10px 0 10px 10px',
                    items: [ Yasound.Statistics.UI.ListenGraph(), Yasound.Statistics.UI.Metrics() ]
                }, {
                    columnWidth: 0.33,
                    style: 'padding:10px 0 10px 10px',
                    items: [ Yasound.Statistics.UI.SharesGraph(), Yasound.Statistics.UI.KeyFigures() ]
                } ],
        updateData: function (component) {
            var keyfigures = Ext.getCmp('stats-keyfigures');
            keyfigures.reload(keyfigures);

            var tags = Ext.getCmp('stats-radio-tags');
            tags.reload(tags);

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

            var listenGraph = Ext.getCmp('listen-graph');
            listenGraph.reload(listenGraph);

            var postsGraph = Ext.getCmp('posts-graph');
            postsGraph.reload(postsGraph);

            var likesGraph = Ext.getCmp('likes-graph');
            likesGraph.reload(likesGraph);
        }
    };
};