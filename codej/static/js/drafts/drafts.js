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
  showDrafts(dt, '/api/drafts', page);
  if (window.localStorage.getItem('token')) {
    $('body').on('click', '#title-submit', function() {
      let title = $('#title');
      title.blur();
      $(this).blur();
      if (!$('.input-field').hasClass('has-error')) {
        $.ajax({
          method: 'POST',
          url: '/api/drafts',
          data: {
            auth: window.localStorage.getItem('token'),
            title: title.val().trim()
          },
          success: function(data) {
            console.log(data);
            if (data.draft) {
              window.location.assign(data.draft);
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
    $('body').on(
      'keyup blur', '#title', {min: 3, max: 100, block: '.input-field'},
      markInputError);

  }
});
