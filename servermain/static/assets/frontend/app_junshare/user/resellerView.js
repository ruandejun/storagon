/** JavaScript on WebKit
 *
 *  resellerView.js
 *
 *
 *  Created by TVA on 3/13/15.
 *  Copyright (c) 2015 storagon. All rights reserved.
 */
'use strict';
var app = angular.module('Storagon.user.resellerView', []);

app.controller('resellerManagePremiumKey', ['$scope', 'User_ClientAPI', function ($scope, $sdk) {
    $sdk.getUserBalance(function (data) {
        $scope.credits = data[0].fields.amount;
    });

	$sdk.getListPremiumKey(0, 0, function (data) {
        $scope.premiumKeyList = data;
      }
	);

    $sdk.getPlanAndPaygateInfo(function(data) {
        $scope.plans = data.planConfigDict;
    });

    $scope.selectPlan = function (planid) {
        $('#purchaseModal').foundation('reveal', 'open');
        $scope.planid = planid;
    };

    $scope.processForm = function () {
		angular.element('.loader').show();
		if($scope.submitting || !$scope.planid) return;
		$scope.submitting = true;
		$scope.message = "Your payment is being processing at the moment, please wait...";
		$scope.success = true;
		$scope.error = false;
        $sdk.buyPremiumKeyUsingCredit($scope.max_num_key, planid, function (data){
            $sdk.getListPremiumKey(0,0,
                function (data) {
                    $scope.premiumKeyList = data;
                }
            );
            angular.element('.loader').hide();
            $('#modal-signup p.modal-body').html("Process payment success! Click OK to redirect!");
            $('#modal-signup').foundation('reveal', 'open');
            //$location.path("/account");
            $('a.close').on('click', function() {
                location.reload(true);
            });
        }
        ,function (data,status,headers,config){
            angular.element('.loader').hide();
            $scope.submitting = false;
            $scope.message = "Process failed with error="+data.error+" code="+data.code;
            $scope.error = true;
            $scope.success = false;
        });
	};
}]);