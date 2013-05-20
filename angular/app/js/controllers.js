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

    $scope.chk=function(id){
        return(!($("#chk"+id).hasClass("checked")));
    }

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
                $scope.data = response_json.data;
                $scope.gData=transform($scope.data,"status");
                //var status=$scope.gData;
                var chart = new CanvasJS.Chart("chartContainer", {

                      title:{
                        text: "HTTP status count" ,
                        fontSize: 20,
                      },
                      
                      legend: {
                        verticalAlign: "center",  // "top" , "bottom"
                        horizontalAlign:"right"
                        },
                        
                      data: [//array of dataSeries              
                        { //dataSeries object

                         /*** Change type "column" to "bar", "area", "line" or "pie"***/
                         type: "pie",
                         showInLegend: true,
                         indexLabelFontColor:"white",
                         indexLabelLineColor:"white",
                         dataPoints : $scope.gData
                        }
                     ]
                    }
                );
                          
                chart.render();
            
            });

//For OS stats
    $http.get(
                    '/data/'+$scope.logset.name,
                    {
                        params:{
                            op : "count",
                            field : "os"
                            
                        }
                    })
            .success(function(response_json, status){
                $scope.data = response_json.data;
                $scope.gData=transform($scope.data,"os");
                //console.log(transform($scope.LogData,"os"))
                //var test=($scope.LogData);
                 
                var chart = new CanvasJS.Chart("chartContainer2", {

                      title:{
                        text: "Operating System Statistics"    ,
                        fontSize: 20,
                      },

                      legend: {
                        verticalAlign: "center",  // "top" , "bottom"
                        horizontalAlign:"left"
                        },
                      data: [//array of dataSeries              
                        { //dataSeries object

                         /*** Change type "column" to "bar", "area", "line" or "pie"***/
                         type: "pie",
                         showInLegend: true,
                         indexLabelFontColor:"white",
                         indexLabelLineColor:"white",
                         dataPoints : $scope.gData
                        }
                     ]
                    }
                );

                    chart.render();
            
            });
           
    //For Broswer stats
        
        $http.get(
                    '/data/'+$scope.logset.name,
                    {
                        params:{
                            op : "count",
                            field : "browser"
                            
                        }
                    })
            .success(function(response_json, status){
                $scope.data = response_json.data;
                $scope.gData=transform($scope.data,"browser");
                //console.log(transform($scope.LogData,"os"))
                //var test=($scope.LogData);
                 
                var chart = new CanvasJS.Chart("chartContainer3", {

                      title:{
                        text: "Broswer Statistics"    ,
                        fontSize: 20,
                      },
                       legend: {
                        horizontalAlign: "left", // "center" , "right"
                        verticalAlign: "bottom",  // "top" , "bottom"
                        fontSize: 15,
                    },
                      data: [//array of dataSeries              
                        { //dataSeries object

                         /*** Change type "column" to "bar", "area", "line" or "pie"***/
                         type: "pie",
                         showInLegend: true,
                         indexLabelFontColor:"white",
                         indexLabelLineColor:"white",                         
                         dataPoints : $scope.gData
                        }
                     ]
                    }
                );

                    chart.render();
            
            });


//Country List

   $http.get(
                    '/data/'+$scope.logset.name,
                    {
                        params:{
                            op : "count",
                            field : "request_country"
                            
                        }
                    })
            .success(function(response_json, status){
                $scope.countryCount = response_json.data;
                //console.log($scope.countryCount)
                
                }); 


//Request URL
    $http.get(
                    '/data/'+$scope.logset.name,
                    {
                        params:{
                            op : "count",
                            field : "request"
                            
                        }
                    })
            .success(function(response_json, status){
                $scope.requests = response_json.data;
                //console.log($scope.requests)
                
                }); 


//Client IP
     $http.get(
                    '/data/'+$scope.logset.name,
                    {
                        params:{
                            op : "count",
                            field : "client_ip"
                            
                        }
                    })
            .success(function(response_json, status){
                $scope.ip = response_json.data;
                $scope.visitors = $scope.ip.length;
                $scope.visits = getCount($scope.ip);
                
                
                }); 



}



function CountryCtrl  ($scope, $http, $routeParams,$filter) {
    
    

    $scope.logset = $filter('filter')($scope.logsets, {name: $routeParams.table_name})[0];
     $http.get(
                    '/data/'+$scope.logset.name,
                    {
                        params:{
                            op : "count",
                            field : "request_country"
                            
                        }
                    })
            .success(function(response_json, status){
                $scope.countryCount = response_json.data;
                //console.log($scope.countryCount)
                
                }); 



}


function RequestCtrl  ($scope, $http, $routeParams,$filter) {
    
    

    $scope.logset = $filter('filter')($scope.logsets, {name: $routeParams.table_name})[0];
     $http.get(
                    '/data/'+$scope.logset.name,
                    {
                        params:{
                            op : "count",
                            field : "request"
                            
                        }
                    })
            .success(function(response_json, status){
                $scope.requests = response_json.data;
                //console.log($scope.requests)
                
                }); 





}

function transform(data,type) {
    var t_data = [];
    
  
    //this.push({ label : value.status ,y: value.count })
    switch(type){
      case "status" :
            var sCount = getCount(data);
            angular.forEach(data, function(value, key){
            var temp = {};  
            temp.label = String(value.status);
            temp.y = ((value.count/sCount)*100).toFixed(2);
            temp.legendText = String(temp.y)+"% "+String(value.status);
            //console.log(temp)
            this.push(temp);
            
            
            },t_data);
            break;
      case "os" :
            var oCount = getCount(data);
            angular.forEach(data, function(value, key){
            var temp = {};  
            temp.label = String(value.os);
            temp.y = ((value.count/oCount)*100).toFixed(2);;
            temp.legendText = String(temp.y)+"% "+String(value.os);
            //console.log(temp);  
            this.push(temp);
            
            
            },t_data);
            break;  
      case "browser" :
            var bCount = getCount(data);
            angular.forEach(data, function(value, key){
            var temp = {};  
            temp.label = String(value.browser);
            temp.y = ((value.count/bCount)*100).toFixed(2);;
            temp.legendText = String(temp.y)+"% "+String(value.browser);
            //console.log(temp);  
            this.push(temp);
            
            
            },t_data);
            break;  
   
    }
   //console.log("Inside status",t_data);
   return ((t_data));
}


function getVisits(data){
    var hits=0;
  angular.forEach(data, function(value, key){
    //this.push({ label : value.status ,y: value.count })
    //this.push('y' + ':' + value)
   this.hits += parseInt(value.count);

  },hits);  
  console.log(hits)
}


function getCount (data) {
    var count = 0;
    angular.forEach(data, function(value, key){
        count += value.count;

    })
    return count;
}
