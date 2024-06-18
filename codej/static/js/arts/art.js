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
  if (window.localStorage.getItem('token')) {
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
});
