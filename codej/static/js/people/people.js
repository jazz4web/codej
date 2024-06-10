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
  checkMC(860);
  let token = window.localStorage.getItem('token');
  let tee = token ? {'x-auth-token': token} : {};
  $.ajax({
    method: 'GET',
    url: '/api/people',
    headers: tee,
    data: {
      page: page
    },
    success: function(data) {
      if (token) {
        if (!data.cu || data.cu.brkey != checkBrowser()) {
          window.localStorage.removeItem('token');
          window.location.reload();
        }
      }
      if (data.message) {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#main-container').append(html);
        slidePage('#ealert');
      } else {
        let html = Mustache.render($('#peoplet').html(), data);
        $('#main-container').append(html);
        if ($('.today-field').length) renderTF('.today-field', dt);
        $('.entity-block').each(checkNext);
        $('.date-field').each(function() { formatDateTime($(this)); });
        $('.last-seen').each(function() { renderLastSeen($(this)); });
        if (data.pv) renderPV(data.pagination.page);
        checkMC(860);
      }
    },
    dataType: 'json'
  });
  $('body').on('click', '.page-link', function(event) {
    event.preventDefault();
    let th = $(this).parent();
    if (!th.hasClass('active')) {
      window.location.assign('/people/?page=' + $(this).text().trim());
    }
  });
  $('body').on('click', '#next-link', {page: page}, function(event) {
    event.preventDefault();
    let p = event.data.page + 1;
    window.location.assign('/people/?page=' + p);
  });
  $('body').on('click', '#prev-link', {page: page}, function(event) {
    event.preventDefault();
    let p = event.data.page - 1;
    window.location.assign('/people/?page=' + p);
  });
});
