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
    url: '/api/admin-tools',
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
        slidePage('#ealert');
      } else {
        let html = Mustache.render($('#toolst').html(), data);
        $('#main-container').append(html);
        checkMC(860);
        let s = $('#select-group option');
        for (let n = 0; n < s.length; n++) {
          if (s[n].value == data.dgroup) {
            $(s[n]).attr('selected', 'selected');
          }
        }
      }
    },
    dataType: 'json'
  });
  if (token) {
    $('body').on('click', '#robots-submit', function() {
      $(this).blur();
      $.ajax({
        method: 'PUT',
        url: '/api/chrobots',
        data: {
          auth: window.localStorage.getItem('token'),
          value: $('#reditor').val()
        },
        success: function(data) {
          if (data.done) {
            window.location.assign('/robots.txt');
          } else {
            showError('.editor-forms-block', data);
            scrollPanel($('#ealert'));
          }
        },
        dataType: 'json'
      });
    });
    $('body').on('click', '#user-submit', function() {
      $(this).blur();
      let tee = {
        username: $('#username').val(),
        address: $('#address').val(),
        password: $('#password').val(),
        confirma: $('#confirmation').val(),
        auth: window.localStorage.getItem('token')
      };
      if (tee.username && tee.address && tee.password && tee.confirma) {
        $.ajax({
          method: 'POST',
          url: '/api/admin-tools',
          data: tee,
          success: function(data) {
            if (data.done) {
              window.location.assign(data.redirect);
            } else {
              showError('.editor-forms-block', data);
              scrollPanel($('#ealert'));
            }
          },
          dataType: 'json'
        });
      }
    });
    $('body').on('click', '#select-group', function() {
      let res = $(this).val();
      $.ajax({
        method: 'PUT',
        url: '/api/chdgroup',
        data: {
          dgroup: res,
          auth: window.localStorage.getItem('token')
        },
        success: function(data) {
          if (data.done) {
            window.location.reload();
          } else {
            showError('#permissions', data);
            scrollPanel($('#ealert'));
          }
        },
        dataType: 'json'
      });
    });
    $('body').on('click', '#edit-perms', function() {
      $(this).blur();
      let p = $('#default-perms-editor');
      if (p.is(':hidden')) {
        p.siblings().each(function() {
          if (!$(this).is(':hidden')) $(this).slideUp('slow');
        });
        p.slideDown('slow');
      }
    });
    $('body').on('click', '#create-user', function() {
      $(this).blur();
      let p = $('#new-user-editor');
      if (p.is(':hidden')) {
        p.siblings().each(function() {
          if (!$(this).is(':hidden')) $(this).slideUp('slow');
        });
        p.slideDown('slow');
      }
    });
    $('body').on('click', '#edit-li-stat', function() {
      $(this).blur();
      let l = $('#li-editor');
      if (l.is(':hidden')) {
        l.siblings().each(function() {
          if (!$(this).is(':hidden')) $(this).slideUp('slow');
        });
        l.slideDown('slow');
      }
    });
    $('body').on('click', '#edit-index', function() {
      $(this).blur();
      let i = $('#index-editor');
      if (i.is(':hidden')) {
        i.siblings().each(function() {
          if (!$(this).is(':hidden')) $(this).slideUp('slow');
        });
        i.slideDown('slow');
      }
    });
    $('body').on('click', '#edit-robots', function() {
      $(this).blur();
      let r = $('#robots-editor');
      if (r.is(':hidden')) {
        r.siblings().each(function() {
          if (!$(this).is(':hidden')) $(this).slideUp('slow');
        });
        r.slideDown('slow');
      }
    });

  }
});
