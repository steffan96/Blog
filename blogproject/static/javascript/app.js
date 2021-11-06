$(document).ready(function() {
    $('.likeButton').on('click', function() {
        var like = $('#likeId').val();
        var unlike = $('#unlikeId').val();
        var post_id = $('#post_idd').val():

        req = $.ajax({
            url : '/like/' +post_id,
            type : 'POST',
            data : {} 
        })
    })
})