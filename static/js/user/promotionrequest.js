$(document).ready(function () {
    $('form').submit(function () {
        event.preventDefault();

        $.ajax({
            url: '/user/promotionrequest',
            data: $('form').serialize(),
            type: 'POST',
            success: function (message) {
                if (message == 'success') {
                    $('#response').addClass('text-success mt-2');
                    $('#response').text("Promotion request sent! An admin will review it soon.");
                    $('form').remove();
                }
            }
        });
    });
});