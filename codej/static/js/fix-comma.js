function fixComma() {
  let html = $(this).html().trim();
  if (html.slice(-1) === ',') html = html.slice(0, -1);
  $(this).html(html);
}
