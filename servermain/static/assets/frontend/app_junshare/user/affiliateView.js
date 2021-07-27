/** JavaScript on WebKit
 *
 *  affiliateView
 *
 *
 *  Created by TVA on 3/19/15.
 *  Copyright (c) 2015 storagon. All rights reserved.
 */
'use strict';
var app = angular.module('Storagon.user.affiliateView', []);

app.controller('transactionController', ['$rootScope', '$scope', 'User_ClientAPI', '$location', function ($rootScope, $scope, $sdk, $location) {
    var currentDate = new Date();
    var lastDate = new Date(currentDate.getTime() - (6 * 24 * 60 * 60 * 1000));
    currentDate.setMonth(currentDate.getMonth() + 1);
    lastDate.setMonth(lastDate.getMonth() + 1);

    var last_date = lastDate.getFullYear() + '-' + ("0" + lastDate.getMonth()).slice(-2) +
        '-' + ("0" + lastDate.getDate()).slice(-2);
    var current_date = currentDate.getFullYear() + '-' +
            ("0" + currentDate.getMonth()).slice(-2) + '-' + ("0" + currentDate.getDate()).slice(-2);

    var updateTransaction = function(fromDate, toDate, initialize){
      if(!initialize){
        switch ($('ul.tabs').find('li.active').find('a').attr('href')){
          case "#agency":
            $sdk.listTransaction(fromDate, toDate, TransactionType.agency, function (data) {
                $scope.agencyData = data;
            });
            break;
          case "#referrer":
            $sdk.listTransaction(fromDate, toDate, TransactionType.referer, function (data) {
                $scope.refererData = data;
            });
            break;
          case "#website":
            $sdk.listTransaction(fromDate, toDate, TransactionType.website, function (data) {
                $scope.websiteData = data;
            });
            break;
        }
      }
      else{
        $sdk.listTransaction(fromDate, toDate, TransactionType.agency, function (data) {
            $scope.agencyData = data;           
        });

        $sdk.listTransaction(fromDate, toDate, TransactionType.referer, function (data) {
            $scope.refererData = data;
        });

        $sdk.listTransaction(fromDate, toDate, TransactionType.website, function (data) {
            $scope.websiteData = data;
        });
      }
    };
    
    updateTransaction(lastDate.getFullYear() + '-' + ("0" + lastDate.getMonth()).slice(-2) + '-' + ("0" + lastDate.getDate()).slice(-2), currentDate.getFullYear() + '-' + ("0" + currentDate.getMonth()).slice(-2) + '-' + ("0" + currentDate.getDate()).slice(-2), true);


    $('.fromDate').each(function(){
      $(this).val(last_date);
      $(this).datepicker({
          dateFormat: 'yy-mm-dd',
          onSelect: function(dateText) {
            updateStatistic($(this).val(), $(this).parent().find('input.toDate').val(), false, $('#download-count-perpage').val());
          }
      });
    });
    $('.toDate').each(function(){
        $(this).val(current_date);
        $(this).datepicker({
            dateFormat: 'yy-mm-dd',
            onSelect: function(dateText) {
                updateStatistic($(this).parent().find('input.fromDate').val(), $(this).val(), false, $('#download-count-perpage').val());

            }
        });
    });

}]);

app.controller('manageController', ['$scope', 'User_ClientAPI', 'User_RESTFullAPI', '$location', '$cookies', '$filter', function ($scope, $sdk, $sdkREST, $location, $cookies, $filter) {
    $scope.pps = false;
    $scope.ppd = false;
    $scope.deposit_balance_type = {
        "type": "select", 
        "name": "deposit_balance_id",
        "value": "deposit_balance_id", 
        "values": [] 
    };
    $scope.username = CURRENT_USER.username;
    var account_type = parseInt($cookies['account_type']);

    switch(account_type){
      case 1:
        $scope.affMode = 'pps';
        $scope.Mode = 'pps';
        break;
      case 3:
        $scope.affMode = 'ppd';
        $scope.Mode = 'ppd';
        break;
    }
    
    var refreshBalance = function(){
      $sdk.getUserBalance(function (data) {      
        for(var i in data){
          if((account_type === 1 && data[i].fields.balance_type === 0) || (account_type === 3 && data[i].fields.balance_type === 4)){
            $scope.creditBalance = data[i].fields.amount; 
            $scope.currentBalanceID = data[i].pk;
            $scope.currentBalanceType = data[i].fields.balance_type;
            $sdkREST.getNonAvaiableTransaction(data[i].pk, function(data){
              $scope.availableBalance = $scope.creditBalance - data[0][1] - data[1][1];
            });
            return;
          }
        }      
      });
    };
    
    $sdkREST.getUserInfo(function(data){
      $scope.referrer = data.refererList;
    });
    
    $sdk.getListWebsiteAgency(function (data) {      
        $scope.affWebsiteData = data;
    });
    
    $sdkREST.getUserAccountBalance(function(data){
        for(var i in data){
          if(data[i].balance_type !== 0 && data[i].balance_type !== 4){
            $scope.deposit_balance_type.values.push({id: data[i].id, name: data[i].account_id + " - " + $filter('enumBalanceType')(data[i].balance_type)});
          }
        }
        $scope.accountBalance = data;
    });
    
    $scope.displayProg = function(e){        
        if(angular.element(e.currentTarget).attr('id') === "pps"){
          $scope.pps = true;
          $scope.ppd = false;
        }
        else{
          $scope.pps = false;
          $scope.ppd = true;
        }
    };
    
    refreshBalance();

    
    $scope.addAffWebsite = function () {
        $('#modal-add-aff-website').modal('show');
        $scope.processAddAffWebForm = function () {
            angular.element('.loader').show();            
            $scope.success = false;
            $scope.error = false;
            $scope.isProcessing = true;            
            $sdk.addWebsiteAgencyDomain($scope.website_address, function () {
                angular.element('.loader').hide();
                $scope.isProcessing=false;
                $sdk.getListWebsiteAgency(function (data) {
                    $scope.affWebsiteData = data;
                    $('#modal-add-aff-website').modal('hide');
                });                
            }, function (data) {
                angular.element('.loader').hide();
                $scope.message = data.error;
                $scope.error = true;                
                $scope.isProcessing=false;
            });
        };
    };
    
    $scope.addAccount = function () {
        $('#modal-add-account').modal('show');
        $scope.processAddAccForm = function () {
            angular.element('.loader').show();            
            $scope.success = false;
            $scope.error = false;
            $scope.isProcessing = true;            
            $sdkREST.addAccountBalance($scope.balance_type, $scope.account_id.replace(/\s+/g, '_').toLowerCase(), function (data) {
                angular.element('.loader').hide();
                $scope.isProcessing=false;
                $sdkREST.getUserAccountBalance(function (data) {
                    $scope.accountBalance = data;
                    $('#modal-add-account').modal('hide');
                });
                $scope.deposit_balance_type.values.push({id: data.id, name: $scope.account_id.replace(/\s+/g, '_').toLowerCase() + " - " + $filter('enumBalanceType')($scope.balance_type)});
            }, function (data) {
                angular.element('.loader').hide();
                $scope.message = data.detail;
                $scope.error = true;                
                $scope.isProcessing=false;
            });
        };
    };
    
    $scope.processPPDForm = function(){
      angular.element('.loader').show();            
      $scope.success = false;
      $scope.error = false;
      $scope.isProcessing = true;
      $sdk.applyToChangeAffiliateMode($scope.Mode, function () {
          angular.element('.loader').hide();          
          $scope.message = "Application was successful";
          $scope.success = true;
          $cookies['account_type'] = ($scope.Mode === "pps") ? 1 : 3;
          refreshBalance();
          $scope.isProcessing=false;
      }, function (data) {
          angular.element('.loader').hide();
          $scope.message = data.error;
          $scope.error = true;                
          $scope.isProcessing=false;
      });
    };
    
    $scope.processWithdrawForm = function(){
      angular.element('.loader').show();            
      $scope.success = false;
      $scope.error = false;
      $scope.isProcessing = true;
      var withdraw_amount = ($scope.currentBalanceType === 0) ? ($scope.withdraw_amount * 100) : ($scope.withdraw_amount * 100000);
      $sdkREST.withdrawMoney($scope.currentBalanceID, withdraw_amount, $scope.deposit_balance_id.id, function (data) {          
          angular.element('.loader').hide();
          $scope.message = "We have received your pay request of $" + data.deposit_amount / 100 + ". Please wait for us to verify. Thank you for using our service";
          $scope.success = true;
          refreshBalance();
          $scope.isProcessing=false;
      }, function (data) {
          angular.element('.loader').hide();
          $scope.message = data.error;
          $scope.error = true;                
          $scope.isProcessing=false;
      });
    };
}]);

app.controller('requestHistoryController', ['$scope', 'User_RESTFullAPI', function ($scope, $sdkREST) {
    $sdkREST.getUserApply(function (data) {      
      $scope.applyHistories = data;
    });
}]);