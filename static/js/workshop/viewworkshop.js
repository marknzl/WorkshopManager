$(document).ready(function () {
    var enrollmentID = "";
    var enrolledStudent = "";
    var fileID = "";
    var fileName = "";

    $('button').click(function () {
        var name = $(this).attr('name');

        if (name == 'kick_btn') {
            enrollmentID = $(this).val();
            enrolledStudent = $(this).data('fullname');
            $('#student_id_modal').text('Are you sure you want to kick ' + enrolledStudent + '?');
            $('#confirm_kick_modal').modal('show');
        }

        if (name == 'delete_file_btn') {
            fileID = $(this).val();
            fileName = $(this).data('filename');

            $('#file_id_modal').text('Are you sure you want to delete "' + fileName + '"?');
            $('#confirm_file_delete_modal').modal('show');
        }

        if (name == 'add_student_btn') {
            $('#add_student_modal').modal('show');
        }

        if (name == 'complete_btn') {
            var workshopID = $(this).val();
            var confirmCompletion = confirm('Are you sure you want to mark this workshop as complete?');

            if (confirmCompletion) {
                window.location = '/workshop/complete/' + workshopID;
            }
        }

        if (name == 'revert_complete_btn') {
            var workshopID = $(this).val();
            var revertCompletion = confirm('Are you sure you want revert this workshop back to in-complete?');

            if (revertCompletion) {
                window.location = '/workshop/complete/revert/' + workshopID;
            }
        }
    });

    $('#upload_file_form').submit(function (event) {
        event.preventDefault();
        var form = $('form')[0];
        var data = new FormData(form);

        $.ajax({
            url: '/workshop/file/upload',
            data: data,
            enctype: 'multipart/form-data',
            processData: false,
            contentType: false,
            cache: false,
            type: 'POST',
            success: function (message) {
                $('#file_upload_response').removeClass();

                if (message != "error") {
                    var file_obj = JSON.parse(message);

                    $('#file_table').append('<tr>' +
                        '<td>' + file_obj.name + '</td>' +
                        '<td><div class="btn-toolbar">' +
                        '<a class="btn btn-sm btn-primary" href="/workshop/file/download/' + file_obj.location + '"><span><i class="fa fa-download"></i></span></a>' +
                        '<button name="delete_file_btn" value="' + file_obj.file_id + '" class="btn btn-sm btn-danger ml-2"><span><i class="fa fa-trash"></i></span></button>' +
                        '</div></tr>');

                    $('#file_upload_response').addClass('text-success');
                    $('#file_upload_response').text("File uploaded!");
                } else {
                    $('#file_upload_response').addClass('text-danger');
                    $('#file_upload_response').text("Choose a valid file for upload!");
                }

                $('form').trigger("reset");
            }
        });
    });

    $('#kick_modal_accept_btn').click(function () {
        $('#kick_modal_accept_btn').prop('disabled', true);
        $('#kick_modal_deny_btn').prop('disabled', true);

        $.ajax({
            url: '/workshop/kick',
            data: {
                enrollment_id: enrollmentID
            },
            type: 'POST',
            success: function (message) {
                $("#response").removeClass();

                if (message == 'success') {
                    $("#kick_response_text").addClass("text-success");
                    $('#' + enrollmentID + "").remove();
                    $('#kick_response_text').text("Student kicked!");
                } else {
                    $('#kick_response_text').addClass("text-danger");
                    $('#kick_response_text').text("An error occurred.");
                }
            }
        });
    });

    $('#kick_modal_deny_btn').click(function () {
        $('#confirm_kick_modal').modal('hide');
    });

    $('#file_modal_accept_btn').click(function () {
        $('#file_modal_accept_btn').prop('disabled', true);
        $('#file_modal_deny_btn').prop('disabled', true);

        $.ajax({
            url: '/workshop/file/delete',
            data: {
                file_id: fileID
            },
            type: 'POST',
            success: function (message) {

                if (message == 'success') {
                    $('#file_response_text').addClass("text-success");
                    $('#file_response_text').text('File deleted!');
                    $('#file_' + fileID).remove();
                }
            }
        });
    });

    $('#add_student_form').submit(function () {
        event.preventDefault();

        $.ajax({
            url: '/workshop/addstudent',
            data: $('#add_student_form').serialize(),
            type: 'POST',
            success: function (message) {
                if (message == "success") {
                    var studentID = $('#add_student_dropdown').find(':selected').val();
                    var fullName = $('#add_student_dropdown').find(':selected').text().split(' ');
                    var firstName = fullName[0];
                    var lastName = fullName[1];

                    $('#add_student_' + studentID).remove();
                    $('#student_table').append('<tr id="' + studentID +'">' +
                        '<td>' + firstName + '</td>' +
                        '<td>' + lastName + '</td>' +
                        '<td>' +
                        '<div class="btn-toolbar">' + 
                        '<button class="btn btn-danger btn-sm mr-3" value="' + studentID + '" name="kick_btn">Kick student</button>' +
                        '</div></td></tr>');

                    $('#add_student_response').addClass('text-success');
                    $('#add_student_response').text('Student added!');
                }
            }
        });
    });

    $('#file_modal_deny_btn').click(function () {
        $('#confirm_file_delete_modal').modal('hide');
    });

    $('#confirm_kick_modal').on('hidden.bs.modal', function (event) {
        $('#kick_modal_accept_btn').prop('disabled', false);
        $('#kick_modal_deny_btn').prop('disabled', false);
        $('#kick_response_text').text("");
        $('#kick_response_text').removeClass();
    });

    $('#confirm_file_delete_modal').on('hidden.bs.modal', function (event) {
        $('#file_modal_accept_btn').prop('disabled', false);
        $('#file_modal_deny_btn').prop('disabled', false);
        $('#file_response_text').text('');
    });
});