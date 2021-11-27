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
            templateUrl: '/static/assets/frontend/app/page/home.html',
            controller : 'homeController'
        })
        .when('/tos', {
            templateUrl: '/static/assets/frontend/app/page/tos.html'
        })
        .when('/privacy', {
            templateUrl: '/static/assets/frontend/app/page/privacy.html'
        })
        .when('/support', {
            templateUrl: '/static/assets/frontend/app/page/support.html'
        })
        .when('/copyright', {
            templateUrl: '/static/assets/frontend/app/page/copyright.html'
        })
        .when('/takedown', {
            templateUrl: '/static/assets/frontend/app/page/takedown.html'
        })
        .when('/cprnotice', {
            templateUrl: '/static/assets/frontend/app/page/copyright_notice.html'
        })
         .when('/about', {
            templateUrl: '/static/assets/frontend/app/page/aboutus.html'
        })
         .when('/devs', {
            templateUrl: '/static/assets/frontend/app/page/developer.html'
        })
}]);

app.controller('homeController', [function() {
  //alert("home");
}]);