function changeAnn(field, value, suffix) {
  $.ajax({
    method: 'PUT',
    url: '/api/announce',
    data: {
      field: field,
      value: value,
      suffix: suffix,
      auth: window.localStorage.getItem('token')
    },
    success: function(data) {
      if (data.done) {
        window.location.reload();
      } else {
        showError('.ann-block', data);
        scrollPanel($('#ealert'));
      }
    },
    dataType: 'json'
  });
}
