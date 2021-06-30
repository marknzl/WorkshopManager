$(document).ready(function () {
    $('button').click(function () {
        var name = $(this).attr('name');

        if (name == 'approve_btn') {
            var promotionID = $(this).val();

            var approve = confirm("Are you sure you want to approve that promotion request?");

            if (!approve)
                return;

            $.ajax({
                url: '/user/promotionrequests/approve',
                data: {
                    promotion_id: promotionID
                },
                type: 'POST',
                success: function (message) {
                    if (message == 'success') {
                        $('#' + promotionID).remove();
                    }
                }
            });
        } else if (name == 'deny_btn') {
            var promotionID = $(this).val();

            $.ajax({
                url: '/user/promotionrequests/deny',
                data: {
                    promotion_id: promotionID
                },
                type: 'POST',
                success: function (message) {
                    if (message == 'success') {
                        $('#' + promotionID).remove();
                    }
                }
            });
        }
    });
});