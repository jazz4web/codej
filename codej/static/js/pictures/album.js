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
        if (data.pagination) renderPV(data.pagination.page);
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
    $('body')
      .on('click', '.remove-button', {page: page, suffix: suffix}, removeThis);
    $('body').on('click', '.trash-button', function() {
      $(this).blur();
      let alb = $(this).parents('.album-tools-panel')
                       .siblings('.album-header-panel');
      if (alb.hasClass('clicked-item')) {
        showHideButton($(this), '.remove-button');
      }
    });
    $('body').on('change', '#select-status', {suffix: suffix}, changeStatus);
    $('body').on('click', '#rename-album', {suffix: suffix}, renameAlbum);
    $('body').on(
      'keyup blur', '#title-change',
      {min: 3, max: 100, block: '#rename-form'},
      markInputError);
    $('body').on('click', '#show-rename-form', showRenameForm);
    $('body').on('click', '#show-state-form', showStateForm);
    $('body').on('click', '.copy-md-code', function() {
      $(this).blur();
      $('.remove-button').each(function() { $(this).fadeOut('slow'); });
      let sf = $('.album-form-b');
      let ff = $('.album-form');
      if (sf.is(':hidden')) {
        sf.slideDown('slow');
        ff.slideUp('slow');
      } else {
        sf.slideUp('slow');
      }
    });
    $('body').on('click', '.copy-link', function() {
      $(this).blur();
      $('.remove-button').each(function() { $(this).fadeOut('slow'); });
      let ff = $('.album-form');
      let sf = $('.album-form-b');
      if (ff.is(':hidden')) {
        ff.slideDown('slow');
        sf.slideUp('slow');
      } else {
        ff.slideUp('slow');
      }
    });
    $('body')
    .on('click', '#album-first-page', {suffix: suffix}, function(event) {
      $(this).blur();
      window.location.assign('/pictures/' + event.data.suffix);
    });
    $('body').on('click', '.album-header-panel', function() {
      if (!$(this).hasClass('clicked-item')) {
        let form = $('#create-form-block');
        if (!form.is(':hidden')) form.slideUp('slow');
        $('.clicked-item').removeClass('clicked-item');
        $('.remove-button').each(function() { $(this).fadeOut('slow'); });
        $(this).addClass('clicked-item');
        let token = window.localStorage.getItem('token');
        let tee = token ? {'x-auth-token': token} : {};
        $.ajax({
          method: 'GET',
          url: '/api/picstat',
          headers: tee,
          data: {
            suffix: $(this).data().suffix
          },
          success: function(data) {
            if (data.picture) {
              let html = Mustache.render($('#picturet').html(), data);
              $('#right-panel').empty().append(html);
              formatDateTime($('.date-field'));
              checkMC(1152);
              let block_width = parseInt($('.album-statistic').width());
              let pic_width = parseInt($('.picture-body img').attr('width'));
              if (pic_width >= block_width) {
                let pic_height = parseInt($('.picture-body img')
                                          .attr('height'));
                let width = block_width - 4;
                let height = Math.round(pic_height / (pic_width / width));
                $('.picture-body img').attr({
                  "width": width, "height": height
                });
              }
              $('#copy-button').on('click', {cls: '.album-form'}, copyThis);
              $('#copy-button-b')
                .on('click', {cls: '.album-form-b'}, copyThis);
            } else {
              let html = Mustache.render($('#ealertt').html(), data);
              $('#main-container').append(html);
              showError('#left-panel', data);
              scrollPanel($('#ealert'));
            }
          },
          dataType: 'json'
        });
      }
    });
    $('body').on('click', '#go-home', function() {
      $(this).blur();
      window.location.assign('/pictures/');
    });
    $('body')
    .on('click', '#show-statistic', {suffix: suffix}, function(event) {
      $(this).blur();
      let form = $('#create-form-block');
      if (!form.is(':hidden')) form.slideUp('slow');
      if ($('.clicked-item').length) {
        $('.clicked-item').removeClass('clicked-item');
        $('.remove-button').each(function() { $(this).fadeOut('slow'); });
        showAlbumStat(event.data.suffix);
      }
    });
    $('body').on('click', '#album-reload', reload);
    $('body').on('click', '#upload-new', {suffix: suffix}, function(event) {
      $(this).blur();
      let upblock = $('#create-form-block');
      if (!upblock.is(':hidden')) {
        upblock.slideUp('slow');
      } else {
        if ($('.clicked-item').length) {
          $('.clicked-item').removeClass('clicked-item');
          $('.remove-button').each(function() { $(this).fadeOut('slow'); });
          showAlbumStat(event.data.suffix);
        }
        upblock.slideDown('slow');
        scrollPanel($('.albums-options'));
      }
    });
    $('body').on('click', '.page-link', {suffix: suffix}, function(event) {
      event.preventDefault();
      window.location.assign(
        '/pictures/' + event.data.suffix + '?page=' + $(this).text().trim());
    });
    $('body')
    .on('click', '#next-link', {page: page, suffix: suffix}, function(event) {
      event.preventDefault();
      let p = event.data.page + 1;
      window.location.assign('/pictures/' + event.data.suffix + '?page=' + p);
    });
    $('body')
    .on('click', '#prev-link', {page: page, suffix: suffix}, function(event) {
      event.preventDefault();
      let p = event.data.page - 1;
      window.location.assign('/pictures/' + event.data.suffix + '?page=' + p);
    });
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
