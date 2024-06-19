function showAnns(suffix) {
  $.ajax({
    method: 'GET',
    url: '/api/broadcast',
    data: {
      suffix: suffix
    },
    success: function(data) {
      if (data.anns) {
        let html = Mustache.render($('#announcet').html(), data);
        $('.text-block').before(html);
        $('.announce-block .entity-text-block iframe').each(adjustFrame);
        $('.announce-block .entity-text-block').children().each(setMargin);
        $('.announce-block .entity-text-block img').each(adjustImage);
      }
    },
    dataType: 'json'
  });
}
