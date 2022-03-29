/** JavaScript on WebKit
 *
 *  exchangePointView
 *
 *
 *  Created by Hoan Pham on 3/20/15.
 *  Copyright (c) 2015 storagon. All rights reserved.
 */
'use strict';
var app = angular.module('Storagon.user.redeemView', []);

app.controller('redeemController', ['$scope', '$location', 'User_ClientAPI', function ($scope, $location, $sdk)
{
    $scope.code_type = {
        "type": "select", 
        "name": "code_type",
        "value": "Premium", 
        "values": [{id:1, name:"Premium"}] 
    };
    $scope.processForm = function(){
      angular.element('.loader').show();
      $scope.isProcessing=true;
      $sdk.exchangePremiumKey($scope.redeem_code, function(){
        angular.element('.loader').hide();
        $location.path('/account');
      }, function(){//error callback
        angular.element('.loader').hide();
        $('#modal-redeem p.modal-body').html("Redeem code or code type is not valid");
        $('#modal-redeem').foundation('reveal', 'open');
        $scope.isProcessing=false;
      });
      $('a.close').on('click', function() {
          $('#modal-redeem').foundation('reveal', 'close');
      });
    };
}]);