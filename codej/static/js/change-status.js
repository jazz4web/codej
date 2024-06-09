function changeStatus(event) {
  let suffix = event.data.suffix ? event.data.suffix : $(this).data().suffix;
  $.ajax({
    method: 'PUT',
    url: '/api/pictures/' + suffix,
    data: {
      token: window.localStorage.getItem('token'),
      field: 'state',
      value: $(this).val()
    },
    success: function(data) {
      if (data.album) {
        window.location.replace('/pictures/' + suffix);
      } else {
        showError('#left-panel', data);
        scrollPanel($('#ealert'));
      }
    },
    dataType: 'json'
  });
}
