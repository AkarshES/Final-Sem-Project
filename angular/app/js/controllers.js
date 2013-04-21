'use strict';

/* Controllers */
function MainCtrl($scope, $http){
    $http.get('/logsets').success(function(response_json, status){
        $scope.logsets = response_json.data;
    });
}

function LogViewerCtrl($scope, $http, $routeParams){
    $scope.table_name = $routeParams.table_name;
    $http.get('/data/'+$scope.table_name).success( function(response_json, status){
        $scope.LogData = response_json.data;
    });
}

function AddTableCtrl($scope, $http, $routeParams){
    //optionally set table_name
    $scope.table_name = $routeParams.table_name || null;
}
