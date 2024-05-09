function showError(eid, data) {
  let html = Mustache.render($('#ealertt').html(), data);
  let b = $('#ealert');
  if (b.length) b.remove();
  $(eid).before(html);
  $('#ealert').slideDown('slow');
}
