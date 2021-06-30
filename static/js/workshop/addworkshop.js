// This file contains all AJAX code for workshop adding functionality

$(document).ready(function () {
    var subjectAdded = false;

    $("#add_subject_link").click(function () {
        $("#add_subject").modal('show')
    });

    // Handles adding a workshop
    $("#add_workshop_btn").click(function (event) {
        event.preventDefault();

        $.ajax({
            url: '/workshop/add',
            data: $('#add_workshop_form').serialize(),
            type: 'POST',
            success: function (message) {
                $('#response_txt_workshop').removeClass();
                $("#response_txt_workshop").addClass("mt-3");

                if (message != "error") {
                    var checked = $('#private').prop('checked');

                    $("#response_txt_workshop").addClass("text-success");

                    if (checked) {
                        $("#response_txt_workshop").text("Workshop added! Workshop code: " + message);
                    } else {
                        $("#response_txt_workshop").text("Workshop added!");
                    }

                    $('#toast_text').text('Workshop added!');
                    $('#add_notification').toast('show');

                    $('#add_workshop_form').trigger('reset');
                } else {
                    $("#response_txt_workshop").addClass("text-danger");
                    $("#response_txt_workshop").text("An error occurred, no workshop added!");
                }
            }
        });
    });

    // Handles adding a subject
    $('#add_subject_btn').click(function (event) {
        event.preventDefault();

        var subjectName = $("#subject_name").val();

        if (subjectName == "") {
            $('#subject_add_response').removeClass();
            $("#subject_add_response").addClass("text-warning mt-2");
            $("#subject_add_response").text("Please enter in a valid subject name!");
        } else if (!subjectName.replace(/\s/g, '').length) {
            $('#subject_add_response').removeClass();
            $("#subject_add_response").addClass("text-warning mt-2");
            $("#subject_add_response").text("Please enter in a valid subject name!");
            return;
        } else {
            $.ajax({
                url: '/subject/add',
                data: $('#add_subject_form').serialize(),
                type: 'POST',
                success: function (message) {
                    $('#subject_add_response').removeClass();
                    subjectAdded = true;

                    $('#subject_add_response').addClass("mt-3");

                    if (message != "exists") {
                        var subjectName = $("#subject_name").val();
                        var level = $("#level").val();
                        var subjectID = message;

                        $('#subject').prepend('<option value="' + subjectID + '" selected="selected">' + 'Level ' + level + ' ' + subjectName + '</option>');

                        $("#subject_add_response").addClass("text-success");
                        $("#subject_add_response").text("Level " + level + " " + subjectName + " added as a subject!");

                        $('#toast_text').text('Subject added!');

                        $('#add_notification').toast('show');
                    } else if (message == "exists") {
                        $("#subject_add_response").addClass("text-warning");
                        $("#subject_add_response").text("Subject already exists!")
                    } else {
                        $("#subject_add_response").addClass("text-danger");
                        $("#subject_add_response").text("An error occurred")
                    }
                }
            });
        }
    });

    // Handles refreshing the subject selection dropdown on the main form after a subject has been added
    $('#add_subject').on('hidden.bs.modal', function () {
        function refreshSubjectList() {
            $.ajax({
                url: '/workshop/add',
                success: function (content) {
                    $("body").html(content)
                }
            });
        }

        if (subjectAdded) {
            $('#refreshing').modal('show');
            setTimeout(refreshSubjectList, 3000); // Artificial delay for simulating actual loading
        }
    });
})