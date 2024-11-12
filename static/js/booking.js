document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendar');
    const dateInput = document.getElementById('date');
    const selectedDateTime = document.getElementById('selectedDateTime');
    const submitBtn = document.getElementById('submitBtn');
    const errorMessages = document.getElementById('errorMessages');
    const errorText = document.getElementById('errorText');

    // Configure business hours in PST
    const businessHours = {
        daysOfWeek: [1, 2, 3, 4, 5, 6], // Monday - Saturday
        startTime: '08:00',
        endTime: '17:00',
        timeZone: 'America/Los_Angeles'
    };

    console.log('Initializing calendar with business hours:', businessHours);

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
                showError('Failed to load available appointment slots. Please refresh the page.');
            }
        }],
        select: function(info) {
            const selectedDate = info.start;
            const now = new Date();

            console.log('Time slot selected:', {
                selectedDate,
                currentTime: now,
                timeZone: calendar.getOption('timeZone')
            });

            // Use calendar's built-in timezone handling
            if (selectedDate < now) {
                calendar.unselect();
                console.warn('Attempted to book past date:', selectedDate);
                showError('Cannot book appointments in the past');
                return;
            }

            // Check if selected day is within business days (Monday-Saturday)
            const day = selectedDate.getDay();
            if (day === 0) { // Sunday
                calendar.unselect();
                console.warn('Attempted to book on Sunday:', selectedDate);
                showError('We are closed on Sundays. Please select a day between Monday and Saturday.');
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

            console.log('Time slot successfully selected:', {
                date: selectedDate,
                timeZone: calendar.getOption('timeZone'),
                businessHours: calendar.getOption('businessHours')
            });
        },
        unselect: function() {
            console.log('Time slot unselected');
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
    console.log('Calendar initialized successfully');

    // Helper function to show error messages
    function showError(message) {
        errorText.textContent = message;
        errorMessages.style.display = 'block';
        setTimeout(() => {
            errorMessages.style.display = 'none';
        }, 5000);
    }

    // Form validation and submission handling
    const appointmentForm = document.getElementById('appointmentForm');
    appointmentForm.addEventListener('submit', function(e) {
        console.log('Form submission attempted');

        if (!dateInput.value) {
            e.preventDefault();
            console.warn('Form submission blocked: No time slot selected');
            showError('Please select a time slot before submitting.');
            return;
        }

        const formData = new FormData(this);
        console.log('Form data collected:', {
            name: formData.get('client_name'),
            email: formData.get('client_email'),
            service: formData.get('service'),
            date: formData.get('date')
        });
    });

    // Service change handler
    const serviceSelect = document.getElementById('service');
    serviceSelect.addEventListener('change', function() {
        console.log('Service changed:', {
            newService: this.value,
            serviceName: this.options[this.selectedIndex].text
        });
        calendar.refetchEvents();
    });
});
