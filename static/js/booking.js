document.addEventListener('DOMContentLoaded', function() {
    // Set minimum date to today
    const dateInput = document.querySelector('input[type="datetime-local"]');
    if (dateInput) {
        const today = new Date();
        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, '0');
        const day = String(today.getDate()).padStart(2, '0');
        dateInput.min = `${year}-${month}-${day}T09:00`;
        
        // Set maximum date to 30 days from now
        const maxDate = new Date();
        maxDate.setDate(maxDate.getDate() + 30);
        const maxYear = maxDate.getFullYear();
        const maxMonth = String(maxDate.getMonth() + 1).padStart(2, '0');
        const maxDay = String(maxDate.getDate()).padStart(2, '0');
        dateInput.max = `${maxYear}-${maxMonth}-${maxDay}T20:00`;
    }
});
