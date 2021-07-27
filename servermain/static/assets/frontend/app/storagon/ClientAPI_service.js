/**
 * Created by TVA on 1/3/15.
 */

var module = angular.module('ClientAPI', []);

module.factory('User_ClientAPI',['$http', function($http) {
    var factory = {};

    var defaultErrorCallBack = function(method_name, data, status) {
        console.log(method_name+": error_status="+status+" data="+data);
    };

    function add_auth(req){
        var md5 = CryptoJS.algo.MD5.create();
        md5.update(SRK);
        if(req.method=='GET'){
            if(req.url.indexOf('?')<0)req.url+='?';
            else req.url+='&';
            req.url+='rd'+Math.random().toString().substring(2)+'=';
            md5.update(req.url);
        }
        else if(req.method=='POST')md5.update(req.data);
        if(!req.headers)req.headers={};
        req.headers[HEADER_TOKEN]=md5.finalize().toString(CryptoJS.enc.Hex);
    }

    factory.resetPassword = function(email,callback,errorCallback){
        var req = {
            method: 'POST',
            url: '/clapi/user/sendResetPasswordEmail/',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            },
            data: $.param({
                email:email
            })
        };

        add_auth(req);

        $http(req)
            .success(function(data, status, headers, config) {
                callback(data);
            })
            .error(function(data, status, headers, config) {
                if(errorCallback) errorCallback(data,status,headers,config);
                else defaultErrorCallBack('login',data,status)
            })
        ;
    };
    
    factory.login = function(username,password,callback,errorCallback){
        var req = {
            method: 'POST',
            url: '/clapi/user/login/',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            },
            data: $.param({
                username:username,
                password:password
            })
        };

        add_auth(req);

        $http(req)
            .success(function(data, status, headers, config) {
                callback(data);
            })
            .error(function(data, status, headers, config) {
                if(errorCallback) errorCallback(data,status,headers,config);
                else defaultErrorCallBack('login',data,status)
            })
        ;
    };

    factory.logout = function(callback,errorCallback){
        var req = {
            method: 'POST',
            url: '/clapi/user/logout/',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            },
            data: $.param({
            })
        };

        add_auth(req);

        $http(req)
            .success(function(data, status, headers, config) {
                callback(data);
            })
            .error(function(data, status, headers, config) {
                if(errorCallback)errorCallback(data,status,headers,config);
                else defaultErrorCallBack('logout',data,status)
            })
        ;
    };

    factory.signup = function(username,password,email,captcha,referer, callback,errorCallback){
        var req = {
            method: 'POST',
            url: '/clapi/user/signup/',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            },
            data: $.param({
                username:username,
                password:password,
                email:email,
                'g-recaptcha-response':captcha,
                referer: referer
            })
        };

        add_auth(req);

        $http(req)
            .success(function(data, status, headers, config) {
                callback(data);
            })
            .error(function(data, status, headers, config) {
                if(errorCallback)errorCallback(data,status,headers,config);
                else defaultErrorCallBack('login',data,status)
            })
        ;
    };

    factory.getUserInfo = function(callback,errorCallback) {
        var req = {
            method: 'GET',
            url: '/clapi/user/getUserInfo/'
        };

        add_auth(req);

        $http(req)
            .success(function(data, status, headers, config) {
                var profiles= jQuery.parseJSON(data.profiles);
                data['profile']=profiles[0];
                callback(data);
            })
            .error(function(data, status, headers, config) {
                if(errorCallback)errorCallback(data,status,headers,config);
                else defaultErrorCallBack('getUserInfo',data,status)
            });

    };


    factory.getUserBalance = function(callback,errorCallback) {
        var req = {
            method: 'GET',
            url: '/clapi/user/getUserBalance/'
        };

        add_auth(req);

        $http(req)
            .success(function(data, status, headers, config) {
                callback(data);
            })
            .error(function(data, status, headers, config) {
                if(errorCallback)errorCallback(data,status,headers,config);
                else defaultErrorCallBack('getUserInfo',data,status)
            });

    };


    factory.updateUserInfo = function(fullname,email,address,old_password,password,callback,errorCallback){

        var req = {
            method: 'POST',
            url: '/clapi/user/updateUserInfo/',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            },
            data: $.param({
                full_name:fullname,
                email:email,
                address:address,
                old_password:old_password,
                password:password
            })
        }

        add_auth(req);

        $http(req)
            .success(function(data, status, headers, config) {
                callback(data);
            })
            .error(function(data, status, headers, config) {
                if(errorCallback)errorCallback(data,status,headers,config);
                else defaultErrorCallBack('updateUserInfo',data,status)
            })
        ;
    };

    //userstats API
    factory.getUserStorage = function(callback,errorCallback) {
        var req = {
            method: 'GET',
            url: '/clapi/userstats/getUserStorage/'
        }
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

    factory.getPlanAndPaygateInfo = function(callback,errorCallback) {
        var req = {
            method: 'GET',
            url: '/clapi/userstats/getPlanAndPaygateInfo/'
        }
        add_auth(req);
        $http(req)
            .success(function(data, status, headers, config) {
                callback(data);
            })
            .error(function(data, status, headers, config) {
                if(errorCallback)errorCallback(data,status,headers,config);
                else defaultErrorCallBack('getPlanAndPaygateInfo',data,status)
            });
    };

    factory.getExchangePointRateInfo = function(callback,errorCallback) {
        var req = {
            method: 'GET',
            url: '/clapi/userstats/getExchangePointRateInfo/'
        }
        add_auth(req);
        $http(req)
            .success(function(data, status, headers, config) {
                callback(data);
            })
            .error(function(data, status, headers, config) {
                if(errorCallback)errorCallback(data,status,headers,config);
                else defaultErrorCallBack('getExchangePointRateInfo',data,status)
            });
    };

    factory.exchangePoint = function(pack,callback,errorCallback){
        var req = {
            method: 'POST',
            url: '/clapi/userstats/exchangePoint/',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            },
            data: $.param({
                pack:pack
            })
        }

        add_auth(req);

        $http(req)
            .success(function(data, status, headers, config) {
                callback(data);
            })
            .error(function(data, status, headers, config) {
                if(errorCallback)errorCallback(data,status,headers,config);
                else defaultErrorCallBack('sendInboxMessage',data,status)
            });
    };

    /////// session
    factory.sendInboxMessage = function(message,to_user_id,to_username,callback,errorCallback){

        var req = {
            method: 'POST',
            url: '/clapi/session/sendInboxMessage/',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            },
            data: $.param({
                text:message,
                sid:to_user_id,
                to_username:to_username
            })
        }

        add_auth(req);

        $http(req)
            .success(function(data, status, headers, config) {
                callback(data);
            })
            .error(function(data, status, headers, config) {
                if(errorCallback)errorCallback(data,status,headers,config);
                else defaultErrorCallBack('sendInboxMessage',data,status)
            });
    };    

    function convertDateToString(date){
        return date.getFullYear()+'-'+date.getMonth()+'-'+date.getDate();
    }

    factory.listBill = function(from_date,to_date,callback,errorCallback) {
        var getParam='';

        if(from_date){
            if(getParam=='')getParam+='?'+convertDateToString(from_date);
            else getParam+='&from_date='+convertDateToString(from_date);
        }

        if(to_date){
            if(getParam=='')getParam+='?'+convertDateToString(to_date);
            else getParam+='&to_date='+convertDateToString(to_date);
        }

        var req = {
            method: 'GET',
            url: '/clapi/userstats/listBill/'+getParam
        };

        add_auth(req);

        $http(req)
            .success(function(data, status, headers, config) {
                for(var i in data){
                    if(data[i].length){
                      var detail= jQuery.parseJSON(data[i].fields.detail);
                      data[i].fields['detail']=detail;
                    }
                }
                callback(data);
            })
            .error(function(data, status, headers, config) {
                if(errorCallback)errorCallback(data,status,headers,config);
                else defaultErrorCallBack('getUserStorage',data,status)
            });
    };        
    
    factory.listTransaction = function(from_date,to_date,transaction_type,callback,errorCallback) {
        var getParam='';

        if(from_date){
            if(getParam=='')getParam+='?from_date='+from_date;
            else getParam+='&from_date='+from_date;
        }

        if(to_date){
            if(getParam=='')getParam+='?to_date='+to_date;
            else getParam+='&to_date='+to_date;
        }

        if(transaction_type!=null){
            if(getParam=='')getParam+='?transaction_type='+transaction_type;
            else getParam+='&transaction_type='+transaction_type;
        }

        var req = {
            method: 'GET',
            url: '/clapi/userstats/listTransaction/'+getParam
        };
        add_auth(req);
        $http(req)
            .success(function(data, status, headers, config) {
                var transactionList= jQuery.parseJSON(data.transactionList);
                for(var i in transactionList){
                    transactionList[i].fields['invoice_amount']=data.billChargedList[i];
                    transactionList[i].fields['data']=jQuery.parseJSON(transactionList[i].fields['data']);
                }
                callback(transactionList);
            })
            .error(function(data, status, headers, config) {
                if(errorCallback)errorCallback(data,status,headers,config);
                else defaultErrorCallBack('listTransaction',data,status)
            });
    };

    factory.downloadCountSessionStatistic = function(from_date,to_date,callback,errorCallback) {
        var getParam='';

        if(from_date){
            if(getParam=='')getParam+='?from_date='+from_date;
            else getParam+='&from_date='+from_date;
        }

        if(to_date){
            if(getParam=='')getParam+='?to_date='+to_date;
            else getParam+='&to_date='+to_date;
        }

        var req = {
            method: 'GET',
            url: '/clapi/userstats/downloadCountSessionStatistic/'+getParam
        };
        add_auth(req);
        $http(req)
            .success(function(data, status, headers, config) {
                callback(data);
            })
            .error(function(data, status, headers, config) {
                if(errorCallback)errorCallback(data,status,headers,config);
                else defaultErrorCallBack('downloadCountSessionStatistic',data,status);
            });
    };

    factory.newUserOriginFromDownloadLinkStatistic = function(from_date,to_date,callback,errorCallback) {
        var getParam='';

        if(from_date){
            if(getParam=='')getParam+='?from_date='+from_date;
            else getParam+='&from_date='+from_date;
        }

        if(to_date){
            if(getParam=='')getParam+='?to_date='+to_date;
            else getParam+='&to_date='+to_date;
        }

        var req = {
            method: 'GET',
            url: '/clapi/userstats/newUserOriginFromDownloadLinkStatistic/'+getParam
        };
        add_auth(req);
        $http(req)
            .success(function(data, status, headers, config) {
                callback(data);
            })
            .error(function(data, status, headers, config) {
                if(errorCallback)errorCallback(data,status,headers,config);
                else defaultErrorCallBack('newUserOriginFromDownloadLinkStatistic',data,status)
            });
    };

    //payment

    factory.buyPremiumDirectProcess = function(plan_id,paygate_id,
                                               card_number, card_name, card_expiry, card_cvc, first_name, last_name, email, phone_number, address, country, state, city, zipcode,
                                               callback,errorCallback){

        var req = {
            method: 'POST',
            url: '/buypremium/'+plan_id+'/'+paygate_id+'/',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            },
            data: $.param({
                card_number:card_number,
                card_name:card_name,
                card_expiry:card_expiry,
                card_cvc:card_cvc,
                first_name: first_name,
                last_name: last_name,
                email: email,
                phone_number: phone_number,
                address: address,
                country: country,
                state: state,
                city: city,
                zipcode: zipcode
            })
        };

        add_auth(req);

        $http(req)
            .success(function(data, status, headers, config) {
                callback(data);
            })
            .error(function(data, status, headers, config) {
                if(errorCallback)errorCallback(data,status,headers,config);
                else defaultErrorCallBack('buyPremiumDirectProcess',data,status)
            });
    };

    //PremiumKey

    factory.getListPremiumKey = function(offset,limit,callback,errorCallback) {
        var getParam='?offset='+offset+'&limit='+limit;

        var req = {
            method: 'GET',
            url: '/clapi/premium/getListPremiumKey/'+getParam
        };

        add_auth(req);

        $http(req)
            .success(function(data, status, headers, config) {
                callback(data);
            })
            .error(function(data, status, headers, config) {
                if(errorCallback)errorCallback(data,status,headers,config);
                else defaultErrorCallBack('getListPremiumKey',data,status)
            })
        ;
    };

    factory.buyPremiumKeyUsingCredit = function(max_num_key,plan_id, callback,errorCallback){

        var req = {
            method: 'POST',
            url: '/clapi/premium/buyPremiumKeyUsingCredit/',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            },
            data: $.param({
                max_num_key:max_num_key,
                plan_id:plan_id
            })
        };

        add_auth(req);

        $http(req)
            .success(function(data, status, headers, config) {
                callback(data);
            })
            .error(function(data, status, headers, config) {
                if(errorCallback)errorCallback(data,status,headers,config);
                else defaultErrorCallBack('buyPremiumKeyUsingCredit',data,status)
            })
        ;
    };

    factory.exchangePremiumKey = function(premium_code, callback,errorCallback){

        var req = {
            method: 'POST',
            url: '/clapi/premium/exchangePremiumKey/',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            },
            data: $.param({
                premium_code:premium_code
            })
        };

        add_auth(req);

        $http(req)
            .success(function(data, status, headers, config) {
                callback(data);
            })
            .error(function(data, status, headers, config) {
                if(errorCallback)errorCallback(data,status,headers,config);
                else defaultErrorCallBack('buyPremiumKeyUsingCredit',data,status)
            })
        ;
    };

    factory.resendActivationEmail = function(callback,errorCallback){

        var req = {
            method: 'POST',
            url: '/clapi/user/resendActivationEmail/',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            },
            data: $.param({
            })
        };

        add_auth(req);

        $http(req)
            .success(function(data, status, headers, config) {
                callback(data);
            })
            .error(function(data, status, headers, config) {
                if(errorCallback)errorCallback(data,status,headers,config);
                else defaultErrorCallBack('resendActivationEmail',data,status)
            })
        ;
    };

    factory.applyToBecomeAffiliate = function(website_address, callback,errorCallback){

        var req = {
            method: 'POST',
            url: '/clapi/user/applyToBecomeAffiliate/',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            },
            data: $.param({
                website_address:website_address
            })
        };

        add_auth(req);

        $http(req)
            .success(function(data, status, headers, config) {
                callback(data);
            })
            .error(function(data, status, headers, config) {
                if(errorCallback)errorCallback(data,status,headers,config);
                else defaultErrorCallBack('applyToBecomeAffiliate',data,status)
            })
        ;
    };
    
    factory.applyToChangeAffiliateMode = function(affiliate_mode, callback, errorCallback){

        var req = {
            method: 'POST',
            url: '/clapi/user/applyToChangeAffiliateMode/',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            },
            data: $.param({
                affiliate_mode:affiliate_mode
            })
        };

        add_auth(req);

        $http(req)
            .success(function(data, status, headers, config) {
                callback(data);
            })
            .error(function(data, status, headers, config) {
                if(errorCallback)errorCallback(data,status,headers,config);
                else defaultErrorCallBack('applyToChangeAffiliateMode',data,status)
            })
        ;
    };

    factory.addWebsiteAgencyDomain = function(website_address, callback,errorCallback){

        var req = {
            method: 'POST',
            url: '/clapi/user/addWebsiteAgencyDomain/',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            },
            data: $.param({
                website_address:website_address
            })
        };

        add_auth(req);

        $http(req)
            .success(function(data, status, headers, config) {
                callback(data);
            })
            .error(function(data, status, headers, config) {
                if(errorCallback)errorCallback(data,status,headers,config);
                else defaultErrorCallBack('addWebsiteAgencyDomain',data,status)
            })
        ;
    };

    factory.getListWebsiteAgency = function(callback,errorCallback) {

        var req = {
            method: 'GET',
            url: '/clapi/user/getListWebsiteAgency/'
        };

        add_auth(req);

        $http(req)
            .success(function(data, status, headers, config) {
                callback(data);
            })
            .error(function(data, status, headers, config) {
                if(errorCallback)errorCallback(data,status,headers,config);
                else defaultErrorCallBack('getListWebsiteAgency',data,status)
            })
        ;
    };

    factory.createReport = function(text,file_id,user_id,detail,callback,errorCallback){
        var req = {
            method: 'POST',
            url : '/clapi/session/createReport/',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            },
            data: $.param({
                'text' : text,
                'fid': file_id,
                'sid' : user_id,
                'detail' : detail
            })
        };

        add_auth(req);

        $http(req)
            .success(function(data, status, headers, config) {
                callback(data);
            })
            .error(function(data, status, headers, config) {
                if(errorCallback)errorCallback(data,status,headers,config);
                else defaultErrorCallBack('createReport',data,status)
            })
        ;
    };

    return factory;
}]);
