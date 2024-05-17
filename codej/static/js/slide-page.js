function slidePage(eid) {
  let block = $(eid);
  block.slideDown('slow', function() { checkMC(860); });
  block.siblings().each(function() {
    $(this).slideUp('slow', function() { $(this).remove(); });
  });
}
