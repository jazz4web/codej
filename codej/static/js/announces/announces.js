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
    url: '/api/announces',
    headers: tee,
    data: {
      page: page
    },
    success: function(data) {
      if (data.message) {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#main-container').append(html);
        slidePage('#ealert');
      } else {
        let html = Mustache.render($('#announcest').html(), data);
        $('#main-container').append(html);
        if ($('.today-field').length) renderTF('.today-field', dt);
        $('.entity-block').each(checkNext);
        $('.date-field').each(function() { formatDateTime($(this)); });
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
    checkIncomming();
    $('body').on('click', '.page-link', function(event) {
      event.preventDefault();
      let th = $(this).parent();
      if (!th.hasClass('active')) {
        window.location.assign('/announces/?page=' + $(this).text().trim());
      }
    });
    $('body').on('click', '#next-link', {page: page}, function(event) {
      event.preventDefault();
      let p = event.data.page + 1;
      window.location.assign('/announces/?page=' + p);
    });
    $('body').on('click', '#prev-link', {page: page}, function(event) {
      event.preventDefault();
      let p = event.data.page - 1;
      window.location.assign('/announces/?page=' + p);
    });
    $('body').on('click', '.title-link', function(event) {
      event.stopPropagation();
    });
    $('body').on('click', '.entity-text-block img', clickImage);
    $('body').on('click', '.slidable', slideBlock);
    $('body').on('blur', '#body', blurBodyAn);
    $('body').on(
      'keyup blur', '#headline',
      {min: 3, max: 50, block: '.form-headline-group'}, markInputError);
    $('body').on(
      'keyup', '#body',
      {len: 1024, marker: '#length-marker', block: '.length-marker'},
      trackMarker);
    $('body').on('click', '#submit', function() {
      $(this).blur();
      $('#headline').trigger('blur');
      $('#body').trigger('blur');
      let head = $('.form-headline-group');
      let body = $('.form-group');
      if (!head.hasClass('has-error') && !body.hasClass('has-error')) {
        $.ajax({
          method: 'POST',
          url: '/api/announces',
          data: {
            'title': $('#headline').val(),
            'text': $('#body').val(),
            'heap': $('#heap').is(':checked') ? 1 : 0,
            'auth': window.localStorage.getItem('token')
          },
          success: function(data) {
            if (data.announce) {
              window.location.assign(data.announce);
            } else {
              let html = Mustache.render($('#ealertt').html(), data);
              $('#main-container').append(html);
              showError('#new-title', data);
              scrollPanel($('#ealert'));
            }
          },
          dataType: 'json'
        });
      }
    });
  }
});
