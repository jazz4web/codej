function showArt(url, slug, dt) {
  let token = window.localStorage.getItem('token');
  let tee = token ? {'x-auth-token': token} : {};
  $.ajax({
    method: 'GET',
    url: url,
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
      if (data.art) {
        $('title').text($('title').text().trim() + ' ' + data.art.title);
      } else {
        $('title').text($('title').text().trim() + ' пусто');
      }
      if (data.message) {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#main-container').removeClass('nonlisted').append(html);
        slidePage('#ealert');
      } else {
        let html = Mustache.render($('#artt').html(), data);
        $('#main-container').append(html);
        if (!data.own && !data.admin) countClicks(data.art.suffix);
        $('.date-field').each(function() { formatDateTime($(this)); });
        $('#copy-button').on('click', {cls: '#link-copy-form'}, copyThis);
        pingUser();
        checkMC(860);
        $('.entity-text-block iframe').each(adjustFrame);
        $('.entity-text-block').children().each(setMargin);
        $('.entity-text-block img').each(adjustImage);
        let lhtml = $('.labels').html().trim().slice(0, -1);
        $('.labels').html(lhtml);
      }
    },
    dataType: 'json'
  });
}
