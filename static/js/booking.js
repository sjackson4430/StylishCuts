document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendar');
    const dateInput = document.getElementById('date');
    const selectedDateTime = document.getElementById('selectedDateTime');
    const submitBtn = document.getElementById('submitBtn');
    const errorMessages = document.getElementById('errorMessages');
    const errorText = document.getElementById('errorText');
    const appointmentForm = document.getElementById('appointmentForm');

    console.log('Initializing booking form components...');

    // Configure business hours in PST
    const businessHours = {
        daysOfWeek: [1, 2, 3, 4, 5, 6], // Monday - Saturday
        startTime: '08:00',
        endTime: '17:00',
        timeZone: 'America/Los_Angeles'
    };

    console.log('Setting up business hours:', businessHours);

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
        select: handleTimeSlotSelection,
        unselect: handleTimeSlotUnselection,
        validRange: function(nowDate) {
            let endDate = new Date(nowDate);
            endDate.setDate(endDate.getDate() + 30);
            return {
                start: nowDate,
                end: endDate
            };
        }
    });

    function handleTimeSlotSelection(info) {
        const selectedDate = info.start;
        const now = new Date();

        console.log('Time slot selection initiated:', {
            selectedDate,
            currentTime: now,
            timeZone: calendar.getOption('timeZone')
        });

        if (selectedDate < now) {
            calendar.unselect();
            console.warn('Selection rejected: Past date selected:', selectedDate);
            showError('Cannot book appointments in the past');
            return;
        }

        const day = selectedDate.getDay();
        if (day === 0) { // Sunday
            calendar.unselect();
            console.warn('Selection rejected: Sunday booking attempted');
            showError('We are closed on Sundays. Please select a day between Monday and Saturday.');
            return;
        }

        updateSelectedDateTime(selectedDate);
        updateCalendarHighlight(info);

        console.log('Time slot selection completed successfully:', {
            date: selectedDate,
            formattedDate: dateInput.value
        });
    }

    function handleTimeSlotUnselection() {
        console.log('Time slot unselection initiated');
        clearSelectedDateTime();
        removeCalendarHighlights();
        console.log('Time slot unselection completed');
    }

    function updateSelectedDateTime(selectedDate) {
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
    }

    function clearSelectedDateTime() {
        dateInput.value = '';
        selectedDateTime.textContent = 'No time slot selected';
        selectedDateTime.classList.remove('alert-success');
        selectedDateTime.classList.add('alert-secondary');
        submitBtn.disabled = true;
    }

    function updateCalendarHighlight(info) {
        removeCalendarHighlights();
        calendar.addEvent({
            start: info.start,
            end: info.end,
            classNames: ['selection-highlight'],
            display: 'background',
            backgroundColor: 'var(--bs-success)'
        });
    }

    function removeCalendarHighlights() {
        calendar.getEvents().forEach(event => {
            if (event.classNames.includes('selection-highlight')) {
                event.remove();
            }
        });
    }

    function showError(message) {
        console.error('Showing error message:', message);
        errorText.textContent = message;
        errorMessages.style.display = 'block';
        setTimeout(() => {
            errorMessages.style.display = 'none';
        }, 5000);
    }

    function validateForm() {
        console.log('Starting form validation');
        const requiredFields = ['client_name', 'client_email', 'service', 'date'];
        
        // Check required fields
        for (const field of requiredFields) {
            const input = document.getElementById(field);
            if (!input || !input.value.trim()) {
                console.warn(`Validation failed: Missing required field - ${field}`);
                showError(`Please fill in all required fields`);
                return false;
            }
        }

        // Validate email format
        const emailInput = document.getElementById('client_email');
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(emailInput.value.trim())) {
            console.warn('Validation failed: Invalid email format');
            showError('Please enter a valid email address');
            return false;
        }

        console.log('Form validation passed successfully');
        return true;
    }

    async function handleFormSubmission(e) {
        e.preventDefault();
        console.log('Form submission initiated');

        const submitBtn = this.querySelector('button[type="submit"]');
        const buttonText = submitBtn.querySelector('.button-text');
        const spinner = submitBtn.querySelector('.spinner-border');
        
        try {
            if (!validateForm()) {
                console.warn('Form submission blocked: Validation failed');
                return;
            }
            
            // Update button state
            submitBtn.disabled = true;
            buttonText.textContent = 'Booking...';
            spinner.classList.remove('d-none');
            
            console.log('Sending form data to server...');
            const formData = new FormData(this);
            const response = await fetch('/booking', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const result = await response.json();
            console.log('Server response received:', result);
            
            if (response.ok) {
                console.log('Booking successful, redirecting...');
                window.location.href = result.redirect || '/';
            } else {
                throw new Error(result.error || 'Booking failed');
            }
        } catch (error) {
            console.error('Booking submission error:', error);
            showError(error.message);
        } finally {
            // Reset button state
            submitBtn.disabled = false;
            buttonText.textContent = 'Book Appointment';
            spinner.classList.add('d-none');
            console.log('Form submission completed');
        }
    }

    // Initialize calendar
    calendar.render();
    console.log('Calendar initialization completed');

    // Set up event listeners
    appointmentForm.addEventListener('submit', handleFormSubmission);

    const serviceSelect = document.getElementById('service');
    serviceSelect.addEventListener('change', function() {
        console.log('Service selection changed:', {
            newService: this.value,
            serviceName: this.options[this.selectedIndex].text
        });
        calendar.refetchEvents();
    });

    console.log('All event listeners initialized');
});
