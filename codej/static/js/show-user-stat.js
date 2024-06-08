function showUserStat() {
  let token = window.localStorage.getItem('token');
  let tee = token ? {'x-auth-token': token} : {};
  $.ajax({
    method: 'GET',
    url: '/api/ustat',
    headers: tee,
    success: function(data) {
      if (data.stat) {
        let ust = Mustache.render($('#ustatt').html(), data);
        $('#right-panel').empty().append(ust);
        formatDateTime($('.date-field'));
        checkMC(1152);
      } else {
        showError('#left-panel', data);
        scrollPanel($('#ealert'));
      }
    },
    dataType: 'json'
  });
}
