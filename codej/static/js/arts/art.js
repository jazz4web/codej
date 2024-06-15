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
  $('body').on('click', '.copy-link', showCopyForm);
  $('body').on('click', '.entity-text-block img', clickImage);
  $('body').on('click', '#move-screen-up', moveScreenUp);
  showArt('/api/art', slug, dt);
  if (window.localStorage.getItem('token')) {
    $('body').on('click', '#tape-out', {slug: slug}, follow);
    $('body').on('click', '#tape-in', {slug: slug}, follow);
  }
});
