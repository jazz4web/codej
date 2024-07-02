$(function() {
  "use strict";
  let dt = luxon.DateTime.now();
  formatFooter(dt);
  checkMC(860);
  $('body').on('click', '.closeable', closeTopFlashed);
  $.ajax({
    method: 'GET',
    url: '/api/reset-passwd',
    headers: {
      'x-reg-token': key
    },
    success: function(data) {
      if (!data.aid) {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#main-container').append(html).removeClass('nonlisted');
        slidePage('#ealert');
      } else {
        let html = Mustache.render($('#rspt').html(), data);
        $('#main-container').append(html);
        if ($('.today-field').length) renderTF('.today-field', dt);
        checkMC(860);
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
  $('body').on('click', '#rsp-submit', function() {
    $(this).blur();
    let tee = {
      address: $('#rsaddress').val(),
      passwd: $('#rspassword').val(),
      confirma: $('#rsconfirm').val(),
      aid: $(this).data().aid
    };
    if (tee.address && tee.passwd && tee.confirma && tee.aid) {
      $.ajax({
        method: 'POST',
        url: '/api/reset-passwd',
        data: tee,
        success: function(data) {
          if (data.done) {
            window.location.replace('/');
          } else {
            showError('#rspf', data);
          }
        },
        dataType: 'json'
      });
    }
  });
});
