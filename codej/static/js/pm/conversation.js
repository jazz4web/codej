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
    url: '/api/conv',
    headers: tee,
    data: {
      username: username,
      page: page,
      nopage: nopage
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
        let html = Mustache.render($('#convt').html(), data);
        $('#main-container').append(html);
        if ($('.today-field').length) renderTF('.today-field', dt);
        $('.entity-block').each(checkNext);
        $('.date-field').each(function() { formatDateTime($(this)); });
        if (data.incomming) scrollPanel($('.last-pm'));
        if (!data.pagination.next && data.pagination.messages) {
          for (let i = 0; i < data.pagination.messages.length; i++) {
            let message = data.pagination.messages[i];
            if (i == data.pagination.messages.length - 1) {
              html = '<button type="button"' +
                     '        title="обновить страницу"' +
                     '        class="btn btn-sm btn-default reload-button">' +
                     '  <span class="glyphicon glyphicon-refresh"' +
                     '        aria-hidden="true"></span>' +
                     '</button>';
              $('.last-pm .pm-options').append(html);
              if (message.author_username == data.cu.username) {
                if (message.received) {
                  html = '<button type="button"' +
                         '        title="новое сообщение"' +
                         '    class="btn btn-sm btn-primary new-pm-button">' +
                    '<span class="glyphicon glyphicon-edit"' +
                    '      aria-hidden="true"></span>' +
                         '</button>';
                  $('.last-pm .pm-options').prepend(html);
                } else {
                  html = '<button type="button"' +
                         '        title="редактировать"' +
                         '        data-id="' + message.id + '"' +
                         '        class="btn btn-sm btn-danger edit-button">' +
                    '<span class="glyphicon glyphicon-edit"' +
                    '      aria-hidden="true"></span>' +
                         '</button>';
                  $('.last-pm .pm-options').prepend(html);
                };
              } else {
                html = '<button type="button"' +
                       '        title="ответить"' +
                       '    class="btn btn-sm btn-primary new-pm-button">' +
                  '<span class="glyphicon glyphicon-edit"' +
                  '      aria-hidden="true"></span>' +
                       '</button>';
                $('.last-pm .pm-options').prepend(html);
              }
            }
          }
        }
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
    $('body').on('click', '.entity-text-block img', clickImage);
    $('body').on('click', '.page-link', function(event) {
      event.preventDefault();
      let th = $(this).parent();
      if (!th.hasClass('active')) {
        window.location.assign(
          '/pm/' + username + '/?page=' + $(this).text().trim());
      }
    });
    $('body').on('click', '#next-link', {page: page}, function(event) {
      event.preventDefault();
      let p = event.data.page + 1;
      window.location.assign('/pm/' + username + '?page=' + p);
    });
    $('body').on('click', '#prev-link', {page: page}, function(event) {
      event.preventDefault();
      let p;
      if (!parseInt(nopage)) {
        p = parseInt($('.pagination .active .page-link').text()) - 1;
      } else {
        p = event.data.page - 1;
      }
      window.location.assign('/pm/' + username + '?page=' + p);
    });
    $('body').on('click', '#pm-editor-submit', function() {
      $(this).blur();
      let val = $('#pm-editor-edit').val();
      let mid = $(this).data().id;
      if (val) {
        $.ajax({
          method: 'PATCH',
          url: '/api/conv',
          data: {
            text: val,
            mid: mid,
            auth: window.localStorage.getItem('token')
          },
          success: function(data) {
            if (data.done) {
              window.location.reload();
            } else {
              let html = Mustache.render($('#ealertt').html(), data);
              $('#main-container').append(html);
              showError('#edit-message', data);
              scrollPanel($('#ealert'));
            }
          },
          dataType: 'json'
        });
      }
    });
    $('body').on('click', '#cancel-edit', function() {
      $(this).blur();
      window.location.reload();
    });
    $('body').on('click', '.edit-button', function() {
      $(this).blur();
      if (!$('#edit-message').length) {
        $.ajax({
          method: 'PUT',
          url: '/api/conv',
          data: {
            auth: window.localStorage.getItem('token'),
            mid: $(this).data().id
          },
          success: function(data) {
            if (data.done) {
              if (data.update) window.location.reload();
              if (data.text) {
                let dt = luxon.DateTime.now();
                let html = Mustache.render($('#editpmt').html(), data);
                $('.last-pm').after(html);
                $('#edit-message').slideDown('slow', function() {
                  scrollPanel($('#edit-message'));
                });
                if ($('.today-field').length) renderTF('.today-field', dt);
              }
            } else {
              let html = Mustache.render($('#ealertt').html(), data);
              $('#main-container').append(html);
              showError('.last-pm', data);
              scrollPanel($('#ealert'));
            }
          },
          dataType: 'json'
        });
      }
    });
    $('body').on('click', '.reload-button', function() {
      $(this).blur();
      window.location.reload();
    });
    $('body').on('click', '.new-pm-button', function() {
      $(this).blur();
      let fblock = $('#new-message');
      if (fblock.is(':hidden')) {
        fblock.slideDown('slow', function() {
          scrollPanel($('.last-pm'));
          checkMC(860);
        });
      } else {
        fblock.slideUp('slow', function() {
          checkMC(860);
        });
      }
    });
    $('body').on('click', '#pm-submit', function() {
      $(this).blur();
      let text = $('#pm-editor').val();
      if (text) {
        $.ajax({
          method: 'POST',
          url: '/api/conv',
          data: {
            recipient: username,
            auth: window.localStorage.getItem('token'),
            message: text
          },
          success: function(data) {
            if (data.done) {
              window.location.reload();
            } else {
              let html = Mustache.render($('#ealertt').html(), data);
              $('#main-container').append(html);
              showError('#new-message', data);
              scrollPanel($('#ealert'));
            }
          },
          dataType: 'json'
        });
      }
    });
  }
});
