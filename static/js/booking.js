document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendar');
    const dateInput = document.getElementById('date');
    const selectedDateTime = document.getElementById('selectedDateTime');
    const submitBtn = document.getElementById('submitBtn');
    const errorMessages = document.getElementById('errorMessages');
    const errorText = document.getElementById('errorText');
    const appointmentForm = document.getElementById('appointmentForm');

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

            if (selectedDate < now) {
                calendar.unselect();
                console.warn('Attempted to book past date:', selectedDate);
                showError('Cannot book appointments in the past');
                return;
            }

            const day = selectedDate.getDay();
            if (day === 0) { // Sunday
                calendar.unselect();
                console.warn('Attempted to book on Sunday:', selectedDate);
                showError('We are closed on Sundays. Please select a day between Monday and Saturday.');
                return;
            }

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

            calendar.getEvents().forEach(event => {
                if (event.classNames.includes('selection-highlight')) {
                    event.remove();
                }
            });

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

            calendar.getEvents().forEach(event => {
                if (event.classNames.includes('selection-highlight')) {
                    event.remove();
                }
            });
        },
        validRange: function(nowDate) {
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

    function showError(message) {
        errorText.textContent = message;
        errorMessages.style.display = 'block';
        setTimeout(() => {
            errorMessages.style.display = 'none';
        }, 5000);
    }

    function validateForm() {
        const requiredFields = ['client_name', 'client_email', 'service', 'date'];
        for (const field of requiredFields) {
            const input = document.getElementById(field);
            if (!input || !input.value.trim()) {
                showError(`Please fill in all required fields`);
                return false;
            }
        }

        const emailInput = document.getElementById('client_email');
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(emailInput.value.trim())) {
            showError('Please enter a valid email address');
            return false;
        }

        return true;
    }

    appointmentForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const submitBtn = document.getElementById('submitBtn');
        const buttonText = submitBtn.querySelector('.button-text');
        const spinner = submitBtn.querySelector('.spinner-border');
        
        try {
            if (!validateForm()) {
                return;
            }
            
            submitBtn.disabled = true;
            buttonText.textContent = 'Booking...';
            spinner.classList.remove('d-none');
            
            const formData = new FormData(this);
            const response = await fetch('/booking', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const result = await response.json();
            
            if (response.ok) {
                console.log('Booking successful:', result);
                window.location.href = result.redirect || '/';
            } else {
                throw new Error(result.error || 'Booking failed');
            }
        } catch (error) {
            console.error('Booking error:', error);
            showError(error.message);
        } finally {
            submitBtn.disabled = false;
            buttonText.textContent = 'Book Appointment';
            spinner.classList.add('d-none');
        }
    });

    const serviceSelect = document.getElementById('service');
    serviceSelect.addEventListener('change', function() {
        console.log('Service changed:', {
            newService: this.value,
            serviceName: this.options[this.selectedIndex].text
        });
        calendar.refetchEvents();
    });
});
