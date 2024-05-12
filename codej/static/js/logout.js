function lout(url) {
    $.ajax({
      method: 'DELETE',
      url: url,
      data: {
        token: window.localStorage.getItem('token')
      },
      success: function(data) {
        if (data.result) {
          window.localStorage.removeItem('token');
          window.location.assign('/');
        }
      },
      dataType: 'json'
    });
}
