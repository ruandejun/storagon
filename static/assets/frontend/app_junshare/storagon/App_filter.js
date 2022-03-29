/** JavaScript on WebKit
 *
 *  App_filter
 *
 *
 *  Created by TVA on 3/12/15.
 *  Copyright (c) 2015 storagon. All rights reserved.
 */
'use strict';
var app = angular.module('App_filter', []);

app.filter('filesize', function () {
    var units = [
        'bytes',
        'KB',
        'MB',
        'GB',
        'TB',
        'PB'
    ];
    return function( bytes, type ) {
        if ( isNaN( parseFloat( bytes )) || ! isFinite( bytes ) ) {
          return '?';
        }
        if(type !== 1){
          if ( bytes === 0 ){
            return 'Unlimited';
          }
        }
        var unit = 0;
        while ( bytes >= 1024 ) {
            bytes /= 1024;
            unit ++;
        }
        return bytes.toFixed( 2 ) + ' ' + units[ unit ];
    };
});

app.filter('enumSessionStatus', function () {
    return function (input) {
        return SessionStatusFilter[input];
    };
});

app.filter('enumAccountType', function () {
    return function (input) {
        return AccountTypeFilter[input];
    };
});

app.filter('enumBalanceType', function () {
    return function (input) {
        return BalanceTypeFilter[input];
    };
});

app.filter('enumApplyType', function () {
    return function (input) {
        return ApplyTypeFilter[input];
    };
});

app.filter('enumApplyStatus', function () {
    return function (input) {
        return ApplyStatusFilter[input];
    };
});

app.filter('amount', function () {
    return function (input, balanceType) {
      switch(balanceType){
        case 0:
        case "pps":
          return Math.round((input / 100) *1000)/1000;
          break;
        case 1:
          return input;
          break;
        case 4:
        case "ppd":
          return Math.round((input / 100000) *1000)/1000;
          break;
        default:
          return '';
          break;
      }        
    };
});


app.filter('duration', function(){
	var units = ['SEC', 'HOUR', 'DAY', 'WEEK', 'MONTH', 'YEAR'];
	return function(seconds){
		if (isNaN(parseFloat(seconds)) || !isFinite(seconds)){
			return '?';
		}
		var unit = 0;
		if (seconds >= 3600){
			seconds /= 3600;
			unit += 1;
		}
		//day
		if (seconds >= 24){
			seconds /= 24;
			unit += 1;
		}
		//weeks
		if (seconds >= 7){
			seconds /= 7;
			unit += 1;
		}
		//months
		if (seconds >= 4){
			seconds /= 4;
			unit += 1;
		}
		//years
		if (seconds >= 12){
			seconds /= 12;
			unit += 1;
		}
		return seconds.toFixed(0) + ' ' + units[unit];
	};
});