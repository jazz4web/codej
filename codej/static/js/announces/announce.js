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
  let token = window.localStorage.getItem('token');
  let tee = token ? {'x-auth-token': token} : {};
  $.ajax({
    method: 'GET',
    url: '/api/announce',
    headers: tee,
    data: {
      suffix: suffix
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
        $('title').text(
          $('title').text().trim() + ' ' + data.announce.headline);
        let html = Mustache.render($('#announcet').html(), data);
        $('#main-container').append(html);
        $('.date-field').each(function() { formatDateTime($(this)); });
        checkMC(860);
      }
    },
    dataType: 'json'
  });
  if (token) {
    //pass;
  }
});
