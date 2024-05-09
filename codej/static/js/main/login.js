$(function() {
  "use strict";
  let dt = luxon.DateTime.now();
  formatFooter(dt);
  $('body').on('click', '.closeable', closeTopFlashed);
  login(dt);
  $('body').on('click', '#lcaptcha-reload',
    {field: '#lcaptcha-field', suffix: '#lsuffix', captcha: '#lcaptcha'},
    captchaReload);
  $('body').on('click', '#login-submit', loginSubmit);
});
