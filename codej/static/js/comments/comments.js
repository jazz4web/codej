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
    url: '/api/comments',
    headers: tee,
    data: {
      page: page
    },
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
        let html = Mustache.render($('#commentst').html(), data);
        $('#main-container').append(html);
        if ($('.today-field').length) renderTF('.today-field', dt);
        $('.entity-block').each(checkNext);
        $('.date-field').each(function() {formatDateTime($(this)); });
        if (data.pv) renderPV(data.pagination.page);
        checkMC(860);
        $('.entity-text-block iframe').each(adjustFrame);
        $('.entity-text-block').children().each(setMargin);
        $('.entity-text-block img').each(adjustImage);
      }
    },
    dataType: 'json'
  });
  if (token) {
    $('body').on('click', '.remove-button', function() {
      $(this).blur();
      let par = $(this).parents('.commentary-options');
      $.ajax({
        method: 'DELETE',
        url: '/api/comment',
        data: {
          auth: window.localStorage.getItem('token'),
          cid: $(this).data().id
        },
        success: function(data) {
          if (data.done) {
            window.location.assign('/comments/');
          } else {
            showError(par, data);
          }
        },
        dataType: 'json'
      });
    });
    $('body').on('click', '.trash-button', function() {
      $(this).blur();
      showHideButton($(this), '.remove-button');
    });
    $('body').on('click', '.checked-button', function() {
      $(this).blur();
      let par = $(this).parents('.commentary-options');
      $.ajax({
        method: 'PUT',
        url: '/api/comment',
        data: {
          id: $(this).data().id,
          auth: window.localStorage.getItem('token')
        },
        success: function(data) {
          if (data.done) {
            window.location.assign('/comments/');
          } else {
            showError(par, data);
          }
        },
        dataType: 'json'
      });
    });
    $('body').on('click', '.link-button', function() {
      $(this).blur();
      window.open($(this).data().art, '_blank');
    });
    $('body').on('click', '.page-link', function(event) {
      event.preventDefault();
      let th = $(this).parent();
      if (!th.hasClass('active')) {
        window.location.assign('/comments/?page=' + $(this).text().trim());
      }
    });
    $('body').on('click', '#next-link', {page: page}, function(event) {
      event.preventDefault();
      let p = event.data.page + 1;
      window.location.assign('/comments/?page=' + p);
    });
    $('body').on('click', '#prev-link', {page: page}, function(event) {
      event.preventDefault();
      let p = event.data.page - 1;
      window.location.assign('/comments/?page=' + p);
    });

  }
});
