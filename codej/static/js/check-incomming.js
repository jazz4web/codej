function checkIncomming() {
  $.ajax({
    method: 'POST',
    url: '/api/convs',
    data: {
      auth: window.localStorage.getItem('token')
    },
    success: function(data) {
      if (data.pm) {
        let interval = setInterval(function() {
          if ($('#main-container').length) {
            let flashed = $('.top-flashed-block');
            data = {'flashed': flashed.length};
            let html = Mustache.render($('#pmalertt').html(), data);
            if (flashed.length) {
              flashed.append(html);
            } else {
              $('#main-container').prepend(html);
            }
            clearInterval(interval);
          }
        }, 10);
      }
    },
    dataType: 'json'
  });
}
