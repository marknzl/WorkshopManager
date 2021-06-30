$(document).ready(function () {
    $('form').submit(function () {
        $('#save_workshop_btn').prop('disabled', true);
        var userID = $('#save_btn').val();

        var confirmed = confirm('Please note that if you are editing your own profile, you will be logged out. You may choose to confirm or cancel.');
        if (!confirmed) {
            return false;
        }

        $.ajax({
            url: '/user/edit/' + userID,
            data: $('form').serialize(),
            type: 'POST',
            success: function (message) {
                $('#response').removeClass();
                $('#response').text('');

                if (message == 'same_handle') {
                    $('#response').addClass('text-danger mt-2');
                    $('#response').text("Your new email/username is already taken!");
                    return;
                }

                if (message == 'success') {
                    $('#response').addClass('text-success mt-2');
                    $('#response').text("User saved!");
                    $('#save_workshop_btn').prop('disabled', false);

                    $('#toast_text').text('User profile saved!');
                    $('#save_notification').toast('show');
                } else if (message = 'success_own') {
                    window.location = '/user/signout'
                } else {
                    $('#response').addClass('text-danger');
                    $('#response').text('Error occurred');
                    $('#save_workshop_btn').prop('disabled', true);
                }
            }
        });

        event.preventDefault();
    });
});