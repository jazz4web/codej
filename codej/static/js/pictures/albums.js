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
    url: '/api/pictures',
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
        $('#main-container').removeClass('nonlisted').append(html);
        slidePage('#ealert');
      } else {
        let html = Mustache.render($('#albumst').html(), data);
        $('#main-container').append(html);
        let ust = Mustache.render($('#ustatt').html(), data);
        $('#right-panel').append(ust);
        formatDateTime($('.date-field'));
        if ($('.today-field').length) renderTF('.today-field', dt);
        if (data.pv) renderPV(data.pagination.page);
        if ($('.entity-pagination').length) {
          $('.entity-pagination').addClass('footer-bottom');
        }
        checkMC(1152);
        let pub = $('#pub-f');
        pub.on('change', function() {
          if ($(this).is(':checked')) {
            uncheckBox('#priv-f');
            uncheckBox('#ffo-f');
          } else {
            checkBox('#priv-f');
          }
        });
        let priv = $('#priv-f');
        priv.on('change', function() {
          if ($(this).is(':checked')) {
            uncheckBox('#pub-f');
            uncheckBox('#ffo-f');
          } else {
            checkBox('#pub-f');
          }
        });
        let ffo = $('#ffo-f');
        ffo.on('change', function() {
          if ($(this).is(':checked')) {
            uncheckBox('#pub-f');
            uncheckBox('#priv-f');
          } else {
            checkBox('#pub-f');
          }
        });
      }
    },
    dataType: 'json'
  });
  if (window.localStorage.getItem('token')) {
    checkIncomming();
    $('body').on('click', '#find-submit', function() {
      $(this).blur();
      let suffix = $('#find-input').val();
      let token = window.localStorage.getItem('token');
      let tee = token ? {'x-auth-token': token} : {};
      if (suffix) {
        $.ajax({
          method: 'GET',
          url: '/api/search',
          headers: tee,
          data: {
            suffix: suffix
          },
          success: function(data) {
            if (data.album) {
              window.location.assign(data.album);
            } else {
              let html = Mustache.render($('#ealertt').html(), data);
              $('#main-container').append(html);
              showError('#left-panel', data);
              scrollPanel($('#ealert'));
              checkMC(1152);
            }
          },
          dataType: 'json'
        });
      }
    });
    $('body').on('change', '#select-status', {suffix: null}, changeStatus);
    $('body').on('click', '#rename-album', {suffix: null}, renameAlbum);
    $('body').on(
      'keyup blur', '#title-change',
      {min: 3, max: 100, block: '#rename-form'},
      markInputError);
    $('body').on('click', '#show-rename-form', showRenameForm);
    $('body').on('click', '#show-state-form', showStateForm);
    $('body').on('click', '#album-first-page', function() {
      $(this).blur();
      window.location.assign('/pictures/');
    });
    $('body').on('click', '#user-home', function() {
      $(this).blur();
      let cform = $('#create-form-block');
      let fform = $('#find-pic-block');
      if (!cform.is(':hidden')) cform.slideUp('slow');
      if (!fform.is(':hidden')) fform.slideUp('slow');
      if ($('.clicked-item').length) {
        $('.clicked-item').removeClass('clicked-item');
        showUserStat();
      }
    });
    $('body').on('click', '.album-header-panel', function() {
      if (!$(this).hasClass('clicked-item')) {
        let cform = $('#create-form-block');
        let fform = $('#find-pic-block');
        if (!cform.is(':hidden')) cform.slideUp('slow');
        if (!fform.is(':hidden')) fform.slideUp('slow');
        $('.clicked-item').removeClass('clicked-item');
        $(this).addClass('clicked-item');
        showAlbumStat($(this).data().suffix);
      }
    });
    $('body').on('click', '.page-link', function(event) {
      event.preventDefault();
      let th = $(this).parent();
      if (!th.hasClass('active')) {
        window.location.assign('/pictures/?page=' + $(this).text().trim());
      }
    });
    $('body').on('click', '#next-link', {page: page}, function(event) {
      event.preventDefault();
      let p = event.data.page + 1;
      window.location.assign('/pictures/?page=' + p);
    });
    $('body').on('click', '#prev-link', {page: page}, function(event) {
      event.preventDefault();
      let p = event.data.page - 1;
      window.location.assign('/pictures/?page=' + p);
    });
    $('body').on('click', '.show-album', function() {
      $(this).blur();
      let url = '/pictures/' + $(this).data().dest;
      window.location.assign(url);
    });
    $('body').on('click', '#create-new', function() {
      $(this).blur();
      if (!$('#title-group').hasClass('has-error')) {
        $.ajax({
          method: 'POST',
          url: '/api/pictures',
          data: {
            auth: window.localStorage.getItem('token'),
            title: $('#title').val(),
            state: $('#create-form-block :checked').val()
          },
          success: function(data) {
            if (data.done) {
              window.location.replace(data.target);
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
    $('body').on('click', '#album-reload', reload);
    $('body').on('click', '#album-search', function() {
      $(this).blur();
      let cform = $('#create-form-block');
      let fblock = $('#find-pic-block');
      if (fblock.is(':hidden')) {
        if (!cform.is(':hidden')) cform.slideUp('slow');
        fblock.slideDown('slow', function() {
          scrollPanel($('.albums-options'));
          checkMC(1152);
        });
        if ($('.clicked-item').length) {
          $('.clicked-item').removeClass('clicked-item');
          showUserStat();
        }
      } else {
        fblock.slideUp('slow', function() { checkMC(1152); });
      }
    });
    $('body').on(
      'keyup blur', '#title', {min: 3, max: 100, block: '.form-group'},
      markInputError);
    $('body').on('click', '#create-new-album', function() {
      $(this).blur();
      let cform = $('#create-form-block');
      let fblock = $('#find-pic-block');
      if (cform.is(':hidden')) {
        if (!fblock.is(':hidden')) fblock.slideUp('slow');
        cform.slideDown('slow', function() {
          if (!fblock.is(':hidden')) fblock.slideUp('slow');
          $('#title').focus();
          scrollPanel($('.albums-options'));
          checkMC(1152);
        });
        if ($('.clicked-item').length) {
          $('.clicked-item').removeClass('clicked-item');
          showUserStat();
        }
      } else {
        cform.slideUp('slow', function() { checkMC(1152); });
      }
    });
  }
});
