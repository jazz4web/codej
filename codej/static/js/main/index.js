$(function() {
  "use strict";
  let dt = luxon.DateTime.now();
  formatFooter(dt);
  if ($('.today-field').length) renderTF('.today-field', dt);
  $('body').on('click', '.closeable', closeTopFlashed);
  checkMC(860);
});
