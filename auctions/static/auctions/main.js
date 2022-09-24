function placeBid() {
    if ($('.bid-form-input').css('display') === 'none') {
      $('.bid-form-input').css('display', 'inline-block');
      $('select.bid-form-input').css('display', 'none');
    }else{
      $('.bid-form-input').css('display', 'none');

    }
  };

function imageUrl() {
  if ($('.image-url-input').css('display') === 'none') {
    $('.image-url-input').css('display', 'inline-block');
    $('.image-btn').val('Image File');
    $('#id_image').css('display', 'none');
    $('.image-url-input').css('margin-top', '20px');
  }else{
    $('.image-url-input').css('display', 'none');
    $('#id_image').css('display', 'inline-block');
    $('.image-btn').val('Image URL');
    
  }
};

function showCategories() {
  $('ul.categories').css('display', 'block');

}

function closeCategories() {
  $('ul.categories').css('display', 'none');
}

