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
      console.log(data);
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
      }
    },
    dataType: 'json'
  });
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
});
