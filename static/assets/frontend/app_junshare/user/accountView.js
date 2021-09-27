/** JavaScript on WebKit
 *
 *  accountView.js
 *
 *
 *  Created by TVA on 3/12/15.
 *  Copyright (c) 2015 storagon. All rights reserved.
 */
'use strict';
var app = angular.module('Storagon.user.accountView', ['ngCookies']);

app.controller('accountController', ['$scope', '$location', 'User_ClientAPI', '$cookies', function ($scope, $location, $sdk, $cookies) {

    $scope.resendActivationEmail = function (){
        angular.element('.loader').show();
		$scope.isProcessingResendActivationEmail=true;
        $sdk.resendActivationEmail(function(){        
            angular.element('.loader').hide();
            $('#modal-activate-email div.modal-body').html("Successful! Please check your email to confirm");
            $('#modal-activate-email').modal('show');
		}, function(){//error callback
			alert("Error Sending email");
			angular.element('.loader').hide();
            $('#modal-activate-email div.modal-body').html("Failed! Please check your email again!");
            $('#modal-activate-email').modal('show');
			$scope.isProcessingResendActivationEmail=false;
		});
        $('a.close').on('click', function() {
            $('#modal-activate-email').modal('hide');
        });
    };

    $scope.applyAffiliate = function () {
      $('#modal-apply-affiliate').modal('show');
    };

    $scope.processForm = function() {
        angular.element('.loader').show();
        $scope.success = false;
        $scope.error = false;
        $scope.isProcessing = true;
        $sdk.applyToBecomeAffiliate('', function () {            
            angular.element('.loader').hide();
            $scope.message = "You have applied to become affiliate successfully, please wait for us to processing your application";
            $scope.success = true;
            $scope.error = false;
            $scope.isProcessing = false;
            //$location.path('/account');
        }, function (data) {
            angular.element('.loader').hide();
            $scope.message = data.error;
            $scope.success = false;
            $scope.error = true;
            $scope.isProcessing = false;
        });
    };

    var init = function () {
        // get data from the server to populate the view

        $sdk.getUserInfo(function(data) {
            if(typeof($cookies['account_type']) === 'undefined'){
              $cookies['account_type'] = data.profile.fields.account_type;
            }
            var user_plan_id = data.profile.fields.plan_id;
            $scope.username = data.username;
            $scope.email = data.profile.fields.email;
            $scope.accountType = AccountTypeFilter[data.profile.fields.account_type];

            if (data.profile.fields.plan_id > 0 ) {
                $scope.premiumStatus = "Premium";
            } else {
                $scope.premiumStatus = "User";
            }
            $scope.accountStatus = AccountStatusFilter[data.profile.fields.account_status];
            $scope.planExpired = data.profile.fields.plan_expired;
            $scope.storageSpace = data.profile.fields.storage_space;
            $sdk.getPlanAndPaygateInfo(function (data) {
              $scope.monthly_bandwidth = data.planConfigDict[user_plan_id].download_bandwidth;
              $scope.download_speed = data.planConfigDict[user_plan_id].download_speed;
              $scope.download_wait = (user_plan_id === 0) ? '30 seconds' : 'No wait';
              $scope.access_premium_files = (user_plan_id === 0) ? 'No' : 'Yes';
              $scope.access_premium_tools = (user_plan_id === 0) ? 'No' : 'Yes';
            });
        });

        $sdk.getUserStorage(function(data){
        $scope.storageUsed = data.storage_used;
        $scope.bandwidthUsed = data.download_bandwidth;
        $scope.folder = data.folder_count;
        $scope.file = data.file_count;
    });

        $sdk.getUserBalance(function (data) {
        $scope.pointBalance = data[1].fields.amount;
    });

    };
    init();

}]);

app.controller('profileController', ['$scope', 'User_ClientAPI', function ($scope, $sdk) {

    $sdk.getUserInfo(function (data) {
        var pf=data.profile.fields;
        $scope.full_name = pf.full_name;
        $scope.address = pf.address;
        $scope.email = pf.email;
    });

    $scope.processForm = function () {
        angular.element('.loader').show();
        if($scope.password !== $scope.password2){
            angular.element('.loader').hide();
            $scope.message = "Inputed password doesn't match!";
            $scope.success = false;
            $scope.error = true;
            return;
        }
        $scope.success = false;
        $scope.error = false;
        $sdk.updateUserInfo($scope.full_name,$scope.email,$scope.address,$scope.old_password,$scope.password, function(){
            angular.element('.loader').hide();
            $scope.message = 'Update Info Sucesss';
            $scope.success = true;
        },function(){
            angular.element('.loader').hide();
            $scope.message = 'Failed to Update Info';
            $scope.error = true;
        });
    };

}]);