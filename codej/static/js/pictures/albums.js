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
  checkMC(1152);
  let token = window.localStorage.getItem('token');
  let tee = token ? {'x-auth-token': token} : {};
  $.ajax({
    method: 'GET',
    url: '/api/pictures',
    data: {
      page: page
    },
    headers: tee,
    success: function(data) {
      console.log(data);
      if (token) {
        if (!data.cu || data.cu.brkey != checkBrowser()) {
          window.localStorage.removeItem('token');
          window.location.reload();
        }
      }
      if (data.message) {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#main-container').removeClass('nonlisted').append(html);
        slidePage('#ealert');
      } else {
        let html = Mustache.render($('#albumst').html(), data);
        $('#main-container').append(html);
        let ust = Mustache.render($('#ustatt').html(), data);
        $('#right-panel').append(ust);
        formatDateTime($('.date-field'));
        checkMC(1152);
      }
    },
    dataType: 'json'
  });
});
