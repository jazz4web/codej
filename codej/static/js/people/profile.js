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
