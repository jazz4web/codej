function showLabeledDrafts(url, page, label, dt) {
  let token = window.localStorage.getItem('token');
  let tee = token ? {'x-auth-token': token} : {};
  $.ajax({
    method: 'GET',
    url: url,
    headers: tee,
    data: {
      page: page,
      label: label
    },
    success: function(data) {
      if (token) {
        if (!data.cu || data.cu.brkey != checkBrowser()) {
          window.localStorage.removeItem('token');
          window.location.reload();
        }
      }
      if (data.message) {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#main-container').append(html);
        slidePage('#ealert');
      } else {
        let html = Mustache.render($('#draftst').html(), data);
        $('#main-container').append(html);
        $('.date-field').each(function() { formatDateTime($(this)); });
        $('.entity-block').each(checkNext);
        if ($('.today-field').length) renderTF('.today-field', dt);
        $('.labels').each(fixComma);
        if (data.pv) renderPV(data.pagination.page);
        checkMC(860);
      }
    },
    dataType: 'json'
  });
}
