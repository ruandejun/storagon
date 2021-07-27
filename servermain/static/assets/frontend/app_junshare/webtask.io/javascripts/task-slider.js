var slice = [].slice;

(function($, window) {
  var TaskSlider;
  TaskSlider = (function() {
    TaskSlider.prototype.defaults = {
      controls: '.controls',
      slides: '.slides',
      animationIn: 'fadeInRight',
      animationInReversed: 'fadeInLeft',
      durationIn: 400,
      animationOut: 'fadeOutLeft',
      animationOutReversed: 'fadeOutRight',
      durationOut: 200,
      singleSlide: false,
      hammer: false,
      beforeNav: function() {
        return false;
      },
      afterNav: function() {
        return false;
      }
    };

    function TaskSlider(el, options) {
      this.options = $.extend({}, this.defaults, options);
      this.element = $(el);
      this.controls = this.element.find(this.options.controls + ' > *');
      this.slides = this.element.find(this.options.slides + ' > *');
      this.init();
    }

    TaskSlider.prototype.init = function() {
      var $body, api;
      api = this;
      $body = $('body');
      this.element.addClass('js-task-slider');
      this.controls.eq(0).addClass('is-active');
      this.slides.eq(0).addClass('is-active animated ' + this.options.animationIn);
      this.setControlsOffset();
      this.element.on('click', this.options.controls + ' > *', function() {
        var index;
        index = $(this).index();
        if (api.controls.filter('.is-active').index() === index) {
          return;
        }
        api.navigate(index, $(this));
        api.controls.removeClass('is-active');
        $(this).addClass('is-active');
        return api.setControlsOffset();
      });
      this.touchEvents(this);
      return $body.on('resize', this.setControlsOffset());
    };

    TaskSlider.prototype.navigate = function(number, button) {
      var $leaving, $target, animationEnd, animations, css, isBack;
      animationEnd = 'animationend webkitAnimationEnd mozAnimationEnd';
      button = button ? button : false;
      $target = this.slides.eq(number);
      $leaving = this.slides.filter('.is-active');
      isBack = this.controls.filter('.is-active').index() > button.index();
      animations = this.setAnimations(isBack);
      css = {
        "in": 'is-active animated ' + animations["in"],
        out: 'animated ' + animations.out,
        all: 'is-active ' + this.options.animationIn + ' ' + this.options.animationInReversed + ' animated ' + this.options.animationOut + ' ' + this.options.animationOutReversed
      };
      this.options.beforeNav(button);
      this.setDuration($leaving, this.options.durationOut);
      if (this.options.singleSlide) {
        $target = $leaving;
      }
      $leaving.addClass(css.out);
      return $leaving.on(animationEnd, (function(_this) {
        return function() {
          $leaving.unbind(animationEnd);
          $leaving.removeClass(css.all);
          _this.setDuration($target, _this.options.durationIn);
          $target.addClass(css["in"]);
          return _this.options.afterNav(button);
        };
      })(this));
    };

    TaskSlider.prototype.touchEvents = function(api) {
      var touchControl;
      if (!this.options.hammer || !Hammer) {
        return;
      }
      touchControl = new Hammer($(this.element).get(0), {
        recognizers: [
          [
            Hammer.Swipe, {
              direction: Hammer.DIRECTION_HORIZONTAL
            }
          ]
        ]
      });
      return touchControl.on('swiperight swipeleft', function(e) {
        var active, next, nextI, prevI;
        active = api.controls.filter('.is-active');
        nextI = active.index() + 1;
        prevI = active.index() - 1;
        next = [];
        if (e.type === 'swipeleft') {
          next = $(api.controls.eq(nextI));
        }
        if (e.type === 'swiperight') {
          next = $(api.controls.eq(prevI));
        }
        if (next.length) {
          api.navigate(next.index(), $(next));
          api.controls.removeClass('is-active');
          next.addClass('is-active');
          api.setControlsOffset();
        }
      });
    };

    TaskSlider.prototype.setAnimations = function(isBack) {
      var animations, directionIn, directionOut;
      if (this.options.animationInReversed) {
        directionIn = !isBack ? this.options.animationIn : this.options.animationInReversed;
      } else {
        directionIn = this.options.animationIn;
      }
      if (this.options.animationOutReversed) {
        directionOut = !isBack ? this.options.animationOut : this.options.animationOutReversed;
      } else {
        directionOut = this.options.animationOut;
      }
      return animations = {
        "in": directionIn,
        out: directionOut
      };
    };

    TaskSlider.prototype.setControlsOffset = function() {
      var $active, offsetLeft, properties, value, width;
      $active = this.controls.filter('.is-active');
      width = $active.outerWidth(true);
      offsetLeft = Math.floor($active.position().left + (width / 2));
      value = "translateX(-" + offsetLeft + "px)";
      properties = {
        "-webkit-transform": value,
        "transform": value
      };
      return this.controls.parent().css(properties);
    };

    TaskSlider.prototype.setDuration = function($elem, miliseconds) {
      var ms, properties;
      ms = miliseconds + 'ms';
      properties = {
        "-webkit-animation-duration": ms,
        "animation-duration": ms
      };
      return $elem.css(properties);
    };

    return TaskSlider;

  })();
  return $.fn.extend({
    taskSlider: function() {
      var args, option;
      option = arguments[0], args = 2 <= arguments.length ? slice.call(arguments, 1) : [];
      return this.each(function() {
        var $this, data;
        $this = $(this);
        data = $this.data('taskSlider');
        if (!data) {
          $this.data('taskSlider', (data = new TaskSlider(this, option)));
        }
        if (typeof option === 'string') {
          return data[option].apply(data, args);
        }
      });
    }
  });
})(window.jQuery, window);
