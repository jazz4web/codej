function copyAlias() {
  $(this).blur();
  let clipboard = new ClipboardJS('#' + $(this)[0].id);
  clipboard.on('success', function(e) {
    // pass;
  });
}
