// Admin Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Close alert messages after 3 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 3000);
    
    // Student search functionality
    const searchInput = document.getElementById('studentSearch');
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            const searchTerm = this.value.toLowerCase();
            const studentRows = document.querySelectorAll('tbody tr');
            
            studentRows.forEach(function(row) {
                const text = row.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }
    
    // Fee structure form validation
    const feeForm = document.getElementById('addFeeForm');
    if (feeForm) {
        feeForm.addEventListener('submit', function(event) {
            const amountField = document.querySelector('input[name="amount"]');
            
            if (parseFloat(amountField.value) <= 0) {
                event.preventDefault();
                alert('Amount must be greater than zero');
                amountField.focus();
            }
        });
    }
    
    // Print functionality for tables
    const printButton = document.getElementById('printData');
    if (printButton) {
        printButton.addEventListener('click', function() {
            window.print();
        });
    }
});