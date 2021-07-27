/** JavaScript on WebKit
 *
 *  exchangePointView
 *
 *
 *  Created by TVA on 3/12/15.
 *  Copyright (c) 2015 storagon. All rights reserved.
 */
'use strict';
var app = angular.module('Storagon.user.exchangePointView', []);

app.controller('exchangePointController', ['$scope', 'User_ClientAPI', function ($scope, $sdk)
{
    $sdk.getUserBalance(function (data) {
        $scope.pointBalance = data[1].fields.amount;
    });

    $sdk.getExchangePointRateInfo(function (data) {
        $scope.packs = data.packs;
    });

    $scope.exchange = function(name)
    {
        $sdk.exchangePoint(name, function (data) {
            $('#modal-exchange p.modal-body').html(data);
            $('#modal-exchange').foundation('reveal', 'open');
        });
        $('a.close').on('click', function() {
            $('#modal-exchange').foundation('reveal', 'close');
        });
    }
}]);