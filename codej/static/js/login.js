function login(dt) {
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
}
