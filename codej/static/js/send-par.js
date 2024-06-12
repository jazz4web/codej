function sendPar(slug, val, code) {
  $.ajax({
    method: 'POST',
    url: '/api/send-par',
    data: {
      auth: window.localStorage.getItem('token'),
      slug: slug,
      text: val,
      code: code
    },
    success: function(data) {
      if (data.done) {
        if (!$('.entity-text-block').length) window.location.reload();
        if (data.html) {
          $('.entity-text-block')
            .empty().append(data.html).data('len', data.length);
          parseDraft();
        }
        $('#html-text-edit').val('');
      } else {
        showError('.editor-forms-block', data);
        $('#ealert').addClass('next-block');
      }
    },
    dataType: 'json'
  });
}
