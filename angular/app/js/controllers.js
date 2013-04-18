'use strict';

/* Controllers */
function MainCtrl($scope, $http){
    $http.get('../sample_data/sample-user-object.json').success(function(response_json, status){
        $scope.User = response_json;
    });
}

function LogViewerCtrl($scope, $http, $routeParams){
    $scope.table_name = $routeParams.table_name;
    $http.get('/data/'+$scope.table_name).success( function(response_json, status){
        console.log('here')
        $scope.LogData = response_json.data;
    });
}

function AddTableCtrl($scope, $http, $routeParams){
    $scope.table_name = $routeParams.table_name || null;
}
