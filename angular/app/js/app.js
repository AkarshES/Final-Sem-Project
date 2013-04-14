'use strict';


// Declare app level module which depends on filters, and services
var App = angular.module('App', ['ngResource']);
App.config(['$routeProvider', function($routeProvider) {
    $routeProvider
        .when('/',{
            templateUrl:"partials/main.html"
        })
        .when('/logviewer/:table_name',{
            templateUrl:"partials/logViewer.html",
            controller:"LogViewerCtrl"
        })
        .when('/AddNewTable', {
            templateUrl:'partials/fileUpload.html',
            controller:"AddTableCtrl"
        })
        .when('/AddNewTable/:table_name', {
            templateUrl:'partials/fileUpload.html',
            controller:"AddTableCtrl"
        })
        .otherwise({
            redirectTo:'/'
        })
}]);
