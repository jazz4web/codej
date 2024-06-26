$(function() {
  "use strict";
  let dt = luxon.DateTime.now();
  formatFooter(dt);
  $('body').on('click', '.closeable', closeTopFlashed);
  $.ajax({
    method: 'GET',
    url: '/api/captcha',
    success: function(data) {
      let form = Mustache.render($('#logint').html(), data);
      $('#main-container').append(form);
      if ($('.today-field').length) renderTF('.today-field', dt);
      checkMC(860);
    },
    dataType: 'json'
  });
  $('body').on('click', '#lcaptcha-reload',
    {field: '#lcaptcha-field', suffix: '#lsuffix', captcha: '#lcaptcha'},
    captchaReload);
  $('body').on('click', '#login-submit', loginSubmit);
  $('body').on('click', '#login-reg', function() {
    $(this).blur();
    window.location.replace($('#reg').attr('href'));
  });
  checkMC(860);
});
