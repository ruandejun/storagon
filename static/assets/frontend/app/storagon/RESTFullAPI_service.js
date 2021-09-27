/**
 * Created by Hoan Pham Duy on 16/4/15.
 */

var module = angular.module('RESTFullAPI', []);

module.factory('User_RESTFullAPI', ['$http', function ($http) {
    var factory = {};

    var defaultErrorCallBack = function (method_name, data, status) {
      console.log(method_name + ": error_status=" + status + " data=" + data);
    };

    function add_auth(req) {
        var md5 = CryptoJS.algo.MD5.create();
        md5.update(SRK);
        if (req.method.match('GET|HEAD|DELETE|OPTIONS')) {
        if (req.url.indexOf('?') < 0) req.url += '?';
        else req.url += '&';
        req.url += 'rd' + Math.random().toString().substring(2) + '=';
        md5.update(req.url);
        }else{
            md5.update(req.data);
        }
        if (!req.headers)
        req.headers = {};
        req.headers[HEADER_TOKEN] = md5.finalize().toString(CryptoJS.enc.Hex);
    }

    factory.getUserInfo = function (callback, errorCallback) {
      var req = {
        method: 'GET',
        url: '/api/user/profile/show/',
        headers: {
          //'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
      };
      add_auth(req);
      $http(req)
              .success(function (data, status, headers, config) {
                callback(data);
              })
              .error(function (data, status, headers, config) {
                if (errorCallback)
                  errorCallback(data, status, headers, config);
                else
                  defaultErrorCallBack('login', data, status);
              });
    };
    
    factory.getNonAvaiableTransaction = function (balance_id, callback, errorCallback) {
      var req = {
        method: 'GET',
        url: '/api/user/accountBalance/' + balance_id + '/getNonAvaiableTransaction/',
        headers: {
          //'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
      };
      add_auth(req);
      $http(req)
              .success(function (data, status, headers, config) {
                callback(data);
              })
              .error(function (data, status, headers, config) {
                if (errorCallback)
                  errorCallback(data, status, headers, config);
                else
                  defaultErrorCallBack('getNonAvailableTransaction', data, status);
              });
    };
    
    factory.getUserApply = function (callback, errorCallback) {
      var req = {
        method: 'GET',
        url: '/api/user/userApplyList/',
        headers: {
          //'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
      };
      add_auth(req);
      $http(req)
              .success(function (data, status, headers, config) {
                callback(data);
              })
              .error(function (data, status, headers, config) {
                if (errorCallback)
                  errorCallback(data, status, headers, config);
                else
                  defaultErrorCallBack('getUserApply', data, status);
              });
    };

    factory.getUserAccountBalance = function (callback, errorCallback) {
      var req = {
        method: 'GET',
        url: '/api/user/accountBalance/',
        headers: {
//          'Content-Type': 'application/json; charset=UTF-8'
        }
      };
      add_auth(req);
      $http(req)
              .success(function (data, status, headers, config) {
                callback(data);
              })
              .error(function (data, status, headers, config) {
                if (errorCallback)
                  errorCallback(data, status, headers, config);
                else
                  defaultErrorCallBack('Get account balance', data, status);
              });
    };

    factory.getTransactionStatistic = function (from_date, to_date, callback, errorCallback) {
      var getParam = '';

      if (from_date) {
        if (getParam == '')
          getParam += '?from_date=' + from_date;
        else
          getParam += '&from_date=' + from_date;
      }

      if (to_date) {
        if (getParam == '')
          getParam += '?to_date=' + to_date;
        else
          getParam += '&to_date=' + to_date;
      }

      var req = {
        method: 'GET',
        url: '/api/statistics/aff/transactionStatistics/' + getParam
      };
      add_auth(req);
      $http(req)
              .success(function (data, status, headers, config) {
                var fromDate = new Date(from_date), toDate = new Date(to_date), transactionList = {};
                while (fromDate <= toDate) {
                  transactionList[fromDate.toISOString().slice(0, 10)] = {};
                  transactionList[fromDate.toISOString().slice(0, 10)]['bill'] = [0,0];
                  transactionList[fromDate.toISOString().slice(0, 10)]['ppd'] = [0,0];
                  transactionList[fromDate.toISOString().slice(0, 10)]['rebill'] = [0,0];
                  transactionList[fromDate.toISOString().slice(0, 10)]['refererPPD'] = [0,0];
                  transactionList[fromDate.toISOString().slice(0, 10)]['website'] = [0,0];
                  transactionList[fromDate.toISOString().slice(0, 10)]['referer'] = [0,0];
                  transactionList[fromDate.toISOString().slice(0, 10)]['downloadRaw'] = [0,0];
                  transactionList[fromDate.toISOString().slice(0, 10)]['totalOverall'] = 0;
                  fromDate.setDate(fromDate.getDate() + 1);
                }
                transactionList['Total'] = {'bill' : [0,0], 'ppd' : [0,0], 'rebill' : [0,0], 'refererPPD' : [0,0], 'website' : [0,0], 'referer' : [0,0], 'downloadRaw' : [0,0], 'totalOverall' : 0};
                for (var i in data){
                  for (var j in data[i]){
                    if(i === "downloadRaw"){
                      var date = data[i][j]['_id']['year'] + "-" + ("0" + data[i][j]['_id']['month']).slice(-2) + "-" + ("0" + data[i][j]['_id']['day']).slice(-2);
                    }
                    else{
                      var date = data[i][j][0];
                    }
                    if(transactionList.hasOwnProperty(date)){
                      transactionList[date][i][0] = (Array.isArray(data[i][j]) && i !== "ppd") ? data[i][j][1] : data[i][j]['count'];
                      transactionList[date][i][1] = (Array.isArray(data[i][j])) ? data[i][j][2] : transactionList[date][i][1];
                      transactionList['Total'][i][0] = (Array.isArray(data[i][j])) ? (transactionList['Total'][i][0] +data[i][j][1]) : (transactionList['Total'][i][0] +data[i][j]['count']);
                      transactionList['Total'][i][1] = (Array.isArray(data[i][j])) ? (transactionList['Total'][i][1] +data[i][j][2]) : transactionList['Total'][i][1];
                      if(i === "ppd" || i === "refererPPD"){
                        transactionList[date]['totalOverall'] = (Array.isArray(data[i][j])) ? (transactionList[date]['totalOverall'] +(Math.round((transactionList[date][i][1] / 100000)*1000)/1000)) : transactionList[date]['totalOverall'];                        
                      }
                      else{
                        transactionList[date]['totalOverall'] = (Array.isArray(data[i][j])) ? (transactionList[date]['totalOverall'] +(Math.round((transactionList[date][i][1] / 100)*1000)/1000)) : transactionList[date]['totalOverall'];
                      }
                      //if(typeof(data[i][j][2]) !== 'undefined'){
                      //  transactionList['Total']['totalOverall'] = Math.round((transactionList['Total']['totalOverall'] + transactionList[date]['totalOverall']) * 1000)/1000;
                      //}
                    }
                  }
                }
                for(date in transactionList){
                    if(transactionList.hasOwnProperty(date)) {
                        if (date != 'Total')
                            transactionList['Total']['totalOverall'] += transactionList[date]['totalOverall'];
                    }
                }
                callback(transactionList);
              })
              .error(function (data, status, headers, config) {
                if (errorCallback)
                  errorCallback(data, status, headers, config);
                else
                  defaultErrorCallBack('getTransactionStatistic', data, status)
              });
    };
    
    factory.getListSession = function(type, status, from_date, to_date, pageNum, perPage, kwagrs, callback, errorCallback) {
        var getParam='?type='+type;

        if(status){
            getParam+='&status='+status;
        }

        if(from_date != null){
            getParam+='&from_date='+from_date;
        }
        else{
            getParam+='&from_date=2014-01-01';
        }

        if(to_date != null){
            getParam+='&to_date='+to_date;
        }

        if(kwagrs!=null){
            if (kwagrs.fid){
                getParam += '&fid=' + kwagrs.fid;
            }

            if (kwagrs.oid){
                getParam += '&oid=' + kwagrs.oid;
            }
        }
        
        if(pageNum!=null && perPage!=0){
          getParam += '&page=' + pageNum;
        }
        
        if(perPage!=null && perPage!=0){
          getParam += '&page_size=' + perPage;
        }
        
        var req = {
            method: 'GET',
            url: '/api/mongo/session/'+getParam
        };

        add_auth(req);
        $http(req)
            .success(function(data, status, headers, config) {
                callback(data);
            })
            .error(function(data, status, headers, config) {
                if(errorCallback)errorCallback(data,status,headers,config);
                else defaultErrorCallBack('getUserStorage',data,status)
            });
    };

    factory.addAccountBalance = function (balance_type, account_id, callback, errorCallback) {
      var req = {
        method: 'POST',
        url: '/api/user/accountBalance/',
        data: {balance_type: balance_type, account_id: account_id},
        headers: {
//          'Content-Type': 'application/json; charset=UTF-8'
        }
      };
      add_auth(req);
      $http(req)
              .success(function (data, status, headers, config) {
                callback(data);
              })
              .error(function (data, status, headers, config) {
                if (errorCallback)
                  errorCallback(data, status, headers, config);
                else
                  defaultErrorCallBack('Add account balance', data, status);
              });
    };
    
    factory.withdrawMoney = function (withdraw_balance_id, withdraw_amount, deposit_balance_id, callback, errorCallback) {
      var req = {
        method: 'POST',
        url: '/api/user/userApplyView/requestPay/',
        data: {withdraw_balance_id: withdraw_balance_id, withdraw_amount: withdraw_amount, deposit_balance_id: deposit_balance_id},
        headers: {
//          'Content-Type': 'application/json; charset=UTF-8'
        }
      };
      add_auth(req);
      $http(req)
              .success(function (data, status, headers, config) {
                callback(data);
              })
              .error(function (data, status, headers, config) {
                if (errorCallback)
                  errorCallback(data, status, headers, config);
                else
                  defaultErrorCallBack('Add account balance', data, status);
              });
    };

    factory.invokeDesktopClient = function (invoke_type, invoke_data, callback, errorCallback) {
      var req = {
        method: 'POST',
        url: '/api/user/auth/invokeDesktopClient/',
        data: {invoke_type: invoke_type, invoke_data: invoke_data}
      };
      add_auth(req);
      $http(req)
              .success(function (data, status, headers, config) {
                callback(data);
              })
              .error(function (data, status, headers, config) {
                if (errorCallback)
                  errorCallback(data, status, headers, config);
                else
                  defaultErrorCallBack(req.method+':'+req.url, data, status);
              });
    };


    return factory;
  }]);