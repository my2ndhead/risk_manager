require.config({
    paths: {
        "app": "../app"
    },
    shim: {
        "app/risk_manager/contrib/handsontable-0.12.2/handsontable.full.min": {
            deps: ['css!../handsontable-0.12.2/handsontable.full.min.css'],
            exports: "Handsontable"
        },
    }
});


define(function(require, exports, module) {
    
    var _ = require('underscore');
    var $ = require('jquery');
    var mvc = require('splunkjs/mvc');
    var SimpleSplunkView = require('splunkjs/mvc/simplesplunkview');
    var Handsontable = require('app/risk_manager/contrib/handsontable-0.12.2/handsontable.full.min');
    var splunkUtil = require('splunk.util');

    //require("css!../lib/handsontable.full.css");

    var RiskSettingsView = SimpleSplunkView.extend({
        className: "risksettingsview",

        del_key_container: '',

        // Set options for the visualization
        options: {
            data: "preview",  // The data results model from a search
        },
        output_mode: 'json',

       
        createView: function() { 
            console.log("createView");
            return { container: this.$el, } ;
        },

        updateView: function(viz, data) {

            console.log("updateView", data);

            this.$el.empty();

            $('<div />').attr('id', 'handson_container').appendTo(this.$el);

            headers = [ { col: "_key", tooltip: false }, 
                        { col: "alert", tooltip: false },
                        { col: "title", tooltip: "Configure a title including results for better identification" },
                        { col: "risk_field", tooltip: "Select a field for scoring risks" },
                        { col: "risk_score", tooltip: "Select a risk score"},
                        { col: "collect_evidence", tooltip: "Select, if evicence should be collected"},
                        { col: "encrypt_evidence", tooltip: "Select, if evidence should be encrypted"} ];
            $("#handson_container").handsontable({
                data: data,
                //colHeaders: ["_key", "alert", "risk_field", "risk_score", "collect_evidence", "encrypt_evidence"],
                columns: [
                    {
                        data: "_key",
                        readOnly: true
                    },
                    {
                        data: "alert",
                    },
                    {
                        data: "title",
                    },
                    {
                        data: "risk_field",
                    },
                    {
                        data: "risk_score",
                    },
                    {
                        data: "collect_evidence",
                        type: "checkbox"
                    },
                    {
                        data: "encrypt_evidence",
                        type: "checkbox"
                    },

                ],
                colHeaders: true,
                colHeaders: function (col) {
                    if (headers[col]["tooltip"] != false) {
                        colval = headers[col]["col"] + '<a href="#" data-container="body" class="tooltip-link" data-toggle="tooltip" title="'+ headers[col]["tooltip"] +'">?</a>';
                    }
                    else {
                        colval = headers[col]["col"];
                    }
                    return colval;
                },
                stretchH: 'all',
                contextMenu: ['row_above', 'row_below', 'remove_row', 'undo', 'redo'],
                startRows: 1,
                startCols: 1,
                minSpareRows: 1,
                minSpareCols: 0,
                afterRender: function() {
                    $(function () {
                        $('[data-toggle="tooltip"]').tooltip()
                    })
                },
                beforeRemoveRow: function(row) {
                    var data = $("#handson_container").data('handsontable').getData();
                    if(confirm('Are you sure to remove settings for alert "' + data[row]['alert'] + '"?')) {
                        this.del_key_container = data[row]['_key'];
                        return true;
                    } else {
                        return false;
                    }
                },
                afterRemoveRow: function(row) {
                    console.debug("afterRemoveRow");
                    //var data = $("#handson_container").data('handsontable').getData();
                    console.debug("row", row);
                    //console.debug("data", data);
                    console.debug("key", this.del_key_container);

                    var post_data = {
                        key    : this.del_key_container
                    };

                    var url = splunkUtil.make_url('/custom/risk_manager/risk_settings/delete');
                    console.debug("url", url);

                    $.ajax( url,
                            {
                                uri:  url,
                                type: 'POST',
                                data: post_data,
                                
                               
                                success: function(jqXHR, textStatus){
                                    this.del_key_container = '';
                                    // Reload the table
                                    mvc.Components.get("risk_settings_search").startSearch()
                                    console.debug("success");
                                },
                                
                                // Handle cases where the file could not be found or the user did not have permissions
                                complete: function(jqXHR, textStatus){
                                    console.debug("complete");
                                },
                                
                                error: function(jqXHR,textStatus,errorThrown) {
                                    console.log("Error");
                                } 
                            }
                    );
                }
            });
            //console.debug("id", id);


          //debugger;
          //id

        },

        // Override this method to format the data for the view
        formatData: function(data) {
            console.log("formatData", data);

            myData = []
             _(data).chain().map(function(val) {
                return {
                    _key: val.key,
                    alert: val.alert, 
                    title: val.title,
                    risk_field: val.risk_field,
                    risk_score: val.risk_score, 
                    collect_evidence: parseInt(val.collect_evidence) ? true : false, 
                    encrypt_evidence: parseInt(val.encrypt_evidence) ? true : false, 
                };
            }).each(function(line) {
                myData.push(line);        
            });

            return myData;
        },

    });
    return RiskSettingsView;
});
