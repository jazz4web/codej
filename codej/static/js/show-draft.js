function showDraft(slug, dt) {
  let token = window.localStorage.getItem('token');
  let tee = token ? {'x-auth-token': token} : {};
  $.ajax({
    method: 'GET',
    url: '/api/draft',
    headers: tee,
    data: {
      slug: slug
    },
    success: function(data) {
      console.log(data);
      if (token) {
        if (!data.cu || data.cu.brkey != checkBrowser()) {
          window.localStorage.removeItem('token');
          window.location.reload();
        }
      }
      if (data.draft) {
        $('title').text($('title').text().trim() + ' ' + data.draft.title);
      }
      if (data.message) {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#main-container').removeClass('nonlisted').append(html);
        slidePage('#ealert');
      } else {
        let html = Mustache.render($('#draftt').html(), data);
        $('#main-container').append(html);
        $('.date-field').each(function() { formatDateTime($(this)); });
        $('#copy-button').on('click', {cls: '#link-copy-form'}, copyThis);
        let s = $('#select-status option');
        for (let n = 0; n < s.length; n++) {
          if (s[n].value == data.draft.state) {
            $(s[n]).attr('selected', 'selected');
          }
        }
        checkMC(860);
      }
    },
    dataType: 'json'
  });
}
