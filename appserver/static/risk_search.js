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
    'app/alert_manager/views/single_trend',
    'util/moment'   
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
        TrendIndicator,
        moment         
    ) {

    var HiddenCellRenderer = TableView.BaseCellRenderer.extend({
        canRender: function(cell) {
            // Only use the cell renderer for the specific field
            return (cell.field==="decrypt_command");
        },
        render: function($td, cell) {
            // ADD class to cell -> CSS
            return _(['decrypt_command']).contains(cell.field);
        }
    });

    mvc.Components.get('risk_contributing_data').getVisualization(function(tableView) {
        // Add custom cell renderer
        tableView.table.addCellRenderer(new HiddenCellRenderer());
        tableView.table.render();

    });

    mvc.Components.get('risk_contributing_data_decrypted').getVisualization(function(tableView) {
        // Add custom cell renderer
        tableView.table.addCellRenderer(new HiddenCellRenderer());
        tableView.table.render();

    });

});    
