'use strict';

/* Controllers */
function MainCtrl($scope, $http){
    $http.get('/logsets').success(function(response_json, status){
        $scope.logsets = response_json.data;
    });

}

function LogViewerCtrl($scope, $http, $routeParams, $filter){
    $scope.show_table = true;
    $scope.isInvalidDateRange = false;

    //complicated way to get the correct logset object from the logsets array
    $scope.logset = $filter('filter')($scope.logsets, {name: $routeParams.table_name})[0];

    $scope.$watch('log_row_filter', function(newValue, oldValue){
        var conditions = newValue.split(/\s*[\s,;]\s*/);//split on any of the following: space , ; with optional surrounding spaces
        if(conditions[conditions.length - 1] == ""){
            conditions.pop();
        }
        var valid_fields = $scope.logset.fields;
        $scope.log_row = {};
        angular.forEach(conditions, function (condition, index){
            var key, value, pair;
            pair = condition.split(/\s*[:=]\s*/);//split on : or = into key value pair
            key = pair[0].toLowerCase() || "";
            value = pair[1] || "";
            if(key == ""){
                return;
            }
            var i, key_regex = new RegExp('^'+key), isValid = false;
            for(i=0;i<valid_fields.length;i++){
                if(key_regex.test(valid_fields[i])){
                    key = valid_fields[i];
                    isValid = true;
                }
            }
            if(!isValid){
                console.log('here')
                return;
            }
            console.log(key+':'+value);
            $scope.log_row[key] = value;
        });
    });

    $scope.retrieve_logs = function(page_number){
        //correctly set from_datetime
        var from_datetime = moment($scope.from_time, "hh:mm A");
        from_datetime.date($scope.from_date.getDate());
        from_datetime.month($scope.from_date.getMonth());
        from_datetime.year($scope.from_date.getFullYear());

        //correctly set to_datetime
        var to_datetime = moment($scope.to_time, "hh:mm A");
        to_datetime.date($scope.to_date.getDate());
        to_datetime.month($scope.to_date.getMonth());
        to_datetime.year($scope.to_date.getFullYear());

        if(from_datetime.isAfter(to_datetime)){
            $scope.isInvalidDateRange = true;
            //don't get the data
        } else {
            $scope.isInvalidDateRange = false;
            $http.get(
                    '/data/'+$scope.logset.name,
                    {
                        params:{
                            from:from_datetime.unix(),
                            to:to_datetime.unix(),
                            page:page_number,
                        }
                    })
            .success(function(response_json, status){
                $scope.LogData = response_json.data;
                $scope.noOfPages = response_json.max_page;
            });
        }
    };

    $scope.min_date = moment.unix($scope.logset.date_range.min_date);
    $scope.max_date = moment.unix($scope.logset.date_range.max_date);

    $scope.to_date = moment($scope.max_date).toDate();
    $scope.to_time = $scope.max_date.format("hh:mm A");

    //checking whether duration between max_date and min_date is less than a day
    if(moment($scope.max_date).subtract('days', 1).isBefore($scope.min_date)){
        $scope.from_date = $scope.min_date.toDate();
        $scope.from_time = $scope.min_date.format("hh:mm A");
    } else {
        $scope.from_date = moment($scope.max_date).subtract('days', 1).toDate();
        $scope.from_time = $scope.to_time;
    }

    //defaults for pagination directive
    $scope.noOfPages = 0;
    $scope.currentPage = 0;
    $scope.maxSize = 10;

    $scope.retrieve_logs($scope.currentPage);

}

function AddTableCtrl($scope, $http, $routeParams){
    //optionally set table_name
    $scope.table_name = $routeParams.table_name || null;

    $scope.handleResponse = function(content, completed){
        if(completed && content.length > 0){
            $scope.response = angular.fromJson(content);
            if($scope.response.status == 'Success'){
                window.location.href = '/';
            } else {
                //incase upload fails
                console.log("here");
                $scope.alerts.insert({
                    type: "error"
                    , title: $scope.response.message || "Unexpected error occured, contact a system admin"
                });
                console.log("here");
            }
        }
    };
}

function GraphCtrl ($scope, $http, $routeParams,$filter) {
    
    $scope.data="testing";
    
    $scope.logset = $filter('filter')($scope.logsets, {name: $routeParams.table_name})[0];
    
    /*For HTTP status*/
    $http.get(
                    '/data/'+$scope.logset.name,
                    {
                        params:{
                            op : "count",
                            field : "status"
                            
                        }
                    })
            .success(function(response_json, status){
                $scope.LogData = response_json.data;
                $scope.gData=transform_status($scope.LogData);
                console.log(transform_status($scope.LogData))
                //var test=($scope.LogData);
                var status=[{"label":"200","y":34473},{"label":"206","y":124},{"label":"301","y":99},{"label":"302","y":3415},{"label":"304","y":637},{"label":"403","y":12},{"label":"404","y":1010},{"label":"500","y":230}];
                var chart = new CanvasJS.Chart("chartContainer", {

                      title:{
                        text: "HTTP status count" ,
                        fontSize: 40,
                      },
                      data: [//array of dataSeries              
                        { //dataSeries object

                         /*** Change type "column" to "bar", "area", "line" or "pie"***/
                         type: "pie",
                         //showInLegend: true,
                         dataPoints : status
                        }
                     ]
                    }
                );

                    chart.render();
            
            });

    $http.get(
                    '/data/'+$scope.logset.name,
                    {
                        params:{
                            op : "count",
                            field : "os"
                            
                        }
                    })
            .success(function(response_json, status){
                $scope.LogData = response_json.data;
                $scope.gData=transform_os($scope.LogData);
                console.log(transform_os($scope.LogData))
                //var test=($scope.LogData);
                var chart = new CanvasJS.Chart("chartContainer2", {

                      title:{
                        text: "Operating System Statistics"    ,
                        fontSize: 40,
                      },
                      data: [//array of dataSeries              
                        { //dataSeries object

                         /*** Change type "column" to "bar", "area", "line" or "pie"***/
                         type: "pie",
                       
                         dataPoints : os
                        }
                     ]
                    }
                );

                    chart.render();
            
            });
            var browser= [{"label":"Avant","y":2},{"label":"Camino","y":4},{"label":"Chrome","y":98},{"label":"Firefox","y":1418},{"label":"Firefox (Minefield)","y":23},{"label":"Firefox (Shiretoko)","y":7},{"label":"Firefox Beta","y":5},{"label":"Googlebot","y":7577},{"label":"IE","y":7171},{"label":"Iron","y":1},{"label":"Maxthon","y":3},{"label":"Mobile Safari","y":95},{"label":"MyIE2","y":2},{"label":"NetNewsWire","y":205},{"label":"Opera","y":90},{"label":"Other","y":21649},{"label":"Safari","y":152},{"label":"Sleipnir","y":2},{"label":"Slurp","y":1486},{"label":"UP.Browser","y":4},{"label":"WebKit Nightly","y":6}]
            console.log(transform_browser(browser))

            var chart = new CanvasJS.Chart("chartContainer3", {

                      title:{
                        text: "Browser Statistics"    ,
                        fontSize: 40,
                      },
                      data: [//array of dataSeries              
                        { //dataSeries object

                         /*** Change type "column" to "bar", "area", "line" or "pie"***/
                         type: "pie",
                        
                         dataPoints : browser
                        }
                     ]
                    }
                );

                    chart.render();
        
    $http.get(
                    '/data/'+$scope.logset.name,
                    {
                        params:{
                            op : "count",
                            field : "request"
                            
                        }
                    })
            .success(function(response_json, status){
                $scope.hits = response_json.data;
                //console.log($scope.hits)
                getHits($scope.hits)
            });


}

function getHits(data){
    var hits=0;
  angular.forEach(data, function(value, key){
    //this.push({ label : value.status ,y: value.count })
    //this.push('y' + ':' + value)
   this.hits += parseInt(value.count);

  },hits);  
  console.log(hits)
}
function transform_status(data) {
    var t_data = [];
  angular.forEach(data, function(value, key){
    this.push({ label : value.status ,y: value.count })
    //this.push('y' + ':' + value)
   
  },t_data);
   
   return (JSON.stringify(t_data));
}

function transform_os(data) {
    var t_data = [];
  angular.forEach(data, function(value, key){
    this.push({ label : value.os ,y: value.count })
    //this.push('y' + ':' + value)
   
  },t_data);
   
   return (JSON.stringify(t_data));
}


function transform_browser(data) {
    var t_data = [];
  angular.forEach(data, function(value, key){
    this.push({ label : value.browser ,y: value.count })
    //this.push('y' + ':' + value)
   
  },t_data);
   
   return (JSON.stringify(t_data));
}


var os=[{"label":"Fedora","y":4},{"label":"Linux","y":530},{"label":"Mac OS X","y":348},{"label":"Other","y":30315},{"label":"Red Hat","y":9},{"label":"SUSE","y":3},{"label":"Ubuntu","y":139},{"label":"Windows","y":10},{"label":"Windows 2000","y":35},{"label":"Windows 7","y":24},{"label":"Windows 98","y":10},{"label":"Windows Vista","y":2121},{"label":"Windows XP","y":6357},{"label":"iOS","y":95}] ;
