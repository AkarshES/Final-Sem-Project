'use strict';

/* Controllers */
function TableCtrl($scope){}

function LogViewerCtrl($scope, $http){
    $http.get('LogData/sample.json').success( function(response_json, status){
        $scope.LogData = response_json.data
    })
}
