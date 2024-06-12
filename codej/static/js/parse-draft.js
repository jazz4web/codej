function parseDraft() {
  let ch = $('.entity-text-block').children();
  let len = $('.entity-text-block').data().len;
  for (let i = 0, m = 0; i < ch.length && m < len; i++) {
    n = ch[i].nodeName;
    if (n === 'UL' || n === 'OL' || n === 'BLOCKQUOTE') {
      let lch = $(ch[i]).children();
      let l = lch.length;
      let j = 0;
      while (j < lch.length) {
        $(lch[j]).attr({'data-num': m});
        $(lch[j]).addClass('editable');
        j++;
        m++;
      }
    } else {
      $(ch[i]).attr({'data-num': m});
      $(ch[i]).addClass('editable');
      m++;
    }
  }
  $('.entity-text-block iframe').each(adjustFrame);
  $('.entity-text-block').children().each(setMargin);
  $('.entity-text-block img').each(adjustImage);
}
