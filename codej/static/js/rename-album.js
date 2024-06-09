function renameAlbum(event) {
  $(this).blur();
  let suffix = event.data.suffix ? event.data.suffix : $(this).data().suffix;
  let current = $('#left-panel .panel-title').text().trim();
  let newtitle = $('#title-change').val().trim();
  if (!$('#rename-form').hasClass('has-error') && newtitle !== current) {
    $.ajax({
      method: 'PUT',
      url: '/api/pictures/' + suffix,
      data: {
        token: window.localStorage.getItem('token'),
        field: 'title',
        value: newtitle
      },
      success: function(data) {
        if (data.album) {
          window.location.replace('/pictures/' + suffix);
        } else {
          showError('#left-panel', data);
          scrollPanel($('#ealert'));
        }
      },
      dataType: 'json'
    });
  }
}
