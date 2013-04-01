'use strict';


// Declare app level module which depends on filters, and services
var App = angular.module('App', ['ngResource']);
App.config(['$routeProvider', function($routeProvider) {
    $routeProvider
        .when('/',{
            templateUrl:"partials/tableView.html",
            controller:"TableCtrl"
        })
        .when('/logviewer',{
            templateUrl:"partials/logViewer.html",
            controller:"LogViewerCtrl"
        })
        .otherwise({
            redirectTo:'/'
        })
}]);
