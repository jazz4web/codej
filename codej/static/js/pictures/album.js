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
    url: '/api/pictures/' + suffix,
    data: {
      page: page
    },
    headers: tee,
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
        $('#main-container').removeClass('nonlisted').append(html);
        slidePage('#ealert');
      } else {
        let html = Mustache.render($('#albumt').html(), data);
        $('#main-container').append(html);
        let ast = Mustache.render($('#astatt').html(), data);
        $('#right-panel').append(ast);
        if ($('.today-field').length) renderTF('.today-field', dt);
        formatDateTime($('.date-field'));
        $('#progress-block').hide();
        renderPV(data.pagination.page);
        if ($('.entity-pagination').length) {
          $('.entity-pagination').addClass('footer-bottom');
        }
        let s = $('#select-status option');
        for (let n = 0; n < s.length; n++) {
          if (s[n].value == data.album.state) {
            $(s[n]).attr('selected', 'selected');
          }
        }
        checkMC(1152);
      }
    },
    dataType: 'json'
  });
  if (window.localStorage.getItem('token')) {
    $('body').on('change', '#image', {suffix: suffix}, function(event) {
      $('#ealert').remove();
      $('#upload-form-block').slideUp('slow', function() {
        $('#progress-block').slideDown('slow');
      });
      let file = $(this)[0].files[0];
      if (file.size <= 5 * 1024 * 1024) {
        let fd = new FormData($('#uploadform')[0]);
        fd.append('token', window.localStorage.getItem('token'));
        $.ajax({
          method: 'POST',
          url: '/api/pictures/' + event.data.suffix,
          processData: false,
          contentType: false,
          cache: false,
          data: fd,
          success: function(data) {
            if (data.done) {
              window.location.reload();
            } else {
              if ($('.top-flashed-block').length) {
                $('.top-flashed-block').remove();
              }
              showError('#left-panel', data);
              scrollPanel($('#ealert'));
              $('#upload-form-block').slideDown('slow', function() {
                $('#progress-block').slideUp('slow');
              });
            }
          },
          dataType: 'json'
        });
      } else {
        let d = {message: 'Недопустимый размер файла.'};
        if ($('.top-flashed-block').length) $('.top-flashed-block').remove();
        showError('#left-panel', d);
        $('#upload-form-block').slideDown('slow', function() {
          $('#progress-block').slideUp('slow');
        });
      }
    });
  }
});
