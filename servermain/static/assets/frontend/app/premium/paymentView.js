/**
 * Created by TVA on 3/10/15.
 */
'use strict';

var app = angular.module('Storagon.premium.paymentView',[]);
//
app.controller('paymentFormController', ['$scope', 'User_ClientAPI', '$routeParams', '$location', function ($scope, $sdk, $routeParams, $location) {
    console.log("PlanID="+$routeParams.planid);
    $scope.submitting = false;
	//console.log($location.search());

    $scope.processForm = function () {
        if($scope.submitting) return;
        $scope.submitting = true;
        $scope.message = "Your payment is being processing at the moment, please wait...";
        $scope.success = true;
        $scope.error = false;
        $sdk.buyPremiumDirectProcess($routeParams.planid,1,$scope.card_number,$scope.card_name,$scope.card_expiry,$scope.card_cvc,$scope.first_name,$scope.last_name,$scope.email,$scope.phone_number,$scope.address,$scope.country,$scope.state,$scope.city,$scope.zipcode
            ,function (data){
                alert("Process payment success! Click this to redirect!");
                $location.path("/account");
            }
            ,function (data,status,headers,config){
                $scope.submitting = false;
                $scope.message = "Process failed with error="+data.error+" code="+data.code;
                $scope.error = true;
                $scope.success = false;
            }
        );
    };
}]);