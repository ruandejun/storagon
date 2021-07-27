/** JavaScript on WebKit
 *
 *  sessionView.js
 *
 *
 *  Created by TVA on 3/12/15.
 *  Copyright (c) 2015 storagon. All rights reserved.
 */
'use strict';
var app = angular.module('Storagon.user.sessionView', []);

app.controller('inboxController', ['$scope', 'User_ClientAPI', 'User_RESTFullAPI', function ($scope, $sdk, $sdkREST) {
    $sdkREST.getListSession(SessionType.inbox, null, null, null, null, null, null, function (data) {      
      $scope.inboxMessages = data.results;
    });

    $scope.submit = function () {
        angular.element('.loader').show();
        $scope.error = false;
        $scope.isProcessing = true;
        $sdk.sendInboxMessage(this.message, 0, this.to_username, function (data) {
            $sdkREST.getListSession(SessionType.inbox, null, null, null, null, null, null, function (data) {      
              $scope.inboxMessages = data.results;
              angular.element('.loader').hide();
              $('#modal-inbox').foundation('reveal', 'close');
            });
            $scope.isProcessing = false;
        }, function(){
            angular.element('.loader').hide();
            $scope.message = "Failed to send message. Please try again";
            $scope.error = true;
            $scope.isProcessing = false;
        });
        $('a.close').on('click', function() {
            $('#modal-inbox').foundation('reveal', 'close');
        });
    };
}]);

app.controller('reportController', ['$scope', 'User_ClientAPI', 'User_RESTFullAPI', function ($scope, $sdk, $sdkREST) {
    $sdkREST.getListSession(SessionType.report, null, null, null, null, null, null, function (data) {
        console.log(data.results);
        $scope.reports = data.results;
    });
    angular.element('#report').click(function(e){
      angular.element('#modal-report').foundation('reveal', 'open');
      angular.element('#modal-report').unbind('click');
    });
    $scope.processForm = function () {
        angular.element('.loader').show();
        $scope.error = false;
        $scope.isProcessing = true;        
        //todo: filter file_id from $scope.file_url
        if($scope.text === "DCMA"){
          var url_path_array = $scope.file_url.split('/');
          var file_id = url_path_array[2];
        }
        else{
          var file_id = 0;
        }

        $sdk.createReport($scope.text, file_id, CURRENT_USER.id, $scope.detail, function () {
            angular.element('.loader').hide();            
            angular.element('#modal-report').foundation('reveal','close');
            $scope.isProcessing = false;
            $sdkREST.getListSession(SessionType.report, null, null, null, null, null, null, function (data) {
              $scope.reports = data.results;
            });
        }, function () {
            angular.element('.loader').hide();
            $scope.message = "Failed to send report. Please try again";
            $scope.error = true;            
            $scope.isProcessing = false;
        });
    };
}]);

app.controller('statisticController', ['$scope', 'User_ClientAPI', 'User_RESTFullAPI', '$cookies', function ($scope, $sdk, $sdkREST, $cookies) {
    var currentDate = new Date();
    var lastDate = new Date(currentDate.getTime() - (6 * 24 * 60 * 60 * 1000));
    currentDate.setMonth(currentDate.getMonth() + 1);
    lastDate.setMonth(lastDate.getMonth() + 1);    
    $scope.$watch(
      function() {        
        return parseInt($cookies['account_type']);
      },
      function(newValue, oldValue) {
        switch(newValue){
          case 1:
            $scope.affMode = 'pps';
            break;
          case 3:
            $scope.affMode = 'ppd';
            break;
        }
      }              
    );
    var options = {
      chart: {
        type: 'line'
      },
      title: {
        text: ''
      },
      subtitle: {
        text: ''
      },
      xAxis: {
        title: {
          text: 'Date'
        },
        categories: []
      },
      yAxis: {
        title: {
          text: 'Count'
        }
      },
      plotOptions: {
        line: {
          dataLabels: {
            enabled: true,
            format: '<b>{y}</b>'
          },
          enableMouseTracking: true
        }
      },
      series: [{
          name: '',
          data: []
        }
      ]
    };
    
    var reinitialize_pagination = function(totalRecords, perPage){
      // Remove old pagination
      if($('#session_pagination').length){
        $('#session_pagination').remove();
      }
     
      // Reinitialize pagination      
      if(totalRecords !== 0 && parseInt($('#download-count-perpage').val()) !== 0){
        $('div#downloadSessions').append("<ul class=\'pagination right\' id=\'session_pagination\' role=\'menubar\' aria-label=\'Pagination\'></ul>");
        $('#session_pagination').twbsPagination({
          totalPages: (totalRecords % perPage === 0) ? (totalRecords / perPage) : (Math.ceil(totalRecords / perPage)),
          prev: '&laquo; Previous',
          next: 'Next &raquo;',
          first: '&laquo;&laquo; First',
          last: 'Last &raquo;&raquo;',
          nextClass: 'arrow',
          prevClass: 'arrow',
          activeClass: 'current',
          disabledClass: 'unavailable',
          visiblePages: 10,
          onPageClick: function (event, pageNum) {
            $sdkREST.getListSession(SessionType.download, SessionStatus.completed, $('input.fromDate').eq(1).val(), $('input.toDate').eq(1).val(), pageNum, $('#download-count-perpage').val(), {oid : CURRENT_USER.id}, function (data) {
              $scope.downloadCounts = data.results;
            });
          }
        });
      }
    };
    
    var updateChart = function(chartID, data){
      var ChartArrayDate = [];
      var ChartArrayCount = [];
      if(data.length) {
        for(var i in data){
          var group_id = data[i]._id;
          if(typeof(group_id) !== 'undefined'){
            var count = data[i].count;
            var countDate = group_id.day +'/' + group_id.month;
            ChartArrayDate.push(countDate);
            ChartArrayCount.push(count);
          }
        }
      }      
      options.title.text = (chartID === "linechartDownload") ? 'Download count by day' : 'Origional user from my download link';
      options.series[0].name = (chartID === "linechartDownload") ? 'Download Counts' : 'Original User Count';
      options.chart.renderTo = chartID;
      options.series[0].data = ChartArrayCount;
      options.xAxis.categories = ChartArrayDate;
      var chartID = new Highcharts.Chart(options);
    };
    
    var updateStatistic = function(fromDate, toDate, initialize, perPage){      
      if(!initialize){
        switch ($('ul.tabs').find('li.active').find('a').attr('href')){
          case "#overview":
            $sdkREST.getTransactionStatistic(fromDate, toDate, function (data) {                
              $scope.transactionStatsitic = data;
            });
            break;
          case "#downloadSessions":
            if(parseInt(perPage) === 0){
              perPage = $('#totalRecords').val();
            }
            $sdkREST.getListSession(SessionType.download, SessionStatus.completed, fromDate, toDate, 1, perPage, {oid : CURRENT_USER.id}, function (data) {
              $scope.downloadCounts = data.results;
              $('#totalRecords').val(data.count);
              reinitialize_pagination(data.count, parseInt(perPage));
            });
            break;  
          case "#downloadCountChart":
            $sdk.downloadCountSessionStatistic(fromDate, toDate, function (data) {              
              updateChart('linechartDownload', data);
            });
            break;
          case "#myOriginalUser":
            $sdk.newUserOriginFromDownloadLinkStatistic(fromDate, toDate, function (data) {
              updateChart('linechartOriginalUser', data);
            });
            break;
        }
      }
      else{
        $sdkREST.getTransactionStatistic(fromDate, toDate, function (data) {                
          $scope.transactionStatsitic = data;
        });
        $sdkREST.getListSession(SessionType.download, SessionStatus.completed, fromDate, toDate, 1, perPage, {oid : CURRENT_USER.id}, function (data) {
          $scope.downloadCounts = data.results;
          $('#totalRecords').val(data.count);
          reinitialize_pagination(data.count, parseInt(perPage));
        });
        $sdk.downloadCountSessionStatistic(fromDate, toDate, function (data) {
          updateChart('linechartDownload', data);       
        });   
        $sdk.newUserOriginFromDownloadLinkStatistic(fromDate, toDate, function (data) {          
          updateChart('linechartOriginalUser', data);
        });
      }
    };
        
    updateStatistic(lastDate.getFullYear() + '-' + ("0" + lastDate.getMonth()).slice(-2) + '-' + ("0" + lastDate.getDate()).slice(-2), currentDate.getFullYear() + '-' + ("0" + currentDate.getMonth()).slice(-2) + '-' + ("0" + currentDate.getDate()).slice(-2), true, $('#download-count-perpage').val());
    
    $('#download-count-perpage').on('change', function(){
      updateStatistic($('input.fromDate').eq(1).val(), $('input.toDate').eq(1).val(), false, $(this).val());
    });
    
    $(document).foundation();
    
    $('.fromDate').each(function(){
      $(this).val(lastDate.getFullYear() + '-' + ("0" + lastDate.getMonth()).slice(-2) + '-' + ("0" + lastDate.getDate()).slice(-2));
      $(this).fdatepicker({
        format: 'yyyy-mm-dd'
      }).on('changeDate', function(ev){
        updateStatistic($(this).val(), $(this).parent().siblings('div.input-append').find('input.toDate').eq(0).val(), false, $('#download-count-perpage').val());
      });
    });  
    $('.toDate').each(function(){
      $(this).val(currentDate.getFullYear() + '-' + ("0" + currentDate.getMonth()).slice(-2) + '-' + ("0" + currentDate.getDate()).slice(-2));
      $(this).fdatepicker({
        format: 'yyyy-mm-dd'      
      }).on('changeDate', function(ev){
        updateStatistic($(this).parent().siblings('div.input-append').find('input.fromDate').eq(0).val(), $(this).val(), false, $('#download-count-perpage').val());
      });
    });
}]);