$(document).ready(function () {
    $('#save_workshop_btn').click(function (event) {
        event.preventDefault();

        var workshopID = $(this).val();
        var subjectID = $('#subject').val();
        var name = $('#workshop_name').val();
        var location = $('#location').val();
        var summary = $('#summary').val();
        var private = 0;

        var checked = $('#private').prop('checked');

        if (checked) {
            private = 1;
        }

        $('#save_workshop_btn').prop('disabled', true);

        $.ajax({
            url: '/workshop/edit/' + workshopID,
            data: {
                workshop_id: workshopID,
                subject: subjectID,
                name: name,
                location: location,
                private: private,
                summary: summary
            },
            type: 'POST',
            success: function (message) {
                $('#response').removeClass();
                $('#response').addClass('mt-3');

                if (message == "success") {
                    $("#response").addClass("text-success");
                    $("#response").text("Workshop saved!");
                } else if (message != "success" || message != "error") {
                    $("#response").addClass("text-success");
                    $("#response").text("Workshop saved! Newly generated code: " + message);
                } else {
                    $("#response").addClass("text-danger");
                    $("#response").text("An error occurred, no workshop added!");
                }

                $('#toast_text').text('Edits saved!');
                $('#save_notification').toast('show');
                $('#save_workshop_btn').prop('disabled', false);
            }
        });
    });
});