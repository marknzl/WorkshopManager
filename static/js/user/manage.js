$(document).ready(function () {
    $('button').click(function () {
        var name = $('button').attr('name');

        if (name == 'delete_btn') {
            alert('delete');
        }

        if (name == 'edit_btn') {
            alert('edit');
        }
    });
});