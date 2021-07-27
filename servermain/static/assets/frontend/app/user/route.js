/** JavaScript on WebKit
 *
 *  route.js
 *
 *
 *  Created by TVA on 3/12/15.
 *  Copyright (c) 2015 storagon. All rights reserved.
 */
'use strict';

var app = angular.module('Storagon.user', ['ngRoute'
    ,'percentage'
	,'Storagon.user.authenticateView'
	,'Storagon.user.accountView'
	,'Storagon.user.billView'
	,'Storagon.user.sessionView'
	,'Storagon.user.exchangePointView'
    ,'Storagon.user.affiliateView'
    ,'Storagon.user.resellerView'
    ,'Storagon.user.redeemView'
    ,'Storagon.user.sidebarView'
]);

app.config(['$routeProvider', function ($routeProvider) {
    $routeProvider
        .when('/signup', {
            templateUrl: '/static/assets/frontend/app/user/signup.html',
            controller : 'signupController',
            bodyClass: 'login-page',
            headerClass: 'login'
        })
        .when('/login', {
            templateUrl: '/static/assets/frontend/app/user/login.html',
            controller : 'loginController',
            bodyClass: 'login-page',
            headerClass: 'login'
        })
        .when('/logout', {
            templateUrl: '/static/assets/frontend/app/page/home.html',
            controller : 'logoutController'
        })
        .when('/account', {
            templateUrl: '/static/assets/frontend/app/user/account.html',
            controller: 'accountController'
        })
        .when('/profile', {
            templateUrl: '/static/assets/frontend/app/user/profile.html',
            controller: 'profileController'
        })
        .when('/billing', {
            templateUrl: '/static/assets/frontend/app/user/billing.html',
            controller: 'billingController'
        })
        .when('/statistic', {
            templateUrl: '/static/assets/frontend/app/user/statistic.html',
            controller: 'statisticController'
        })
        .when('/inbox', {
            templateUrl: '/static/assets/frontend/app/user/inbox.html',
            controller: 'inboxController'
        })
        .when('/report', {
            templateUrl: '/static/assets/frontend/app/user/report.html',
            controller: 'reportController'
        })
        .when('/exchange', {
            templateUrl: '/static/assets/frontend/app/user/exchange.html',
            controller: 'exchangePointController'
        })
        .when('/transaction', {
            templateUrl: '/static/assets/frontend/app/user/transaction.html',
            controller: 'transactionController'
        })
        .when('/manage', {
            templateUrl: '/static/assets/frontend/app/user/manage.html',
            controller: 'manageController'
        })
        .when('/request-history', {
            templateUrl: '/static/assets/frontend/app/user/requestHistory.html',
            controller: 'requestHistoryController'
        })
        .when('/reseller', {
            templateUrl: '/static/assets/frontend/app/user/reseller.html',
            controller: 'resellerManagePremiumKey'
        })
        .when('/redeem', {
            templateUrl: '/static/assets/frontend/app/user/redeem.html',
            controller: 'redeemController'
        })
    ;
}]);

//app.run(function($rootScope, ngProgress) {
//  $rootScope.$on('$routeChangeStart', function() {
//      ngProgress.height('4px');
//      ngProgress.color('#FB5557');
//      ngProgress.start();
//  });
//
//  $rootScope.$on('$routeChangeSuccess', function() {
//      ngProgress.complete();
//  });
//  // Do the same with $routeChangeError
//});