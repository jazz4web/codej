$(function() {
  "use strict";
  let dt = luxon.DateTime.now();
  formatFooter(dt);
  $('body').on('click', '.closeable', closeTopFlashed);
  $.ajax({
    method: 'GET',
    url: '/api/captcha',
    success: function(data) {
      let form = Mustache.render($('#regt').html(), data);
      $('#main-container').append(form);
      if ($('.today-field').length) renderTF('.today-field', dt);
      checkMC(860);
    },
    dataType: 'json'
  });
  checkMC(860);
  $('body').on('click', '#rcaptcha-reload',
    {field: '#rcaptcha-field', suffix: '#rsuffix', captcha: '#rcaptcha'},
    captchaReload);
  $('body').on('click', '#reg-submit', regSubmit);
});
