/** JavaScript on WebKit
 *
 *  headerView
 *
 *
 *  Created by TVA on 3/19/15.
 *  Copyright (c) 2015 storagon. All rights reserved.
 */
'use strict';
var app = angular.module('headerView', []);

app.controller('headerController', ['$scope', function ($scope) {
    $scope.$watch(
      function() {
        if (CURRENT_USER !== null) {
            return true;
        }else{
            return false;
        }
      },
      function(newValue, oldValue) {
        $scope.showUserMenu = newValue;
      }
    );
}]);