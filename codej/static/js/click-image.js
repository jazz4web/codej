function clickImage() {
  let w;
  if ($(this).data().link) {
    w = window.open($(this).data().link, '_blank');
    w.focus();
  } else {
    w = window.open($(this).prop("src"), '_blank');
    w.focus();
  }
}
