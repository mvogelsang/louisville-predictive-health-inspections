$(document).ready(function () {
    $('#Table').DataTable({
        dom: 'Bfrtip',
        "lengthMenu": [[50, 250, 500, -1], [50, 250, 500, "All"]],
        "order": [[1, "asc"]],
        buttons: [
            'pageLength', 'copy', 'csv', 'excel', 'pdf', 'print'
        ]
    });
});