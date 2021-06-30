var workshopForDeletion = null;
var workshopName = "";

$(document).ready(function () {
    // For workshop deletion
    $('button').click(function () {
        if (this.id == "workshopdel_delete_btn")
            return;

        if (this.id.includes("delete")) {
            var workshopID = $(this).val();
            var workshopName = $(this).data('workshopname');

            $('#workshop_id_modal').text('Are you sure you want to delete "' + workshopName + '"?');
            $('#workshop_delete_modal').modal('show');
            workshopForDeletion = workshopID;
        }
    });

    // Workshop delete handler
    $('#workshopdel_delete_btn').click(function () {
        $('#workshopdel_delete_btn').prop('disabled', true);
        $('#workshopdel_keep_btn').prop('disabled', true);

        $.ajax({
            url: '/workshop/delete',
            data: {
                workshop_id: workshopForDeletion
            },
            type: 'POST',
            success: function (message) {
                if (message == 'success') {
                    $("#" + workshopForDeletion).remove();

                    $('#workshop_id_modal').addClass('text-muted');
                    $('#workshopdel_response_text').addClass('text-success');
                    $('#workshopdel_response_text').text('Workshop #' + workshopForDeletion + ' has been removed!');

                    $('#toast_text').text('Workshop has been deleted!');
                    $('#delete_notification').toast('show');
                    workshopForDeletion = null;
                }
            }
        });
    });

    // Delete modal events
    $('#workshopdel_keep_btn').click(function () {
        $('#workshop_delete_modal').modal('hide');
    });

    $('#workshop_delete_modal').on('hidden.bs.modal', function () {
        $('#workshopdel_delete_btn').prop('disabled', false);
        $('#workshopdel_keep_btn').prop('disabled', false);

        $('#workshop_id_modal').removeClass('text-muted');
        $('#workshopdel_response_text').removeClass('text-success');
        $('#workshopdel_response_text').text('');
        workshopForDeletion = null;
    });
});