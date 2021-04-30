"use strict";

/*! signup.js | Friendkit | © Css Ninja. 2019-2020 */

/* ==========================================================================
Signup Process JS
========================================================================== */

$(document).ready(function () {
  "use strict";
  
   $('.progress-wrap .dot').on('click', function () {
    var $this = $(this);
    var stepValue = $this.attr('data-step');
    $this.closest('.progress-wrap').find('.bar').css('width', stepValue + '%');
    $this.siblings('.dot').removeClass('is-current');
    $this.addClass('is-active is-current');
    $this.prevAll('.dot').addClass('is-active');
    $this.nextAll('.dot').removeClass('is-active');
    $('.process-panel-wrap').removeClass('is-active');
    $('.step-title').removeClass('is-active');

    if (stepValue == '0') {
      $('#signup-panel-1, #step-title-1').addClass('is-active');
    } else if (stepValue == '25') {
      $('#signup-panel-2, #step-title-2').addClass('is-active');
    } else if (stepValue == '50') {
      $('#signup-panel-3, #step-title-3').addClass('is-active');
    } else if (stepValue == '75') {
      $('#signup-panel-4, #step-title-4').addClass('is-active');
    } else if (stepValue == '100') {
      $('#signup-panel-5, #step-title-5').addClass('is-active');
    }
  });
  
  $('.process-button').bind('click', function () {
    var $this = $(this);
    var targetStepDot = $this.attr('data-step');
    $this.addClass('is-loading');
    setTimeout(function () {
      $this.removeClass('is-loading');
      $('#' + targetStepDot).trigger('click');
    }, 800); 
  });
 });