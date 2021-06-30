// This file contains all AJAX code for subject adding functionality

$(document).ready(function () {
    $('#add_subject_btn').click(function (event) {
        event.preventDefault();

        var subjectName = $("#subject_name").val();

        if (subjectName == "") {
            $('#response').removeClass();
            $("#response").addClass("text-warning");
            $("#response").text("Please enter in a valid subject name!");
        } else if (!subjectName.replace(/\s/g, '').length) {
            $('#response').removeClass();
            $("#response").addClass("text-warning mt-2");
            $("#response").text("Please enter in a valid subject name!");
            return;
        } else {
            $.ajax({
                url: '/subject/add',
                data: $('form').serialize(),
                type: 'POST',
                success: function (message) {
                    $('#response').removeClass();

                    if (message != "exists") {
                        var subjectName = $("#subject_name").val();
                        var level = $("#level").val();

                        $("#response").addClass("text-success");
                        $("#response").text("Level " + level + " " + subjectName + " added as a subject!");
                    } else if (message == "exists") {
                        $("#response").addClass("text-warning");
                        $("#response").text("Subject already exists!")
                    } else {
                        $("#response").addClass("text-danger");
                        $("#response").text("An error occurred")
                    }
                }
            });
        }
    });
});