//(function($){
  "use strict";


  // SMOOTH SCROLL________________________//
  $(function() {
    $('a[href*=#]:not([href=#])').click(function() {
      if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'') && location.hostname == this.hostname) {
        var target = $(this.hash);
        target = target.length ? target : $('[name=' + this.hash.slice(1) +']');
        if (target.length) {
          $('html,body').animate({
            scrollTop: target.offset().top
          }, 1000);
          return false;
        }
      }
    });
  });
  
  // ______________ BIND CLICK ON TOP BAR OF PANEL

  $('#panel ul.nav').unbind('click');
  $(document).on('click', '#panel #upload-panel', function (e) {
    e.stopPropagation();
    if (!$("#panel").hasClass("active")) {
      $("#panel").addClass("active");
       $('#tawkchat-iframe-container').css("display", "none");
    }
    else {
        $('#tawkchat-iframe-container').css("display", "block");
      $("#panel").removeClass("active");
    }
  });
  
  // ______________ BIND CLICK ON FUNCTIONAL BUTTONS
  $('#pause-all-progress').unbind('click');
  $('.stop-progress').unbind('click');

  $(document).on('click', '#pause-all-progress', function (e) {
    e.stopPropagation();
    panel_helper.pauseAllProgress($(this));
    for (var randomID in resumableObjList) {
      if (resumableObjList.hasOwnProperty(randomID)) {
          var r = resumableObjList[randomID];
          if(r.isUploading()) {
              r.pause();
          }
      }
    }
  });

  $(document).on('click', '#resume-all-progress', function (e) {
    e.stopPropagation();
    panel_helper.resumeAllProgress($(this));
    for (var randomID in resumableObjList) {
        if (resumableObjList.hasOwnProperty(randomID)) {
          var r = resumableObjList[randomID];
          if(!r.isUploading()) {
              r.upload();
          }
        }
    }
  });
  $(document).on('click', '.stop-progress', function (e) {
    e.stopPropagation();
    var progress_id = $(this).closest('tr').attr('id');
    if(progress_id in resumableObjList) {
        var r = resumableObjList[progress_id];
        if(r.isUploading()) {
            console.log('pause');
            r.pause();
            panel_helper.pauseProcess($(this));
        }
    }
    //r = null;
  });

  $(document).on('click', '.resume-progress', function (e) {
        e.stopPropagation();
        var progress_id = $(this).closest('tr').attr('id');
        //var array = [];
        // for (var randomID in resumableObjList) {
        //    if (resumableObjList.hasOwnProperty(randomID))
        //        array.push(randomID);
        //}
        //console.log(array);
        //console.log(progress_id);
        if(progress_id in resumableObjList) {
            var r = resumableObjList[progress_id];
            if(!r.isUploading() && r.progress() != 1) {
                console.log('resume');
                r.upload();
                panel_helper.resumeProcess($(this));
            }
        }
  });

  $(document).on('click', '.remove-progress', function (e) {
        e.stopPropagation();
        $(this).closest('tr').remove();
        var progress_id = $(this).closest('tr').attr('id');
        if(progress_id in resumableObjList) {
            console.log('cancel');
            var r = resumableObjList[progress_id];
            r.cancel();
        }
         // there is no file in progress, so restore first state of UI
        if(!$('.remove-progress').length)
            panel_helper.restoreFirstState();
  });



  // ______________ BACK TO TOP BUTTON
  $(window).scroll(function () {
      if ($(this).scrollTop() > 300) {
          $('#back-to-top').fadeIn('slow');
      } else {
          $('#back-to-top').fadeOut('slow');
  }});

    // work with UI on upload panel
  function Fmpanelhelper(){
      this.pauseProcess = function(o){
          o.closest('td').find(".resume-progress").show();
          o.closest('td').find(".stop-progress").hide();
      };
      this.resumeProcess = function(o){
          o.closest('td').find(".resume-progress").hide();
          o.closest('td').find(".stop-progress").show();
      };
      this.toogleProgress = function(o){
          o.closest('td').find(".resume-progress").toggle();
          o.closest('td').find(".stop-progress").toggle();
      };
      this.pauseAllProgress = function(o){
          o.closest('div').find("#resume-all-progress").show();
          o.closest('div').find("#pause-all-progress").hide();
          $( ".stop-progress" ).each(function() {
                panel_helper.pauseProcess($(this));
          });
      };
      this.resumeAllProgress = function(o){
          o.closest('div').find("#pause-all-progress").show();
          o.closest('div').find("#resume-all-progress").hide();
          $( ".stop-progress" ).each(function() {
                panel_helper.resumeProcess($(this));
          });
      };

      this.restoreFirstState = function(){
          $("#pause-all-progress").show();
          $("#resume-all-progress").hide();
      };
  }
  var panel_helper = new Fmpanelhelper();
//})(jQuery);