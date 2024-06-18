function blurBodyAn() {
  let v = $(this).val();
  let g = $(this).parents('.form-group');
  if (v.length === 0 || v.length > 1024) {
    g.addClass('has-error');
  }
}
