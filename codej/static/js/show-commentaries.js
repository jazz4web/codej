function showCommentaries(slug) {
  let token = window.localStorage.getItem('token');
  let tee = token ? {'x-auth-token': token} : {};
  $.ajax({
    method: 'GET',
    url: '/api/comment',
    headers: tee,
    data: {
      slug: slug
    },
    success: function(data) {
      if (data.commentaries) {
        for (let each of data.commentaries) {
          let html = Mustache.render($('#brancht').html(), each);
          $('#entity-commentaries').append(html);
          showChildren(each.children, each.id);
        }
        $('.commentary-attributes .date-field').each(function() {
          formatDateTime($(this));
        });
        checkMC(860);
        $('.commentary-body iframe').each(adjustFrame);
        $('.commentary-body').children().each(setMargin);
        $('.commentary-body img').each(adjustImage);
        $('#entity-commentaries').slideDown('slow');
      }
    },
    dataType: 'json'
  });
}
