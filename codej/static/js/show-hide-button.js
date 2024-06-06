function showHideButton(ths, cls) {
  let target = ths.siblings(cls);
  if (target.is(':hidden')) {
    $(cls).each(function() { $(this).fadeOut('slow'); });
    target.fadeIn('slow');
  } else {
    target.fadeOut('slow');
  }
}
