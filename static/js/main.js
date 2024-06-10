function toggleAttendance(studentId) {
    $.ajax({
        url: '/update_attendance/' + studentId,
        type: 'POST',
        success: function(response) {
            updateButton(studentId, response.attended);
        },
        error: function(error) {
            console.error('Error updating attendance:', error);
        }
    });
}

function updateButton(studentId, attended) {
    const button = $('button[onclick="toggleAttendance(' + studentId + ')"]');
    button.text(attended ? 'Attended' : 'Absent');
}
