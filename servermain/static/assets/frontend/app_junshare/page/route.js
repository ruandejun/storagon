/** JavaScript on WebKit
 *
 *  route
 *
 *
 *  Created by TVA on 3/12/15.
 *  Copyright (c) 2015 storagon. All rights reserved.
 */
'use strict';

var app = angular.module('Storagon.page',['ngRoute']);

app.config(['$routeProvider', function ($routeProvider) {
    $routeProvider
        .when('/', {
            templateUrl: '/static/assets/frontend/app_junshare/page/home.html',
            controller : 'homeController'
        })
        .when('/tos', {
            templateUrl: '/static/assets/frontend/app_junshare/page/tos.html'
        })
        .when('/privacy', {
            templateUrl: '/static/assets/frontend/app_junshare/page/privacy.html'
        })
        .when('/support', {
            templateUrl: '/static/assets/frontend/app_junshare/page/support.html'
        })
        .when('/copyright', {
            templateUrl: '/static/assets/frontend/app_junshare/page/copyright.html'
        })
        .when('/takedown', {
            templateUrl: '/static/assets/frontend/app_junshare/page/takedown.html'
        })
        .when('/cprnotice', {
            templateUrl: '/static/assets/frontend/app_junshare/page/copyright_notice.html'
        })
         .when('/about', {
            templateUrl: '/static/assets/frontend/app_junshare/page/aboutus.html'
        })
         .when('/devs', {
            templateUrl: '/static/assets/frontend/app_junshare/page/developer.html'
        })
}]);

app.controller('homeController', [function() {
  //alert("home");
}]);