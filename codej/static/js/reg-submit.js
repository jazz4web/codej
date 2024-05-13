function regSubmit() {
  $(this).blur();
  let tee = {
    address: $('#raddress').val(),
    cache: $('#rsuffix').val(),
    captcha: $('#rcaptcha').val()
  };
  if (tee.address && tee.cache && tee.captcha) {
    $.ajax({
      method: 'POST',
      url: '/api/request-reg',
      data: tee,
      success: function(data) {
        console.log(data);
        if (data.done) {
          window.location.replace('/');
        } else {
          showError('#regf', data);
        }
      },
      dataType: 'json'
    });
  }
}
