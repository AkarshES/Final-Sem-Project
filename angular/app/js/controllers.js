'use strict';

/* Controllers */
function MainCtrl($scope, $http){
    $http.get('../sample_data/sample-user-object.json').success(function(response_json, status){
        $scope.User = response_json;
    });
}

function LogViewerCtrl($scope, $http, $routeParams){
    $scope.table_name = $routeParams.table_name;
    $http.get('../sample_data/sample-data.json').success( function(response_json, status){
        $scope.LogData = response_json.data;
    });
}

function TableAddCtrl($scope, $http){
    $scope.create_table = function(){
    }
}
