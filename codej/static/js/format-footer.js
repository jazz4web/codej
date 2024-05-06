function formatFooter(dt) {
  let footer = $.trim($('#footer-link').text());
  let html = '&copy;' + ' ' + footer + ', ' + dt.year;
  $('#footer-link').html(html);
}
