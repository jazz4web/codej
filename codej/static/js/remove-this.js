function removeThis(event) {
  $(this).blur();
  let suffix = $(this).data().suffix;
  let last = $(this).data().last;
  $.ajax({
    method: 'DELETE',
    url: '/api/pictures/' + event.data.suffix,
    data: {
      token: window.localStorage.getItem('token'),
      picture: suffix,
      last: last,
      page: event.data.page
    },
    success: function(data) {
      if (data.album) {
        window.location.replace(data.url);
      } else {
        showError('#left-panel', data);
        scrollPanel($('#ealert'));
      }
    },
    dataType: 'json'
  });
}
