$(document).ready(function () {
    // Detect changes in the reg_status dropdown
    $('#id_reg_status').on('change', function () {
        var regStatus = $(this).val();
        console.log('reg_status changed to:', regStatus);
        // Perform any additional actions based on the changed value
    });

    // Function to calculate the difference between two datetime fields
    function calculateDuration() {
        var fromDate = $('#id_from_date').val();
        var toDate = $('#id_to_date').val();
        console.log(fromDate)
        console.log(toDate)
        if (fromDate && toDate) {
            var fromDateTime = new Date(fromDate);
            var toDateTime = new Date(toDate);

            if (fromDateTime <= toDateTime) {
                var diffMs = toDateTime - fromDateTime; // Difference in milliseconds
                var diffHours = Math.floor(diffMs / (1000 * 60 * 60));
                var diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));

                var duration = diffHours + ' hours ' + diffMinutes + ' minutes';
                $('#id_reg_duration').val(duration);
            } else {
                alert('From Date cannot be later than To Date.');
                $('#id_reg_duration').val('');
            }
        }
    }

    // Attach change event handlers to from_date and to_date fields
    $('#id_from_date, #id_to_date').on('change', function () {
        calculateDuration();
    });
});
