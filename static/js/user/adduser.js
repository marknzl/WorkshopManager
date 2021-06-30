// This file contains all AJAX code for user adding functionality

$(document).ready(function () {
    $('form').submit(function (event) {
        $.ajax({
            url: '/user/add',
            data: $('form').serialize(),
            type: 'POST',
            success: function (message) {
                $("#response").removeClass();

                if (message == "success") {
                    $("#response").addClass("text-success");
                    $("#response").text("User added!");
                } else {
                    $("#response").addClass("text-danger");
                    $("#response").text("User already exists with entered email address and/or username!");
                }
            }
        });

        event.preventDefault();
    });
});