$(function() {
  "use strict";
  let dt = luxon.DateTime.now();
  formatFooter(dt);
  checkMC(860);
  $('body').on('click', '.closeable', closeTopFlashed);
  $.ajax({
    method: 'GET',
    url: '/api/setpasswd',
    headers: {
      'x-reg-token': key,
    },
    success: function(data) {
      if (data.aid) {
        let html = Mustache.render($('#crpt').html(), data);
        $('#main-container').append(html);
        if ($('.today-field').length) renderTF('.today-field', dt);
        checkMC(860);
      } else {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#main-container').append(html).removeClass('nonlisted');
        slidePage('#ealert');
      }
    },
    complete: function() {
      if (!$('#main-container').children().length) {
        let data = {'message': 'Проверьте ссылку.'}
        let html = Mustache.render($('#ealertt').html(), data);
        $('#main-container').removeClass('nonlisted').append(html);
        slidePage('#ealert');
      }
    },
    dataType: 'json'
  });
  $('body').on('click', '#crp-submit', function() {
    $(this).blur();
    let tee = {
      username: $('#username').val(),
      passwd: $('#crpassword').val(),
      confirma: $('#confirmation').val(),
      aid: $(this).data().aid
    };
    if (tee.username && tee.passwd && tee.confirma && tee.aid) {
      $.ajax({
        method: 'POST',
        url: '/api/setpasswd',
        data: tee,
        success: function(data) {
          if (data.done) {
            window.location.replace('/');
          } else {
            showError('#crpf', data);
          }
        },
        dataType: 'json'
      });
    }
  });
});
