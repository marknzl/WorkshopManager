var workshopID = 0;
var workshopName = "";

$(document).ready(function () {
    $('button').click(function () {
        var name = $(this).attr('name');

        if (name == 'enroll_btn') {
            var workshopObj = JSON.parse($(this).val());
            workshopID = workshopObj.id;
            workshopName = workshopObj.workshopName;

            $.ajax({
                url: '/workshop/enroll',
                data: {
                    workshop_id: workshopID
                },
                type: 'POST',
                success: function (message) {
                    $('#' + workshopID).remove();
                    $('#toast_text').text('You have been enrolled in "' + workshopName + '"!');
                    $('#enroll_notification').toast('show');
                }
            });
        }

        if (name == 'delete_btn') {
            workshopID = $(this).val();
            workshopName = $(this).data('workshopname');
            $('#workshop_id_modal').text('Are you sure you want to delete "' + workshopName + '"?');
            $('#workshop_delete_modal').modal('show');
        }
    });

    $('#enroll_private_link').click(function () {
        $('#private_enroll_modal').modal('show');
    });

    $('#enroll_private_btn').click(function () {
        var workshop_code = $('#workshop_code').val();

        if (workshop_code == "" || workshop_code == null) {
            $('#private_enroll_response_text').addClass('text-danger mt-2');
            $('#private_enroll_response_text').text("Enter a valid workshop code!");

            return;
        }

        $.ajax({
            url: '/workshop/enroll',
            data: {
                private: 1,
                workshop_code: workshop_code
            },
            type: 'POST',
            success: function (message) {
                $('#private_enroll_response_text').removeClass();

                if (message != 'error' && message != 'already enrolled' && message != 'max' && message != 'invalid_code') {
                    $('#private_enroll_response_text').addClass('text-success mt-2');
                    $('#private_enroll_response_text').text('You have been enrolled! ');
                    $('#private_enroll_response_text').append('<a href="/workshop/view/' + message + '">Click here to view the workshop');
                } else if (message == 'already enrolled') {
                    $('#private_enroll_response_text').addClass('text-danger mt-2');
                    $('#private_enroll_response_text').text("You're already enrolled in that workshop!");
                } else if (message == 'max') {
                    $('#private_enroll_response_text').addClass('text-danger mt-2');
                    $('#private_enroll_response_text').text("Max amount of students reached for that workshop!");
                } else if (message == 'invalid_code') {
                    $('#private_enroll_response_text').addClass('text-danger mt-2');
                    $('#private_enroll_response_text').text("Enter a valid workshop code!");
                } else {
                    $('#private_enroll_response_text').addClass('text-danger mt-2');
                    $('#private_enroll_response_text').text("Workshop doesn't exist!");
                }
            }
        })
    });

    // Workshop delete handler
    $('#workshopdel_delete_btn').click(function () {
        $('#workshopdel_delete_btn').prop('disabled', true);
        $('#workshopdel_keep_btn').prop('disabled', true);

        $.ajax({
            url: '/workshop/delete',
            data: {
                workshop_id: workshopID
            },
            type: 'POST',
            success: function (message) {
                if (message == 'success') {
                    $("#" + workshopID).remove();

                    $('#workshop_id_modal').addClass('text-muted');
                    $('#workshopdel_response_text').addClass('text-success');
                    $('#workshopdel_response_text').text('Workshop #' + workshopID + ' has been removed!');

                    $('#toast_text').text('Workshop has been deleted!');
                    $('#delete_notification').toast('show');
                    workshopID = null;
                }
            }
        });
    });

    // Delete modal events
    $('#workshopdel_keep_btn').click(function () {
        $('#confirm_deletion_modal').modal('hide');
    });

    $('#workshop_delete_modal').on('hidden.bs.modal', function () {
        $('#workshopdel_delete_btn').prop('disabled', false);
        $('#workshopdel_keep_btn').prop('disabled', false);

        $('#workshop_id_modal').removeClass('text-muted');
        $('#workshopdel_response_text').removeClass('text-success');
        $('#workshopdel_response_text').text('');
        workshopID = null;
    });
})