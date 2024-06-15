function follow(event) {
  $(this).blur();
  $.ajax({
    method: 'PUT',
    url: '/api/follow',
    data: {
      auth: window.localStorage.getItem('token'),
      slug: event.data.slug
    },
    success: function(data) {
      if (data.message) {
        showError('#options-block', data);
      } else {
        window.location.reload();
      }
    },
    dataType: 'json'
  });
}
