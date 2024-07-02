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
  let token = window.localStorage.getItem('token');
  let tee = token ? {'x-auth-token': token} : {};
  $.ajax({
    method: 'GET',
    url: '/api/profile',
    headers: tee,
    data: {
      username: username
    },
    success: function(data) {
      if (token) {
        if (!data.cu || data.cu.brkey != checkBrowser()) {
          window.localStorage.removeItem('token');
          window.location.replace('/');
        }
      }
      if (data.message) {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#main-container').append(html);
        slidePage('#ealert');
      } else {
        let html = Mustache.render($('#profilet').html(), data);
        $('#main-container').append(html);
        formatDateTime($('#profile .date-field'));
        renderLastSeen($('#profile .last-seen'));
        if ($('.today-field').length) renderTF('.today-field', dt);
        checkMC(860);
        if (!data.user.description) {
          $('#length-marker').text(500);
        } else {
          $('#length-marker').text(500 - data.user.description.length);
        }
        if ($('#select-group').length) {
          let s = $('#select-group option');
          for (let n = 0; n < s.length; n++) {
            if (s[n].value == data.user.group) {
              $(s[n]).attr('selected', 'selected');
          }
        }
        }
      }
    },
    dataType: 'json'
  });
  if (window.localStorage.getItem('token')) {
    checkIncomming();
    $('body').on('click', '#pm-message', function() {
      $(this).blur();
      window.location.assign($(this).data().url);
    });
    $('body').on('click', '#make-friend', function() {
      $(this).blur();
      $.ajax({
        method: 'POST',
        url: '/api/rel',
        data: {
          auth: window.localStorage.getItem('token'),
          uid: $(this).data().uid
        },
        success: function(data) {
          if (data.done) {
            window.location.reload();
          } else {
            showError('#profile', data);
            scrollPanel($('#ealert'));
          }
        },
        dataType: 'json'
      });
    });
    $('body').on('change', '#select-group', function() {
      let res = $(this).val();
      $.ajax({
        method: 'POST',
        url: '/api/profile',
        data: {
          group: res,
          username: username,
          auth: window.localStorage.getItem('token')
        },
        success: function(data) {
          if (data.done) {
            window.location.reload();
          } else {
            showError('#permissions', data)
            $('#ealert').addClass('next-block');
            scrollPanel($('#ealert'));
            setTimeout(function() { checkMC(860);}, 300)
          }
        },
        dataType: 'json'
      });
    });
  }
  if (cu === username) {
    $('body').on('click', '#chaddress-submit', function() {
      $(this).blur();
      let tee = {
        address: $('#chaddress').val(),
        passwd: $('#chapasswd').val(),
        auth: window.localStorage.getItem('token')
      };
      if (tee.address && tee.passwd && tee.auth) {
        $.ajax({
          method: 'POST',
          url: '/api/request-email-change',
          data: tee,
          success: function(data) {
            if (data.done) {
              window.location.assign('/');
            } else {
              showError('#profile', data);
              scrollPanel($('#ealert'));
            }
          },
          dataType: 'json'
        });
      }
    });
    $('body').on('click', '#changepwd-submit', function() {
      $(this).blur();
      let tee = {
        passwd: $('#curpwd').val(),
        newpwd: $('#newpwd').val(),
        confirma: $('#newpwdconfirm').val(),
        auth: window.localStorage.getItem('token')
      };
      if (tee.passwd && tee.newpwd && tee.confirma && tee.auth) {
        $.ajax({
          method: 'POST',
          url: '/api/change-passwd',
          data: tee,
          success: function(data) {
            if (data.done) {
              window.location.assign('/');
            } else {
              showError('#profile', data);
              scrollPanel($('#ealert'));
            }
          },
          dataType: 'json'
        });
      }
    });
    $('body').on('change', '#image', function() {
      $('#ealert').remove();
      let file = $(this)[0].files[0];
      if (file.size <= 204800) {
        let fd = new FormData($('#ava-form')[0]);
        fd.append('token', window.localStorage.getItem('token'));
        $.ajax({
          method: 'POST',
          url: '/api/change-ava',
          processData: false,
          contentType: false,
          cache: false,
          data: fd,
          success: function(data) {
            if (data.done) {
              window.location.reload();
            } else {
              showError('#profile', data);
              scrollPanel($('#ealert'));
            }
          },
          dataType: 'json'
        });
      } else {
        let d = {message: 'Недопустимый размер файла.'};
        showError('#profile', d);
        scrollPanel($('#ealert'));
      }
    });
    $('body').on('click', '#emchange', function() {
      $(this).blur();
      let em = $('#changeemf');
      if (em.is(':hidden')) {
        $('#changeavaf').slideUp('slow');
        $('#changepwdf').slideUp('slow');
        em.slideDown('slow', function() {
          scrollPanel(em);
          checkMC(860);
        });
      } else {
        em.slideUp('slow', function() {
          checkMC(860);
        });
      }
    });
    $('body').on('click', '#changepwd', function() {
      $(this).blur();
      let pwd = $('#changepwdf');
      if (pwd.is(':hidden')) {
        $('#changeavaf').slideUp('slow');
        $('#changeemf').slideUp('slow');
        pwd.slideDown('slow', function() {
          scrollPanel(pwd);
          checkMC(860);
        });
      } else {
        pwd.slideUp('slow', function() {
          checkMC(860);
        });
      }
    });
    $('body').on('click', '#changeava', function() {
      $(this).blur();
      let ava = $('#changeavaf');
      if (ava.is(':hidden')) {
        $('#changepwdf').slideUp('slow');
        $('#changeemf').slideUp('slow');
        ava.slideDown('slow', function() {
          scrollPanel(ava);
          checkMC(860);
        });
      } else {
        ava.slideUp('slow', function() {
          checkMC(860);
        });
      }
    });
    $('body').on('click', '#fix-description', function() {
      $(this).blur();
      $(this).parents('.description-block').slideUp('slow');
      let editor = $('#description-e');
      editor.slideDown('slow', function() { scrollPanel(editor); });
      $('#description-editor').focus();
    });
    $('body').on('click', '#cancel-description', function() {
      $(this).blur();
      $(this).parents('#description-e').slideUp('slow');
      let description = $('.description-block');
      description.slideDown('slow', function() { scrollPanel(description); });
    });
    $('body').on(
      'keyup', '#description-editor',
      {len: 500, marker: '#length-marker', block: '.length-marker'},
      trackMarker);
    $('body').on('click', '#description-submit', function() {
      $(this).blur();
      if (!$('#description-editor').parents('.form-group')
                                   .hasClass('has-error')) {
        $.ajax({
          method: 'PUT',
          url: '/api/profile',
          data: {
            auth: window.localStorage.getItem('token'),
            text: $('#description-editor').val()
          },
          success: function(data) {
            if (data.done) {
              window.location.reload();
            } else {
              showError('#profile', data);
              scrollPanel($('#ealert'));
            }
          },
          dataType: 'json'
        });
      }
    });
  }
});
