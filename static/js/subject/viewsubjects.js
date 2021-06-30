var subjectID = null;
var fullSubject = "";

$(document).ready(function () {
    $('button').click(function () {
        var name = $(this).attr('name');

        if (name == "delete_btn") {
            subjectID = $(this).val();
            fullSubject = $(this).data('fullsubject');

            $('#subject_id_modal').text('Are you sure you want to delete "' + fullSubject + '"?');
            $('#confirm_deletion_modal').modal('show');
        }
    });

    $('#modal_accept_btn').click(function () {
        $('#modal_accept_btn').prop('disabled', true);
        $('#modal_deny_btn').prop('disabled', true);

        $.ajax({
            url: '/subject/delete',
            data: {
                subject_id: subjectID
            },
            type: 'POST',
            success: function (message) {
                if (message == "success") {
                    $("#" + subjectID).remove();
                    $('#warning_text').text('');

                    $('#subject_id_modal').addClass('text-muted');
                    $('#response_text').addClass('text-success');
                    $('#response_text').text('Subject #' + subjectID + ' has been removed!');
                }
            }
        });
    });

    $('#modal_deny_btn').click(function () {
        $('#confirm_deletion_modal').modal('hide');
    });

    $('#confirm_deletion_modal').on('hidden.bs.modal', function () {
        $('#modal_accept_btn').prop('disabled', false);
        $('#modal_deny_btn').prop('disabled', false);
        $('#modal_accept_btn').show();
        $('#modal_deny_btn').show();
        $('#warning_text').show();
        $('#subject_id_modal').removeClass('text-muted');
        $('#response_text').removeClass('text-success');
        $('#response_text').text('');
    });
});