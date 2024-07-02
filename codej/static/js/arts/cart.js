$(function() {
  "use strict";
  if (cu && !window.localStorage.getItem('token')) {
    ping();
    window.location.reload();
  }
  if (!cu && window.localStorage.getItem('token')) {
    window.localStorage.removeItem('token');
  }
  let dt = luxon.DateTime.now();
  formatFooter(dt);
  $('body').on('click', '.closeable', closeTopFlashed);
  showArt('/api/cart', slug);
  if (window.localStorage.getItem('token')) {
    checkIncomming();
    $('body').on('click', '.copy-link', showCopyForm);
    $('body').on('click', '.entity-text-block img', clickImage);
    $('body').on('click', '#move-screen-up', function() {
      $(this).blur();
      scrollPanel($('#navigation'));
    });
    $('body').on('click', '#censor-this', {slug: slug}, censorThis);
  }

});
