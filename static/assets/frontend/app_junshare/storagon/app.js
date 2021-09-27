/**
 * Created by duongtd on 12/27/14.
 */

'use strict';

var app = angular.module('Storagon', ['ngRoute'
  ,'App_filter'
  ,'ClientAPI'
  ,'RESTFullAPI'
  ,'angular-loading-bar'
  ,'ngAnimate'
  ,'cfp.loadingBar'
  ,'headerView' //layout
  ,'Storagon.page'
  ,'Storagon.user'
  ,'Storagon.premium'
  ,'Storagon.filemanager_ver2'
]);

var restrictControllers = ["fileManagerController"
  , "accountController"
  , "profileController"
  , "billingController"
  , "sessionController"
  , "statisticController"
  , "inboxController"
  , "reportController"
  , "exchangePointController"
  , "affiliateController"
  , "resellerManagePremiumKey"
  , "redeemController"
];

app.config(['$routeProvider', function ($routeProvider) {
    $routeProvider
        .otherwise({redirectTo: '/'});
}]);

app.run(['$rootScope','$location','$cookies', 'cfpLoadingBar',
    function($rootScope, $location, $cookies, cfpLoadingBar) {

  $rootScope.$on('$routeChangeStart', function(event, next) {
      if(next.templateUrl === "/static/assets/frontend/app_junshare/filemanager_ver2/fm.html"){
          cfpLoadingBar.start();
      }
  });
  $rootScope.$on('$routeChangeSuccess', function(event, next, current) {
      //ngProgress.complete();
      //blockUI.stop();
      if(next.templateUrl === "/static/assets/frontend/app_junshare/filemanager_ver2/fm.html"){
        $rootScope.showFooter = false; 
        $rootScope.showPanel = false;
        cfpLoadingBar.complete();
      }
      else{
        $rootScope.showFooter = true;
        if($('table#upload-progress tbody tr td').length) {          
          $rootScope.showPanel = false;
        }
        else{
          $rootScope.showPanel = true;
        }
      }   
      
      if (CURRENT_USER === null && restrictControllers.indexOf(next.controller) > -1) {
        $location.path( "/login" );
      }
      
      if (next.controller === "affiliateController" && $cookies.get('account_type') !== 1){
        $location.path("/account");
      }
      
      if ((next.controller === "signupController" || next.controller === "loginController") && CURRENT_USER !== null){
        $location.path("/account");
      }
      $(document).on('click', '#back-to-top', function(){
        $("html, body").animate({ scrollTop: 0 }, 600);
        return true;
      });
  });
  // Do the same with $routeChangeError
}]);