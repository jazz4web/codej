function slideBlock() {
  let body = $(this).siblings('.block-body');
  if (body.is(':hidden')) {
    body.slideDown('slow', function() {checkMC(860);});

  } else {
    body.slideUp('slow', function() {checkMC(860);});
  }
}
