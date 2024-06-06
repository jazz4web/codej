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
    url: '/api/aliases',
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
        let html = Mustache.render($('#aliasest').html(), data);
        $('#main-container').append(html);
        if ($('.today-field').length) renderTF('.today-field', dt);
        $('.entity-block').each(checkNext);
        $('.date-field').each(function() { formatDateTime($(this)); });
        $('.copy-button').on('click', copyAlias);
        renderPV(data.pagination.page);
        checkMC(860);
      }
    },
    dataType: 'json'
  });
  if (window.localStorage.getItem('token')) {
    $('body').on('click', '.page-link', function(event) {
      event.preventDefault();
      let th = $(this).parent();
      if (!th.hasClass('active')) {
        window.location.assign('/aliases/?page=' + $(this).text().trim());
      }
    });
    $('body').on('click', '#next-link', {page: page}, function(event) {
      event.preventDefault();
      let p = event.data.page + 1;
      window.location.assign('/aliases/?page=' + p);
    });
    $('body').on('click', '#prev-link', {page: page}, function(event) {
      event.preventDefault();
      let p = event.data.page - 1;
      window.location.assign('/aliases/?page=' + p);
    });
    $('body').on('keyup', '#link', function(event) {
      if (event.which == 13) $('#link-submit').trigger('click');
    });
    $('body').on('click', '#link-submit', function() {
      $(this).blur();
      let link = $('#link').val();
      if (link.startsWith('https://') || link.startsWith('http://')) {
        $.ajax({
          method: 'POST',
          url: '/api/aliases',
          data: {
            link: link,
            auth: window.localStorage.getItem('token')
          },
          success: function(data) {
            if (data.done) {
              if (data.alias) {
                $('.found-alias').remove();
                let html = Mustache.render($('#aliast').html(), data.alias);
                $('#new-title').after(html);
                formatDateTime($('.found-alias .date-field'));
                $('#link').val('');
                let b = '#alias-' + data.alias.suffix;
                $(b).on('click', copyAlias);
                checkMC(860);
              } else {
                window.location.reload();
              }
            } else {
              let html = Mustache.render($('#ealertt').html(), data);
              $('#main-container').append(html);
              showError('#new-title', data);
            }
          },
          dataType: 'json'
        });
      }
    });
  }
});
