/** JavaScript on WebKit
 *
 *  premeiumView
 *
 *
 *  Created by TVA on 3/12/15.
 *  Copyright (c) 2015 storagon. All rights reserved.
 */
'use strict';

var app = angular.module('Storagon.premium.premiumView', []);

app.controller('premiumViewController', ['$scope', 'User_ClientAPI', '$location', function($scope, $sdk, $location){
	$sdk.getPlanAndPaygateInfo(function(data){      
        var plans = [];
        for (var i in data.planIDList){
            var k = data.planIDList[i];
            data.planConfigDict[k]['planid'] = k;
            plans.push(data.planConfigDict[k]);
        }
        $scope.plans = plans;
		$scope.paygates = data.paygateConfigDict;
	});
    
	$scope.paymentMethod = function (planid){
		if (CURRENT_USER === null) {
			$location.path('/login');
		} else {
			$('#paygateModal').foundation('reveal', 'open');
			$scope.planid = planid;
            if(planid == 4) planid = 0;
			$scope.plan_storage = $scope.plans[planid].storage;
			$scope.plan_bandwidth = $scope.plans[planid].download_bandwidth;
			$scope.plan_price = $scope.plans[planid].price;
		}
	};
    
    $scope.processPaypal = function(planid){
        $('#empty-form').attr('action', '/buypremium/' + planid + '/2/');
        $('#empty-form').submit();
    };

	$scope.processForm = function () {
		angular.element('.loader').show();
		if($scope.submitting || !$scope.planid) return;
		$scope.submitting = true;
		$scope.message = "Your payment is being processing at the moment, please wait...";
		$scope.success = true;
		$scope.error = false;
		$sdk.buyPremiumDirectProcess($scope.planid,1,$scope.card_number,$scope.card_name,$scope.card_expiry,$scope.card_cvc,$scope.first_name,$scope.last_name,$scope.email,$scope.phone_number,$scope.address,$scope.country,$scope.state,$scope.city,$scope.zipcode
			,function (data){
				alert("Process payment success! Click this to redirect!");
				$location.path("/account");
				angular.element('.loader').hide();
			}
			,function (data,status,headers,config){
				$scope.submitting = false;
				$scope.message = "Process failed with error="+data.error+" code="+data.code;
				$scope.error = true;
				$scope.success = false;
				angular.element('.loader').hide();
			}
		);
	};
}]);