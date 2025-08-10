// QR Attendance System JavaScript

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // QR Code expiration countdown timer
    const countdownEl = document.getElementById('countdown');
    if (countdownEl) {
        let timeLeft = 10 * 60; // 5 minutes in seconds
        
        const countdownTimer = setInterval(function() {
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            
            // Format time as MM:SS
            countdownEl.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
            
            // Decrease time
            timeLeft--;
            
            // Add warning class when under 1 minute
            if (timeLeft < 60) {
                countdownEl.classList.add('text-danger');
                countdownEl.classList.add('fw-bold');
            }
            
            // If timer reaches 0, show alert and reload
            if (timeLeft < 0) {
                clearInterval(countdownTimer);
                alert('This QR code has expired! Please generate a new one.');
                location.reload();
            }
        }, 1000);
    }
    // QR Code download functionality
    const downloadQrBtn = document.getElementById('download-qr');
    if (downloadQrBtn) {
        downloadQrBtn.addEventListener('click', function() {
            const imgData = this.getAttribute('data-img');
            const sessionName = this.getAttribute('data-session');
            
            // Create a temporary link element
            const link = document.createElement('a');
            link.href = `data:image/png;base64,${imgData}`;
            link.download = `QR_${sessionName.replace(/\s+/g, '_')}.png`;
            
            // Trigger the download
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        });
    }

    // Search functionality for attendance table
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            const filter = this.value.toLowerCase();
            const table = document.getElementById('attendanceTable');
            const rows = table.getElementsByTagName('tr');
            
            // Loop through all table rows
            for (let i = 0; i < rows.length; i++) {
                let found = false;
                const cells = rows[i].getElementsByTagName('td');
                
                // Loop through all cells in current row
                for (let j = 0; j < cells.length; j++) {
                    const cellText = cells[j].textContent || cells[j].innerText;
                    
                    if (cellText.toLowerCase().indexOf(filter) > -1) {
                        found = true;
                        break;
                    }
                }
                
                // Show/hide row based on search match
                if (found) {
                    rows[i].style.display = '';
                } else {
                    rows[i].style.display = 'none';
                }
            }
        });
    }

    // Export attendance to CSV
    const exportCsvBtn = document.getElementById('exportCsv');
    if (exportCsvBtn) {
        exportCsvBtn.addEventListener('click', function() {
            const table = document.getElementById('attendanceTable');
            if (!table) return;
            
            const rows = table.getElementsByTagName('tr');
            if (rows.length === 0) {
                alert('No data to export');
                return;
            }
            
            let csv = 'Session,Student ID,Registration Number,Name,Timestamp\n';
            
            // Loop through each row
            for (let i = 0; i < rows.length; i++) {
                // Skip rows that are hidden due to filtering
                if (rows[i].style.display === 'none') continue;
                
                const cells = rows[i].getElementsByTagName('td');
                let rowData = [];
                
                // Skip rows with "No attendances recorded" message
                if (cells.length === 4) {
                    for (let j = 0; j < cells.length; j++) {
                        // Add quotes around data to handle commas in content
                        let cellData = cells[j].textContent || cells[j].innerText;
                        rowData.push(`"${cellData.trim()}"`);
                    }
                    csv += rowData.join(',') + '\n';
                }
            }
            
            // Create a CSV file and trigger download
            const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            const url = URL.createObjectURL(blob);
            
            link.setAttribute('href', url);
            link.setAttribute('download', `attendance_export_${new Date().toISOString().slice(0,10)}.csv`);
            link.style.visibility = 'hidden';
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        });
    }
});
