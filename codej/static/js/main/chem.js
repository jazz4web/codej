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
  $.ajax({
    method: 'GET',
    url: '/api/change-email',
    headers: {
      'x-reg-token': key,
      'x-auth-token': window.localStorage.getItem('token')
    },
    success: function(data) {
      if (data.done) {
        window.location.replace('/');
      } else {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#main-container').append(html);
        slidePage('#ealert');
      }
    },
    dataType: 'json'
  });
});
