$(function() {
  "use strict";
  let dt = luxon.DateTime.now();
  formatFooter(dt);
  if ($('.today-field').length) renderTF('.today-field', dt);
  checkMC(860);
});
