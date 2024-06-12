function undressLinks(slug) {
  $.ajax({
    method: 'PATCH',
    url: '/api/draft',
    data: {
      auth: window.localStorage.getItem('token'),
      slug: slug
    },
    success: function(data) {
      if (data.done) {
        window.location.reload();
      } else {
        showError('#topic-head', data);
        $('#ealert').addClass('next-block');
        scrollPanel($('#ealert'));
      }
    },
    dataType: 'json'
  });
}
