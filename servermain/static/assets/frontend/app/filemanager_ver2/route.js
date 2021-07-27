/** JavaScript on WebKit
 *
 * fmView
 *
 *
 *  Created by TVA on 3/12/15.
 *  Copyright (c) 2015 storagon. All rights reserved.
 */

'use strict';

var app = angular.module('Storagon.filemanager_ver2',['ngRoute']);

app.config(['$routeProvider', function ($routeProvider) {
  $routeProvider
    .when('/fm2', {
        templateUrl: '/static/assets/frontend/app/filemanager_ver2/fm.html',
        controller : 'fileManagerController'
    });
}]);

app.controller('fileManagerController', ['$scope', function($scope) {
  angular.element('#fileTreeDemo_1').gsFileManager();
}]);