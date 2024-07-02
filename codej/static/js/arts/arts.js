$(function() {
  "use strict";
  if (cu && !window.localStorage.getItem('token')) {
    ping();
    window.location.reload();
  }
  if (!cu && window.localStorage.getItem('token')) {
    window.localStorage.removeItem('token');
  }
  let dt = luxon.DateTime.now();
  formatFooter(dt);
  $('body').on('click', '.closeable', closeTopFlashed);
  showDrafts(dt, '/api/arts', page);
  $('body').on('click', '.page-link', function(event) {
    event.preventDefault();
    let th = $(this).parent();
    if (!th.hasClass('active')) {
      window.location.assign('/arts/?page=' + $(this).text().trim());
    }
  });
  $('body').on('click', '#next-link', {page: page}, function(event) {
    event.preventDefault();
    let p = event.data.page + 1;
    window.location.assign('/arts/?page=' + p);
  });
  $('body').on('click', '#prev-link', {page: page}, function(event) {
    event.preventDefault();
    let p = event.data.page - 1;
    window.location.assign('/arts/?page=' + p);
  });
  if (window.localStorage.getItem('token')) checkIncomming();
});
