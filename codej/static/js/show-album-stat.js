function showAlbumStat(suffix) {
  let token = window.localStorage.getItem('token');
  let tee = token ? {'x-auth-token': token} : {};
  $.ajax({
    method: 'GET',
    url: '/api/albumstat',
    headers: tee,
    data: {
      suffix: suffix
    },
    success: function(data) {
      if (data.album) {
        let html = Mustache.render($('#astatt').html(), data);
        $('#right-panel').empty().append(html);
        formatDateTime($('.date-field'));
        let s = $('#select-status option');
        for (let n = 0; n < s.length; n++) {
          if (s[n].value == data.album.state) {
            $(s[n]).attr('selected', 'selected');
          }
        }
        checkMC(1152);
      } else {
        showError('#left-panel', data);
        scrollPanel($('#ealert'));
      }
    },
    dataType: 'json'
  });
}
