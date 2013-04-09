'use strict';

/* Controllers */
function MainCtrl($scope, $http){
    $http.get('LogData/sample-user-object.json').success(function(response_json, status){
        $scope.User = response_json;
    });
}

function LogViewerCtrl($scope, $http){
    $http.get('LogData/sample.json').success( function(response_json, status){
        $scope.LogData = response_json.data
    })
}
