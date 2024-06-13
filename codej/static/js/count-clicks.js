function countClicks(suffix) {
  let cur = window.localStorage.getItem('viewed_');
  if (!cur) {
    cur = new Array();
  } else {
    cur = cur.split(',');
  }
  if (!cur.includes(suffix)) {
    $.ajax({
      method: 'PUT',
      url: '/api/art',
      data: {
        field: 'viewed',
        suffix: suffix
      },
      success: function(data) {
        if (data.done) {
          $('.viewed-ind .value').text(data.views);
        }
      },
      dataType: 'json'
    });
    cur.push(suffix);
    if (cur.length > 200) cur.shift();
    window.localStorage.setItem('viewed_', cur.join());
  }
}
