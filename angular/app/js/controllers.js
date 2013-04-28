'use strict';

/* Controllers */
function MainCtrl($scope, $http){
    $http.get('/logsets').success(function(response_json, status){
        $scope.logsets = response_json.data;
    });
}

function LogViewerCtrl($scope, $http, $routeParams, $filter){
    $scope.show_time = true;

    //complicated way to get the correct logset object from the logsets array
    $scope.logset = $filter('filter')($scope.logsets, {name: $routeParams.table_name})[0];

    $scope.retrieve_logs = function(page_number){
        var from_datetime = moment($scope.from_date+" "+$scope.from_time, "DD/MM/YYYY hh:mm A").unix();
        var to_datetime = moment($scope.to_date+" "+$scope.to_time, "DD/MM/YYYY hh:mm A").unix();
        $http.get(
                '/data/'+$scope.logset.name,
                {
                    params:{
                        from:from_datetime,
                        to:to_datetime,
                        page:page_number,
                    }
                })
        .success(function(response_json, status){
            $scope.LogData = response_json.data;
            $scope.noOfPages = response_json.max_page;
        });
    };

    $scope.from_time = "12:00 AM";
    $scope.to_time = "12:00 AM";
    $scope.min_date = moment.unix($scope.logset.date_range.min_date);
    $scope.max_date = moment.unix($scope.logset.date_range.max_date);
    $scope.to_date = $scope.max_date.format("DD/MM/YYYY");
    $scope.from_date = moment($scope.max_date).subtract('days', 1).format("DD/MM/YYYY");
    $scope.retrieve_logs(0);

    //defaults for pagination directive
    $scope.noOfPages = 0;
    $scope.currentPage = 0;
    $scope.maxSize = 10;

}

function AddTableCtrl($scope, $http, $routeParams){
    //optionally set table_name
    $scope.table_name = $routeParams.table_name || null;
}
