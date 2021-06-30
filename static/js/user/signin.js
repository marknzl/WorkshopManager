// This file contains all AJAX code for sign in functionality

$(document).ready(function () {
    $("#login_button").click(function (event) {
        event.preventDefault();

        $('#loading_spinner').prop('hidden', false);

        $.ajax({
            url: '/user/signin',
            data: $('form').serialize(),
            type: 'POST',
            success: function (message) {
                $("#response").removeClass();
                if (message == "success") {
                    $("#response").addClass("text-success");
                    $("#response").text("Successful login!");
                    $('#loading_spinner').prop('hidden', true);
                    window.location = '/'
                } else {
                    $("#response").addClass("text-danger");
                    $("#response").text("Invalid login details!");
                    $('#password').effect('shake');
                    $('#user_handle').effect('shake');

                    $('#user_handle').prop('disabled', false);
                    $('#password').prop('disabled', false);
                    $('#login_button').prop('disabled', false);
                    $('#loading_spinner').prop('hidden', true);
                }
            }
        });

        $('#user_handle').prop('disabled', true);
        $('#password').prop('disabled', true);
        $('#login_button').prop('disabled', true);
    });

    $('#show_user_list').click(function (event) {
        $('#user_list_modal').modal('show');
    });
});