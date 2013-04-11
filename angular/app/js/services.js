'use strict';

/* Services */
App.factory('UserInfoService', function($http) {
    return $http.get('/LogData/sample-user-info.json')
        .success(function(response_json){
            alert('test')
            return response_json;
        })
        .error(function(response_json){
            alert('test')
            return {};
        });
});
