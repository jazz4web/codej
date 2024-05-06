function resize(wwidth, width) {
  if (wwidth > width) {
    $('#main-container').css({"width": width - 20});
  } else {
    $('#main-container').css({"width": wwidth - 20});
  }
}

function checkMC(width) {
  let wwidth = $(window).width();
  let mcon = $('#main-container');
  resize(wwidth, width);
  $(window).on('resize', function() {
    let wwidth = $(window).width();
    resize(wwidth, width);
  });
}
