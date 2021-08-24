/**
 * Created by duongtd on 12/27/14.
 */

'use strict';
var app = angular.module('Storagon', ['ngRoute'
  ,'blockUI'
  ,'App_filter'
  ,'ClientAPI'
  ,'RESTFullAPI'
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

app.run(['$rootScope', '$location','$cookies','blockUI',function($rootScope, $location, $cookies, blockUI) {
  $rootScope.$on('$routeChangeStart', function() {
      //ngProgress.setParent(document.getElementById('main'));
      //ngProgress.height('4px');
      //ngProgress.color('#FB5557');
      //ngProgress.start();
      blockUI.start();
  });
  
  $rootScope.$on('$routeChangeSuccess', function(event, next, current) {
      //ngProgress.complete();
      blockUI.stop();      
      if(next.templateUrl === "/static/assets/frontend/app/filemanager_ver2/fm.html"){
        $rootScope.showFooter = false; 
        $rootScope.showPanel = false;
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