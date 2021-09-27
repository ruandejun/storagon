(function($){ 
  "use strict";

  // ______________ SUPERFISH
  jQuery('ul.sf-menu').superfish({
      speed : 1,
      animation: false,
      animationOut: false
  });

  $(function(){
      $('nav.mobile-menu').slicknav({
          closedSymbol: "&#8594;",
          openedSymbol: "&#8595;"
      });
  });

  // BLOG SLIDER_________________________ //   

  $(document).ready(function() {
      $("#blogslider").owlCarousel({
      navigation : false,
      slideSpeed : 300,
      paginationSpeed : 400,
      singleItem:true
      });
  });

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
  $('#panel nav.top-bar').unbind('click');
  $(document).on('click', '#panel nav.top-bar', function (e) {
    //e.stopPropagation();
    if (!$("#panel").hasClass("active")) {
      $("#panel").addClass("active");
      $("div.main").height(deviceHeight - 318);
      $('div.sidebar-fm').height($('div.small-10.columns').height());
      $("#panel").animate({height: "160px"}, 100, function () {
        $("#panel").css({"overflow-y": "auto"});
      });
    }
    else {
      $("#panel").removeClass("active");
      $("#panel").animate({height: "34px"}, 100, function () {
        $("#panel").css({"overflow": "hidden"});
        $("div.main").height(deviceHeight - 178);
        $('div.sidebar-fm').height($('div.small-10.columns').height());
      });
    }
  });
  
  // ______________ BIND CLICK ON FUNCTIONAL BUTTONS
  $('#cancel-all-progress').unbind('click');
  $('.stop-progress').unbind('click');
  $(document).on('click', '#cancel-all-progress', function (e) {
    e.stopPropagation();
    $.each(resumableObjList, function (key, value) {
      var r = value;
      r.cancel();
      r = null;
    });
  });
  $(document).on('click', '.stop-progress', function (e) {
    e.stopPropagation();
    var progress_id = $(this).closest('tr').attr('id');
    var r = resumableObjList[progress_id];
    r.cancel();
    r = null;
  });
  
  // ______________ LIVECHAT BUTTON
  $(document).on('click', '#livechat', function(e){
    e.stopPropagation();
    if(!$('#tawkchat-iframe-container').hasClass('active')){      
      $('#tawkchat-iframe-container').get(0).style.setProperty('display', 'block', 'important');
      $_Tawk.toggle();      
      $('#tawkchat-iframe-container').addClass('active');
    }
    else{      
      $('#tawkchat-iframe-container').get(0).style.setProperty('display', 'none', 'important');
      $_Tawk.toggle();
      $('#tawkchat-iframe-container').removeClass('active');
    }
  });

  // ______________ BACK TO TOP BUTTON
  $(window).scroll(function () {
      if ($(this).scrollTop() > 300) {
          $('#back-to-top').fadeIn('slow');
      } else {
          $('#back-to-top').fadeOut('slow');
  }});  

  $(document).foundation();

})(jQuery);