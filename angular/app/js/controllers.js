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
}
