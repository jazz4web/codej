function renderLastSeen(elem) {
  let text = $.trim(elem.text());
  elem.text(luxon.DateTime.fromISO(text).setLocale('ru').toRelative());
}
