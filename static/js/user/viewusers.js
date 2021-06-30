var userID = null;
var fullName = "";

$(document).ready(function () {
    $('button').click(function () {
        var name = $(this).attr('name');

        if (name == 'delete_btn') {
            userID = $(this).val();
            fullName = $(this).data('fullname');

            $('#user_id_modal').text('Are you sure you want to delete user "' + fullName + '"?');
            $('#confirm_deletion_modal').modal('show');
        }
    });

    $('#modal_accept_btn').click(function () {
        $('#modal_accept_btn').prop('disabled', true);
        $('#modal_deny_btn').prop('disabled', true);

        $.ajax({
            url: '/user/delete',
            data: {
                user_id: userID
            },
            type: 'POST',
            success: function (message) {
                $('#response_text').removeClass();

                if (message == 'success') {
                    $("#response_text").addClass("text-success mt-2");
                    $('#response_text').text("User deleted!");

                    $('#' + userID).remove();
                    userID = null;
                } else {
                    $('#response_text').addClass("text-danger mt-2");
                    $('#response_text').text("An error occurred, please contact an admin");
                }                
            }
        });
    });

    $('#modal_deny_btn').click(function () {
        $('#confirm_deletion_modal').modal('hide');
    });

    $('#confirm_deletion_modal').on('hidden.bs.modal', function () {
        $("#response_text").removeClass();
        $('#response_text').text('');
        $('#modal_accept_btn').prop('disabled', false);
        $('#modal_deny_btn').prop('disabled', false);
    });
});