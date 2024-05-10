function captchaReload(event) {
  $(this).blur();
  $.ajax({
    method: 'GET',
    url: '/api/captcha',
    success: function(data) {
      $(event.data.field).attr({"style": 'background:url(' + data.url + ')'});
      $(event.data.suffix).val(data.captcha);
      $(event.data.captcha).val('');
      $(event.data.captcha).focus();
    },
    dataType: 'json'
  });
}
