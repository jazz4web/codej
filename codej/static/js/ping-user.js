function ping() {
  $.ajax({
    method: 'POST',
    url: '/api/index',
    data: {
      auth: window.localStorage.getItem('token')
    },
    success: function(data) {},
    dataType: 'json'
  });
}

function pingUser() {
  setInterval(ping, 300000);
}
