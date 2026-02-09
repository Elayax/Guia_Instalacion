document.addEventListener('DOMContentLoaded', function() {
    // Clock Update
    function updateClock() {
        const now = new Date();
        const clockEl = document.getElementById('clock');
        const dateEl = document.getElementById('date');
        
        if (clockEl) {
            clockEl.textContent = now.toLocaleTimeString('en-US', { hour12: false });
        }
        
        if (dateEl) {
            const options = { year: 'numeric', month: '2-digit', day: '2-digit' };
            // Format YYYY-MM-DD manually if needed or just use locale date string
            dateEl.textContent = now.toISOString().split('T')[0];
        }
    }

    // Update every second
    setInterval(updateClock, 1000);
    updateClock(); // Initial call
});
