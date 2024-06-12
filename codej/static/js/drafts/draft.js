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
  showDraft(slug, dt);
  if (window.localStorage.getItem('token')) {
    $('body').on('click', '#special-case', {slug: slug}, function(event) {
      $(this).blur();
      undressLinks(event.data.slug);
    });
    $('body').on('click', '#comments-state', {slug: slug}, function(event) {
      $(this).blur();
      changeDraft('commented', 'empty', event.data.slug);
    });
    $('body').on('change', '#select-status', {slug: slug}, function(event) {
      changeDraft('state', $('#select-status').val(), event.data.slug);
    });
    $('body').on('click', '#state-button', function() {
      $(this).blur();
      changeForm('#status-editor', '#select-status');
    });
    $('body').on('click', '.entity-text-block img', clickImage);
    $('body').on('click', '.edit-par', {slug: slug}, function(event) {
      $(this).blur();
      let par = $(this).parent().next();
      let num = $(this).data().num;
      let token = window.localStorage.getItem('token');
      let tee = token ? {'x-auth-token': token} : {};
      $.ajax({
        method: 'GET',
        url: '/api/send-par',
        headers: tee,
        data: {
          slug: event.data.slug,
          num: num
        },
        success: function(data) {
          if (data.text) {
            let d = {num: num, insert: 0, text: data.text};
            let html = Mustache.render($('#peditort').html(), d);
            par.after(html).slideUp('slow');
            $('#editor-opts').slideUp('slow');
            $('#paragraph-editor').slideDown('slow').css({'margin': 0});
            $('#options-block').slideUp('slow');
          } else {
            showError('.entity-text-block', data);
            $('#ealert').addClass('next-block');
            scrollPanel($('#ealert'));
          }
        },
        dataType: 'json'
      });
    });
    $('body')
    .on('keyup', '#paragraph-text-edit', {slug: slug}, function(event) {
      if (event.which == 13) {
        let val = $(this).val().trim();
        let insert = $(this).data().insert;
        let num = $(this).data().num;
        const F = '```';
        if (val.startsWith(F)) {
          if (val.indexOf(F, 1) >= 4) {
            val = val.slice(0, val.indexOf(F, 4)).trim() + '\n\n' + F;
            sendEdit(event.data.slug, num, insert, val, 1);
          }
        } else if (val) {
          sendEdit(event.data.slug, num, insert, val.replace('\n', ''), 0);
        }
      }
    });
    $('body').on('click', '#cancel-edit', function() {
      $(this).blur();
      if (!$('#paragraph-text-edit').data().insert) {
        $('#paragraph-editor').prev().slideDown('slow');
      }
      $('#paragraph-editor').slideUp('slow', function() { $(this).remove(); });
      $('#options-block').slideDown('slow');
    });
    $('body').on('click', '.add-before', {slug: slug}, function(event) {
      $(this).blur();
      let par = $(this).parent();
      let num = $(this).data().num;
      let html = Mustache.render($('#peditort').html(), {num: num, insert: 1});
      par.before(html).fadeOut('slow');
      $('#paragraph-editor').slideDown('slow').css({'margin': 0});
      $('#paragraph-text-edit').focus()
      $('#options-block').slideUp('slow');
    });
    $('body').on('click', '.remove-par', {slug: slug}, function(event) {
      $(this).blur();
      let num = $(this).data().num;
      $.ajax({
        method: 'DELETE',
        url: '/api/send-par',
        data: {
          auth: window.localStorage.getItem('token'),
          slug: event.data.slug,
          num: num
        },
        success: function(data) {
          if (data.done) {
            if (data.html) {
              $('.entity-text-block').empty()
                .append(data.html).data('len', data.length);
              parseDraft();
              $('#html-text-edit').val('');
            } else {
              window.location.reload();
            }
          } else {
            showError('.entity-text-block', data);
            $('#ealert').addClass('next-block');
            $('#editor-opts').remove()
            scrollPanel($('#ealert'));
          }
        },
        dataType: 'json'
      });
    });
    $('body').on('mouseleave', '.entity-text-block', function() {
      if (!$('#paragraph-editor').length) {
        $('#editor-opts').remove();
      }
    });
    $('body').on('mouseenter', '.editable', function() {
      if (!$('#paragraph-editor').length && !$('#p-block').length) {
        $('#editor-opts').remove();
        let th = $(this);
        let d = {num: th.data().num};
        let html = Mustache.render($('#eoptst').html(), d);
        if (th[0].nodeName === 'LI') {
          if (th.find('p').length) {
            th.find('p').before(html);
          } else {
            th.before(html);
          }
        } else {
          th.before(html);
        }
      }
    });
    $('body').on('click', '.copy-link', showCopyForm);
    $('body').on('keyup', '#html-text-edit', {slug: slug}, function(event) {
      let val = $(this).val().trim();
      if (event.which == 13) {
        const F = '```';
        if (val.startsWith(F)) {
          if (val.indexOf(F, 1) >= 4) {
            val = val.slice(0, val.indexOf(F, 4)).trim() + '\n\n' + F;
            sendPar(event.data.slug, val, 1);
          }
        } else if (val) {
          sendPar(event.data.slug, val.replace('\n', ''), 0);
        }
      }
    });
    $('body').on('click', '#summary-from-text', function() {
      $(this).blur();
      let l = $('.entity-text-block').children('p');
      let w = '';
      for (let n = 0; n < l.length && w.length < 512; n++) {
        w = w + ' ' + $(l[n]).text();
      }
      let t = w.trim().split(' ');
      let res = '';
      let i = 0;
      while ((res + '...').length <= 384 && i < t.length) {
        res = res + ' ' + t[i];
        i++;
      }
      $('#summary-edit').val(res.trim() + '...').trigger('blur');
    });
    $('body').on('click', '#summary-submit', {slug: slug}, function(event) {
      $(this).blur();
      if (!$('#summary-edit').parents('.form-group').hasClass('has-error')) {
        changeDraft('summary', $('#summary-edit').val(), event.data.slug);
      }
    });
    $('body').on(
      'keyup blur', '#summary-edit',
      {len: 512, marker: '#s-length-value', block: '#s-length-marker'},
      trackMarker);
    $('body').on('click', '#edit-summary', function() {
      $(this).blur();
      changeForm('#summary-editor', '#summary-edit');
    });
    $('body').on('click', '#title-submit', {slug: slug}, function(event) {
      $(this).blur();
      if (!$('.input-field').hasClass('has-error')) {
        changeDraft('title', $('#title').val(), event.data.slug);
      }
    });
    $('body').on(
      'keyup blur', '#title',
      {min: 3, max: 100, block: '.input-field'}, markInputError);
    $('body').on('click', '#edit-title', function() {
      $(this).blur();
      changeForm('#entity-title-editor', '#title');
    });
    $('body').on('click', '#metadesc-submit', {slug: slug}, function(event) {
      $(this).blur();
      if (!$('#metadesc-edit').parents('.form-group').hasClass('has-error')) {
        changeDraft('meta', $('#metadesc-edit').val(), event.data.slug);
      }
    });
    $('body').on(
      'keyup blur', '#metadesc-edit',
      {len: 180, marker: '#d-length-value', block: '#d-length-marker'},
      trackMarker);
    $('body').on('click', '#edit-metadesc', function() {
      $(this).blur();
      changeForm('#meta-description-editor', '#metadesc-edit');
    });
    $('body').on('click', '#labels-submit', {slug: slug}, function(event) {
      $(this).blur();
      let e = $('#labels-edit').parents('.form-group');
      if (!e.hasClass('has-error')) {
        $.ajax({
          method: 'PUT',
          url: '/api/labels',
          data: {
            auth: window.localStorage.getItem('token'),
            labels: $('#labels-edit').val().trim(),
            slug: event.data.slug
          },
          success: function(data) {
            if (data.labels) {
              window.location.reload();
            } else {
              showError('.editor-forms-block', data);
              $('#ealert').addClass('next-block');
            }
          },
          dataType: 'json'
        });
      }
    });
    $('body').on('keyup blur', '#labels-edit', function() {
      let g = $(this).parents('.form-group');
      g.removeClass('has-error');
      let c = $(this).val().split(',');
      for (let each in c) {
        each = $.trim(c[each]);
        if (each) {
          let re = /^[A-Za-zА-Яа-яЁё\d\-]{1,32}$/;
          if (!re.exec(each)) {
            g.addClass('has-error');
          }
        }
      }
    });
    $('body').on('click', '#labels-button', function() {
      $(this).blur();
      changeForm('#labels-editor', '#labels-edit');
    });
    $('body').on('click', '#move-screen-up', moveScreenUp);
  }
});
