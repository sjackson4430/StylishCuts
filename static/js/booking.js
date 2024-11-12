document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendar');
    const dateInput = document.getElementById('date');
    const selectedDateTime = document.getElementById('selectedDateTime');
    const submitBtn = document.getElementById('submitBtn');

    // Get business hours in PST
    const businessHours = {
        daysOfWeek: [1, 2, 3, 4, 5, 6], // Monday - Saturday
        startTime: '08:00',
        endTime: '17:00'
    };

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'timeGridWeek',
        plugins: ['timeGrid', 'interaction'],
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
        events: '/api/available-slots',
        select: function(info) {
            const selectedDate = info.start;
            const now = new Date();
            
            // Prevent selecting past dates
            if (selectedDate < now) {
                calendar.unselect();
                alert('Cannot book appointments in the past');
                return;
            }

            // Check if the selected time is within business hours
            const hour = selectedDate.getHours();
            if (hour < 8 || hour >= 17) {
                calendar.unselect();
                alert('Please select a time between 8 AM and 5 PM PST');
                return;
            }

            // Update the hidden input and display
            dateInput.value = selectedDate.toISOString();
            const options = {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                timeZoneName: 'short'
            };
            selectedDateTime.textContent = `Selected: ${selectedDate.toLocaleString('en-US', options)} PST`;
            submitBtn.disabled = false;

            // Highlight the selected time slot
            calendar.unselect();
            calendar.addEvent({
                start: info.start,
                end: info.end,
                display: 'background',
                color: '#28a745'
            });
        },
        unselect: function() {
            dateInput.value = '';
            selectedDateTime.textContent = 'No time slot selected';
            submitBtn.disabled = true;
            // Remove any temporary selection highlights
            calendar.getEvents().forEach(event => {
                if (event.display === 'background' && event.backgroundColor === '#28a745') {
                    event.remove();
                }
            });
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

    // Update calendar view when service is changed
    document.getElementById('service').addEventListener('change', function() {
        calendar.refetchEvents();
    });
});
