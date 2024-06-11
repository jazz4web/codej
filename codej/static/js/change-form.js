function changeForm(a, fa) {
  let f = $(a);
  if (f.is(':hidden')) {
    f.slideDown('slow', function() {
      $(fa).focus();
      scrollPanel(f);
    });
    f.siblings().each(function() {
      if (!$(this).is(':hidden')) $(this).slideUp('slow');
    });
  } else {
    f.slideUp('slow');
    $('#new-paragraph-editor').slideDown('slow', function() {
      $('#html-text-edit').focus();
    });
  }
}
