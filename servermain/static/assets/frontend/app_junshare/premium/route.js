/** JavaScript on WebKit
 *
 *  premium_route.js
 *
 *
 *  Created by TVA on 3/12/15.
 *  Copyright (c) 2015 storagon. All rights reserved.
 */

'use strict';

var app = angular.module('Storagon.premium', ['ngRoute'
	,'Storagon.premium.paymentView'
	,'Storagon.premium.premiumView'
]);

app.config(['$routeProvider', function($routeProvider){
	$routeProvider
		.when('/premium', {
			templateUrl:'/static/assets/frontend/app_junshare/premium/premium.html',
			controller:'premiumViewController'
		})
		.when('/pmform/:planid', {
			templateUrl:'/static/assets/frontend/app_junshare/premium/payment_form.html',
			controller:'paymentFormController'
		});
}]);