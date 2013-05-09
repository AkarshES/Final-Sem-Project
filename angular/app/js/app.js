'use strict';


// Declare app level module which depends on filters, and services
var App = angular.module('App', ['$strap.directives', 'myApp.directives', 'ngUpload']);
App.config(['$routeProvider', function($routeProvider) {
    $routeProvider
        .when('/',{
            templateUrl:"static/partials/main.html"
        })
        .when('/logviewer/:table_name',{
            templateUrl:"static/partials/logViewer.html",
            controller:"LogViewerCtrl"
        })
         .when('/AddNewTable', {
            templateUrl:'static/partials/fileUpload.html',
            controller:"AddTableCtrl"
        })
        .when('/AddNewTable/:table_name', {
            templateUrl:'static/partials/fileUpload.html',
            controller:"AddTableCtrl"
        })
        .when('/dashboard',{
            templateUrl:"static/partials/dashboard.html",
            controller:"GraphCtrl"
        })
        .otherwise({
            redirectTo:'/'
        });
}]);
