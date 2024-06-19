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
    url: '/api/announce',
    headers: tee,
    data: {
      suffix: suffix
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
        $('title').text(
          $('title').text().trim() + ' ' + data.announce.headline);
        let html = Mustache.render($('#announcet').html(), data);
        $('#main-container').append(html);
        $('.date-field').each(function() { formatDateTime($(this)); });
        checkMC(860);
        $('.entity-text-block iframe'). each(adjustFrame);
        $('.entity-text-block').children().each(setMargin);
        $('.entity-text-block img').each(adjustImage);
      }
    },
    dataType: 'json'
  });
  if (token) {
    $('body').on('click', '#remove-button', function() {
      $(this).blur();
      $.ajax({
        method: 'DELETE',
        url: '/api/announce',
        data: {
          suffix: suffix,
          auth: window.localStorage.getItem('token')
        },
        success: function(data) {
          if (data.done) {
            window.location.replace(data.redirect);
          } else {
            showError('.ann-block', data);
            scrollPanel($('#ealert'));
          }
        },
        dataType: 'json'
      });
    })
    $('body').on('click', '#state-button', function() {
      $(this).blur();
      changeAnn('pub', 0, suffix);
    });
    $('body').on('click', '#headline-submit', function() {
      $(this).blur();
      let value = $('#headline').val();
      if (!$('.input-field').hasClass('has-error')) {
        changeAnn('headline', value, suffix);
      }
    });
    $('body').on('click', '#text-submit', function() {
      $(this).blur();
      if (!$('#text-editor .form-group').hasClass('has-error')) {
        let value = $('#text-edit').val();
        changeAnn('body', value, suffix);
      }
    });
    $('body').on(
      'keyup blur', '#headline',
      {min: 3, max: 50, block: '.input-field'}, markInputError);
    $('body').on('click', '#trash-button', function() {
      $(this).blur();
      if ($('.editor-forms-block').is(':hidden')) {
        $('#remove-button-form').slideDown('fast', function() {
          $('.editor-forms-block').slideDown('slow');
          scrollPanel($('.editor-forms-block'));
        });
      } else {
        if ($('#remove-button-form').is(':hidden')) {
          let f = $('#remove-button-form');
          f.siblings().each(function() {
            $(this).slideUp('slow');
          });
          f.slideDown('slow');
          scrollPanel($('.editor-forms-block'));
        } else {
          $('.editor-forms-block').slideUp('slow', function() {
            $('#remove-button-form').slideUp('fast');
          });
        }
      }
    });
    $('body').on('click', '#edit-headline', function() {
      $(this).blur();
      if ($('.editor-forms-block').is(':hidden')) {
        $('#headline-editor').slideDown('fast', function() {
          $('.editor-forms-block').slideDown('slow');
          scrollPanel($('.editor-forms-block'));
        });
      } else {
        if ($('#headline-editor').is(':hidden')) {
          let f = $('#headline-editor');
          f.siblings().each(function() {
            $(this).slideUp('slow');
          });
          f.slideDown('slow');
          scrollPanel($('.editor-forms-block'));
        } else {
          $('.editor-forms-block').slideUp('slow', function() {
            $('#headline-editor').slideUp('fast');
          });
        }
      }
    });
    $('body').on('click', '#edit-text-button', function() {
      $(this).blur();
      if ($('.editor-forms-block').is(':hidden')) {
        $('#text-editor').slideDown('fast', function() {
          $('.editor-forms-block').slideDown('slow');
          scrollPanel($('.editor-forms-block'));
        });
      } else {
        if ($('#text-editor').is(':hidden')) {
          let f = $('#text-editor');
          f.siblings().each(function() {
            $(this).slideUp('slow');
          });
          f.slideDown('slow');
          scrollPanel($('.editor-forms-block'));
        } else {
          $('.editor-forms-block').slideUp('slow', function() {
            $('#text-editor').slideUp('fast');
          });
        }
      }
    });
    $('body').on('blur', '#text-edit', blurBodyAn);
    $('body').on(
      'keyup', '#text-edit',
      {len: 1024, marker: '#length-marker', block: '.length-marker'},
      trackMarker);
    $('body').on('click', '.entity-text-block img', clickImage);
    $('body').on('click', '#go-home', function() {
      $(this).blur();
      window.location.assign('/announces/');
    });
  }
});
