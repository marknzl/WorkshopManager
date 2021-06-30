// This file contains all AJAX code for registration functionality

$(document).ready(function () {
    $('form').submit(function (event) {
        $.ajax({
            url: '/user/register',
            data: $('form').serialize(),
            type: 'POST',
            success: function (message) {
                $("#response").removeClass();

                if (message == "success") {
                    $("#response").addClass("text-success");
                    $("#response").text("Successful registration!");

                    window.location = '/user/signin';
                } else {
                    $("#response").addClass("text-danger");
                    $("#response").text("User already exists with entered email address and/or username!");
                }
            }
        });

        event.preventDefault();
    });
});