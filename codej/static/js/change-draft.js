function changeDraft(field, value, slug) {
  $.ajax({
    method: 'PUT',
    url: '/api/draft',
    data: {
      auth: window.localStorage.getItem('token'),
      field: field,
      value: value,
      slug: slug
    },
    success: function(data) {
      if (data.done) {
        if (data.slug) {
          window.location.replace('/drafts/' + data.slug);
        } else {
          window.location.reload();
        }
      } else {
        showError('.editor-forms-block', data);
        $('#ealert').addClass('next-block');
      }
    },
    dataType: 'json'
  });
}
