function showCopyForm() {
  $(this).blur();
  let target = $('#link-copy-form');
  if (target.is(':hidden')) {
    target.slideDown('slow');
  } else {
    target.slideUp('slow');
  }
}
