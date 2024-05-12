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
  checkMC(860);
});
