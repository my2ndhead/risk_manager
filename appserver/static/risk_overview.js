require.config({
    paths: {
        "app": "../app"
    }
});
require([
    "splunkjs/mvc",
    "splunkjs/mvc/utils",
    "splunkjs/mvc/tokenutils",
    "underscore",
    "jquery",
    "splunkjs/mvc/simplexml",
    'splunkjs/mvc/tableview',
    'splunkjs/mvc/chartview',
    'splunkjs/mvc/searchmanager',
    'splunk.util',
    'splunkjs/mvc/simplexml/element/single',    
    'app/risk_manager/views/single_trend'
], function(
        mvc,
        utils,
        TokenUtils,
        _,
        $,
        DashboardController,
        TableView,
        ChartView,
        SearchManager,
        splunkUtil,
        SingleElement,
        TrendIndicator
    ) {


    // Find all single value elements created on the dashboard
    _(mvc.Components.toJSON()).chain().filter(function(el) {
        return el instanceof SingleElement;
    }).each(function(singleElement) {
        singleElement.getVisualization(function(single) {
            // Inject a new element after the single value visualization
            var $el = $('<div></div>').addClass('trend-ctr').insertAfter(single.$el);
            // Create a new change view to attach to the single value visualization
            new TrendIndicator(_.extend(single.settings.toJSON(), {
                el: $el,
                id: _.uniqueId('single')
            }));
        });
    });
});
