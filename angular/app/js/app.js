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
        .otherwise({
            redirectTo:'/'
        })
}]);
