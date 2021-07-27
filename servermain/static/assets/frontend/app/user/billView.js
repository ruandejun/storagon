/** JavaScript on WebKit
 *
 *  billView.js
 *
 *
 *  Created by TVA on 3/12/15.
 *  Copyright (c) 2015 storagon. All rights reserved.
 */
'use strict';
var app = angular.module('Storagon.user.billView', []);

app.controller('billingController', ['$scope', 'User_ClientAPI', function ($scope, $sdk) {
    $sdk.listBill(null, null, function (data) {
        $scope.bills = data;
    });    
//    $scope.gridOptions = {
//        data: 'billData',
//        multiSelect: false,
//        columnDefs: [
//            {field: 'pk', displayName: 'ID', width: 50, cellClass: 'text-center'},
//            {field: 'fields.plan_id', displayName: 'Plan', width: 50},
//            {field: 'fields.money_charged', displayName: 'Bill Amount', width: 150, cellFilter: 'currency'},
//            {field: 'fields.created_date', displayName: 'Date', width: 200, cellFilter: 'date:\'dd/MM/yyyy\''},
//            {field: 'fields.detail._id.$oid', displayName: 'Bill_ID'}
//
//        ]
//    };
}]);