$(function() {
  "use strict";
  if (cu && !window.localStorage.getItem('token')) {
    ping();
    window.location.reload();
  }
  if (!cu && window.localStorage.getItem('token')) {
    window.localStorage.removeItem('token');
  }
  if (lall) {
    // logout.js;
    lout('/api/logoutall');
  }
  if (logout) {
    // logout.js;
    lout('/api/logout');
  }
  let dt = luxon.DateTime.now();
  formatFooter(dt);
  if ($('.today-field').length) renderTF('.today-field', dt);
  $('body').on('click', '.closeable', closeTopFlashed);
  $('.date-field').each(function() { formatDateTime($(this)); });
  $('.entity-text-block img').on('click', clickImage);
  checkMC(860);
  $('.entity-text-block iframe').each(adjustFrame);
  $('.entity-text-block').children().each(setMargin);
  $('.entity-text-block img').each(adjustImage);
  if (window.localStorage.getItem('token')) {
    checkIncomming();
  }
});
