document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendar');
    const dateInput = document.getElementById('date');
    const selectedDateTime = document.getElementById('selectedDateTime');
    const submitBtn = document.getElementById('submitBtn');

    // Get business hours in PST
    const businessHours = {
        startTime: '08:00',
        endTime: '17:00',
        daysOfWeek: [1, 2, 3, 4, 5, 6] // Monday - Saturday
    };

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'timeGridWeek',
        slotMinTime: businessHours.startTime,
        slotMaxTime: businessHours.endTime,
        slotDuration: '01:00:00',
        allDaySlot: false,
        selectable: true,
        selectMirror: true,
        unselectAuto: true,
        businessHours: businessHours,
        selectConstraint: 'businessHours',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'timeGridWeek,timeGridDay'
        },
        select: function(info) {
            const selectedDate = info.start;
            const now = new Date();
            
            // Prevent selecting past dates
            if (selectedDate < now) {
                calendar.unselect();
                return;
            }

            // Update the hidden input and display
            dateInput.value = selectedDate.toISOString().slice(0, 16);
            selectedDateTime.textContent = `Selected: ${selectedDate.toLocaleDateString()} at ${selectedDate.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}`;
            submitBtn.disabled = false;
        },
        unselect: function() {
            dateInput.value = '';
            selectedDateTime.textContent = 'No time slot selected';
            submitBtn.disabled = true;
        },
        validRange: function(nowDate) {
            // Allow booking only for the next 30 days
            let endDate = new Date(nowDate);
            endDate.setDate(endDate.getDate() + 30);
            return {
                start: nowDate,
                end: endDate
            };
        }
    });

    calendar.render();

    // Disable form submission if no time slot is selected
    document.getElementById('appointmentForm').addEventListener('submit', function(e) {
        if (!dateInput.value) {
            e.preventDefault();
            alert('Please select a time slot before submitting.');
        }
    });
});
