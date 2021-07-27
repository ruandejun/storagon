/** JavaScript on WebKit
 *
 *  authenticateView.js
 *
 *
 *  Created by TVA on 3/12/15.
 *  Copyright (c) 2015 storagon. All rights reserved.
 */
'use strict';
var app = angular.module('Storagon.user.authenticateView', ['vcRecaptcha']);

app.controller('signupController', ['$scope', 'User_ClientAPI', 'User_RESTFullAPI', '$location', 'vcRecaptchaService', function($scope, $sdk, $sdkREST, $location, vcRecaptchaService){
	$scope.response = null;
    $scope.widgetId = null;
    $scope.setResponse = function (response) {
      console.info('Response available');
      $scope.response = response;
    };
    $scope.setWidgetId = function (widgetId) {
      console.info('Created widget ID: %s', widgetId);
      $scope.widgetId = widgetId;
    };
    $scope.submitSignupForm = function(){ 
        var valid;
        console.log('sending the captcha response to the server', $scope.response);
		var getParam = $location.search();
		var referer = getParam.referer;
		if(referer === true) {
          referer = '';
        }    
        angular.element('.loader').show();
		$sdk.signup($scope.username, $scope.password, $scope.email, vcRecaptchaService.getResponse($scope.widgetId), referer, function(){
			angular.element('.loader').hide();
            valid = true;
            $scope.isProcessing = false;
            $sdkREST.getUserInfo(function(data){
              CURRENT_USER = {
                username: data.username,
                id: data.id,
                email: data.email,
                is_active: data.is_active,
                is_staff: data.is_staff,
                last_login: data.last_login,
                first_name: data.first_name,
                last_name: data.last_name,
                referrer_list: data.refererList
              };
              $location.path('/account');
            }); 
		}, function(data, status, headers, config){//error callback
			angular.element('.loader').hide();
            console.log('callback error');
            console.log(data);
			$('#modal-signup .modal-body').html("Signup Error: " + data['error']);
            $('#modal-signup').modal('show');
            valid = false;
			$scope.isProcessing = false;
		});
        if (!valid) {
          // In case of a failed validation you need to reload the captcha
          // because each response can be checked just once
          vcRecaptchaService.reload($scope.widgetId);
        }
		$('a.close').on('click', function() {
            $('#modal-signup').modal('close');
        });
	};
}]);

app.controller('loginController', ['$scope', '$location', '$route', 'User_ClientAPI', 'User_RESTFullAPI', function($scope, $location, $route, $sdk, $sdkREST){
	$scope.showLogin = true;
    $scope.showReset = false;
    angular.element('a.reset-pass-link').click(function(){
      $scope.$apply(function() {
        if(!angular.element('form#login_form').closest('div').hasClass('ng-hide')){
          $scope.showLogin = false;
          $scope.showReset = true;
        }
        else {
          $scope.showLogin = true;
          $scope.showReset = false;
        }
      });
    });
    $scope.processLoginForm = function(){
		angular.element('.loader').show();
		$sdk.login($scope.username, $scope.password, function(data){
          $sdkREST.getUserInfo(function(data){
            CURRENT_USER = {
              username: data.username,
              id: data.id,
              email: data.email,
              is_active: data.is_active,
              is_staff: data.is_staff,
              last_login: data.last_login,
              first_name: data.first_name,
              last_name: data.last_name,
              referrer_list: data.refererList
            };
            $location.path('/fm2');
          });                        
		}, function(){//error callback			
			angular.element('.loader').hide();
			$('#modal-login .modal-body').html("Username or password is not valid");
            $('#modal-login').modal('show');
		});
	};
    $scope.processResetForm = function(){
		angular.element('.loader').show();
		$sdk.resetPassword($scope.email, function(data){
          angular.element('.loader').hide();
          $('#modal-login .modal-body').html("Reset password link sent successfully. Please check your email");
          $('#modal-login').modal('show');
		}, function(data) {//error callback			
          angular.element('.loader').hide();
          $('#modal-login .modal-body').html(data.error);
          $('#modal-login').modal('show');
		});
	};
}]);

app.controller('logoutController', ['$scope', '$location', 'User_ClientAPI', function($scope, $location, $sdk){
	$sdk.logout(function(){
      CURRENT_USER = null;
      $location.path('/');
	});
}]);

app.directive('pwCheck', [function () {
  return {
    require: 'ngModel',
    link: function (scope, elem, attrs, ctrl) {
      var firstPassword = '#' + attrs.pwCheck;
      elem.add(firstPassword).on('keyup', function () {
        scope.$apply(function () {
          var v = elem.val() === $(firstPassword).val();
          ctrl.$setValidity('pwmatch', v);
        });
      });
    }
  };
}]);