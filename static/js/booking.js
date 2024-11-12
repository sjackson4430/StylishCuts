document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendar');
    const dateInput = document.getElementById('date');
    const selectedDateTime = document.getElementById('selectedDateTime');
    const submitBtn = document.getElementById('submitBtn');

    // Configure business hours in PST
    const businessHours = {
        daysOfWeek: [1, 2, 3, 4, 5, 6], // Monday - Saturday
        startTime: '08:00',
        endTime: '17:00',
        timeZone: 'America/Los_Angeles'
    };

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'timeGridWeek',
        timeZone: 'America/Los_Angeles',
        slotMinTime: businessHours.startTime,
        slotMaxTime: businessHours.endTime,
        slotDuration: '01:00:00',
        allDaySlot: false,
        selectable: true,
        selectMirror: true,
        unselectAuto: true,
        nowIndicator: true,
        businessHours: businessHours,
        selectConstraint: 'businessHours',
        selectOverlap: false,
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'timeGridWeek,timeGridDay'
        },
        eventSources: [{
            url: '/api/available-slots',
            method: 'GET',
            failure: function(error) {
                console.error('Error fetching booked appointments:', error);
                alert('There was an error fetching booked appointments. Please try again.');
            }
        }],
        select: function(info) {
            const selectedDate = info.start;
            const now = new Date();

            // Use calendar's built-in timezone handling
            if (selectedDate < now) {
                calendar.unselect();
                console.log('Attempted to book past date:', selectedDate);
                alert('Cannot book appointments in the past');
                return;
            }

            // Check if selected day is within business days (Monday-Saturday)
            const day = selectedDate.getDay();
            if (day === 0) { // Sunday
                calendar.unselect();
                console.log('Attempted to book on Sunday:', selectedDate);
                alert('We are closed on Sundays. Please select a day between Monday and Saturday.');
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
                timeZone: 'America/Los_Angeles'
            };
            selectedDateTime.textContent = `Selected: ${selectedDate.toLocaleString('en-US', options)} PST`;
            selectedDateTime.classList.remove('alert-secondary');
            selectedDateTime.classList.add('alert-success');
            submitBtn.disabled = false;

            // Remove previous selection highlights
            calendar.getEvents().forEach(event => {
                if (event.classNames.includes('selection-highlight')) {
                    event.remove();
                }
            });

            // Add new selection highlight
            calendar.addEvent({
                start: info.start,
                end: info.end,
                classNames: ['selection-highlight'],
                display: 'background',
                backgroundColor: 'var(--bs-success)'
            });

            console.log('Time slot selected:', {
                date: selectedDate,
                timeZone: calendar.getOption('timeZone'),
                businessHours: calendar.getOption('businessHours')
            });
        },
        unselect: function() {
            dateInput.value = '';
            selectedDateTime.textContent = 'No time slot selected';
            selectedDateTime.classList.remove('alert-success');
            selectedDateTime.classList.add('alert-secondary');
            submitBtn.disabled = true;

            // Remove selection highlights
            calendar.getEvents().forEach(event => {
                if (event.classNames.includes('selection-highlight')) {
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
            console.log('Form submission attempted without time slot');
            alert('Please select a time slot before submitting.');
        }
    });

    // Update calendar view when service is changed
    document.getElementById('service').addEventListener('change', function() {
        console.log('Service changed, refreshing calendar');
        calendar.refetchEvents();
    });
});
