function checkNext() {
  let next = $(this).next('.entity-block');
  if (next.length && !next.hasClass('next-block')) {
    next.addClass('next-block');
  }
}
