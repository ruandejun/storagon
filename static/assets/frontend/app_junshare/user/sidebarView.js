'use strict';

var app = angular.module('Storagon.user.sidebarView', ['ngCookies']);

app.controller('menuController', ['$scope', 'User_ClientAPI', '$cookies', function ($scope, $sdk, $cookies) {
    //todo: set this to false
    $scope.showAffiliate = false;
    $scope.showReseller = false;
    $scope.showRedeem = true;
    if(typeof($cookies['account_type']) === 'undefined'){
      $sdk.getUserInfo(function (data) {
        $cookies['account_type'] = data.profile.fields.account_type;
      });
    }
    $scope.$watch(
      function() {        
          return parseInt($cookies['account_type']);        
      },
      function(newValue, oldValue) {
        if(newValue === 1 ||newValue === 3){
          $scope.showAffiliate = true;
        }
        else if(newValue === 2){
          $scope.showReseller = true;
        }
      }
    );
}]);