function adjust(image) {
  let width = image.width();
  let parent_ = image.parents('p');
  let width_ = parseInt(parent_.outerWidth());
  if (width > width_) image.attr('width', width_);
}


function adjustImage() {
  adjust($(this));
  $(this).on('load', function() {
    adjust($(this));
  });
  $(this).parents('p').addClass('image-par');
}
