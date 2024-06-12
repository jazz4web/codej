function sendEdit(slug, num, insert, text, code) {
  $.ajax({
    method: 'PUT',
    url: '/api/send-par',
    data: {
      auth: window.localStorage.getItem('token'),
      slug: slug,
      num: num,
      insert: insert,
      text: text,
      code: code
    },
    success: function(data) {
      if (data.done) {
        if (data.html) {
          $('.entity-text-block').empty()
                                 .append(data.html)
                                 .data('len', data.length);
          parseDraft();
          $('#options-block').slideDown('slow');
        }
      } else {
        showError('.entity-text-block', data);
        $('#ealert').addClass('next-block');
        scrollPanel($('#ealert'));
      }
    },
    dataType: 'json'
  });
}
