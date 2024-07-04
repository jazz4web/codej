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
  $('body').on('click', '.copy-link', showCopyForm);
  $('body').on('click', '.entity-text-block img', clickImage);
  $('body').on('click', '#move-screen-up', moveScreenUp);
  showArt('/api/art', slug, dt);
  $('body').on('click', '#cancel-answer', function() {
    $(this).blur();
    let nab = $('.new-answer-block');
    nab.slideUp('slow', function() {
      nab.remove();
    });
  });
  $('body').on('click', '.answer-button', function() {
    $(this).blur();
    let ncb = $('.new-comment-block');
    if (ncb.length) ncb.slideUp('slow', function() {ncb.remove();});
    let par = $(this).parents('.root-commentary');
    let cid = $(this).data().id;
    $.ajax({
      method: 'POST',
      url: '/api/answer',
      data: {
        auth: window.localStorage.getItem('token'),
        cid: cid
      },
      success: function(data) {
        let html = Mustache.render($('#sanswert').html(), data);
        let al = $('.comment-alert');
        if (al.length) al.remove();
        let nab = $('.new-answer-block');
        if (nab.length) nab.slideUp('slow', function() {nab.remove();});
        par.after(html);
        if (data.perm) {
          $('.new-answer-block').slideDown('slow', function() {
            scrollPanel($('.new-answer-block'));
          });
        } else {
          $('.comment-alert').slideDown('slow');
        }
      },
      dataType: 'json'
    });
  });
  $('body').on('click', '#new-comment-add', function() {
    $(this).blur();
    let nab = $('.new-answer-block');
    if (nab.length) nab.slideUp('slow', function() {nab.remove();});
    let form = $('.new-comment-block');
    if (form.length) {
      if (form.is(':hidden')) {
        form.slideDown('slow', function() {
          scrollPanel($('.comments-options'));
        });
      } else {
        form.slideUp('slow');
      }
    } else {
      $.ajax({
        method: 'POST',
        url: '/api/art',
        data: {
          auth: window.localStorage.getItem('token'),
          slug: slug
        },
        success: function(data) {
          let html = Mustache.render($('#scommentt').html(), data);
          let al = $('.comment-alert');
          if (al.length) al.remove();
          let ncb = $('.new-comment-block');
          if (ncb.length) ncb.remove();
          $('.comments-options').after(html);
          if (data.perm) {
            $('.new-comment-block').slideDown('slow', function() {
              scrollPanel($('.comments-options'));
            });
          } else {
            $('.comment-alert').slideDown('slow');
          }
        },
        dataType: 'json'
      });
    }
  });
  if (window.localStorage.getItem('token')) {
    $('body').on('click', '.remove-commentary', function() {
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
            window.location.reload();
          } else {
            showError(par, data);
            scrollPanel($('#ealert'));
          }
        },
        dataType: 'json'
      });
    });
    $('body').on('click', '.trash-button', function() {
      $(this).blur();
      showHideButton($(this), '.remove-commentary');
    });
    $('body').on('click', '#answer-submit', function() {
      $(this).blur();
      let pid = $(this).data().pid;
      let text = $('#answer-editor').val();
      if (text) {
        $.ajax({
          method: 'PUT',
          url: '/api/answer',
          data: {
            slug: slug,
            pid: pid,
            auth: window.localStorage.getItem('token'),
            text: text
          },
          success: function(data) {
            if (data.done) {
              window.location.reload();
            } else {
              showError('.new-answer-block', data);
              scrollPanel($('#ealert'));
            }
          },
          dataType: 'json'
        });
      }
    });
    $('body').on('click', '#comment-submit', function() {
      $(this).blur();
      let text = $('#comment-editor').val();
      if (text) {
        $.ajax({
          method: 'POST',
          url: '/api/comment',
          data: {
            slug: slug,
            auth: window.localStorage.getItem('token'),
            text: text
          },
          success: function(data) {
            if (data.done) {
              window.location.reload();
            } else {
              showError('.new-comment-block', data);
              scrollPanel($('#ealert'));
            }
          },
          dataType: 'json'
        });
      }
    });
    $('body').on('click', '#censor-this', {slug: slug}, censorThis);
    $('body').on('click', '#special-case', {slug: slug}, function(event) {
      $(this).blur();
      undressLinks(event.data.slug);
    });
    $('body').on('click', '#tape-out', {slug: slug}, follow);
    $('body').on('click', '#tape-in', {slug: slug}, follow);
    $('body').on('click', '#dislike-button', {slug: slug}, function(event) {
      $(this).blur();
      $.ajax({
        method: 'PUT',
        url: '/api/dislike',
        data: {
          auth: window.localStorage.getItem('token'),
          slug: event.data.slug
        },
        success: function(data) {
          if (data.message) {
            showError('#options-block', data);
          } else {
            if (data.done) {
              $('.like-block .value').text(data.likes);
              $('.dislike-block .value').text(data.dislikes);
              $('#like-button .value').text(data.likes);
              $('#dislike-button .value').text(data.dislikes);
            }
          }
        },
        dataType: 'json'
      });
    });
    $('body').on('click', '#like-button', {slug: slug}, function(event) {
      $(this).blur();
      $.ajax({
        method: 'PUT',
        url: '/api/like',
        data: {
          auth: window.localStorage.getItem('token'),
          slug: event.data.slug
        },
        success: function(data) {
          if (data.message) {
            showError('#options-block', data);
          } else {
            $('.like-block .value').text(data.likes);
            $('.dislike-block .value').text(data.dislikes);
            $('#like-button .value').text(data.likes);
            $('#dislike-button .value').text(data.dislikes);
          }
        },
        dataType: 'json'
      });
    });
  }
  let interval = setInterval(function() {
    if ($('.comments-options').length) {
      showCommentaries(slug);
      clearInterval(interval);
    }
  }, 20);
});
