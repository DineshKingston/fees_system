// Student Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Payment form handling
    const paymentForm = document.getElementById('paymentForm');
    if (paymentForm) {
        const paymentMethodSelect = document.getElementById('payment_method');
        const transactionIdField = document.getElementById('transaction_id_field');
        
        // Show/hide transaction ID field based on payment method
        if (paymentMethodSelect && transactionIdField) {
            paymentMethodSelect.addEventListener('change', function() {
                const selectedMethod = this.value;
                
                if (selectedMethod === 'cash') {
                    transactionIdField.style.display = 'none';
                } else {
                    transactionIdField.style.display = 'block';
                }
            });
            
            // Trigger on page load
            paymentMethodSelect.dispatchEvent(new Event('change'));
        }
        
        // Validate payment amount
        // Validate payment amount
paymentForm.addEventListener('submit', function(event) {
    const amountField = document.querySelector('input[name="amount"]');
    const maxAmount = parseFloat(amountField.getAttribute('max') || 0);
    const enteredAmount = parseFloat(amountField.value);
    
    if (enteredAmount <= 0) {
        event.preventDefault();
        alert('Amount must be greater than zero');
        amountField.focus();
        return;
    }
    
    if (enteredAmount > maxAmount) {
        event.preventDefault();
        alert('Amount cannot exceed the remaining balance');
        amountField.focus();
        return;
    }
});
    }
    
    // Fee selection handling
    const feeSelect = document.getElementById('feeSelect');
    if (feeSelect) {
        feeSelect.addEventListener('change', function() {
            const selectedOption = this.options[this.selectedIndex];
            const amountField = document.getElementById('amount');
            
            if (selectedOption && amountField) {
                const remainingAmount = selectedOption.getAttribute('data-remaining');
                if (remainingAmount) {
                    amountField.value = remainingAmount;
                    amountField.setAttribute('max', remainingAmount);
                }
            }
        });
    }
    
    // Print receipt functionality
    const printButtons = document.querySelectorAll('.print-receipt');
    if (printButtons.length > 0) {
        printButtons.forEach(button => {
            button.addEventListener('click', function() {
                const receiptId = this.getAttribute('data-receipt-id');
                const receiptElement = document.getElementById(receiptId);
                
                if (receiptElement) {
                    const printWindow = window.open('', '_blank');
                    printWindow.document.write('<html><head><title>Payment Receipt</title>');
                    printWindow.document.write('<link rel="stylesheet" href="/static/css/styles.css">');
                    printWindow.document.write('<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">');
                    printWindow.document.write('</head><body class="p-4">');
                    printWindow.document.write('<h3 class="text-center mb-4">Fee Payment Receipt</h3>');
                    printWindow.document.write(receiptElement.innerHTML);
                    printWindow.document.write('</body></html>');
                    
                    setTimeout(function() {
                        printWindow.document.close();
                        printWindow.print();
                    }, 500);
                }
            });
        });
    }
    // Add this to student.js after the existing code
const paymentModal = document.getElementById('paymentModal');
if (paymentModal) {
    paymentModal.addEventListener('show.bs.modal', function (event) {
        // Button that triggered the modal
        const button = event.relatedTarget;
        
        // Extract info from data attributes
        const feeId = button.getAttribute('data-fee-id');
        const feeName = button.getAttribute('data-fee-name');
        const amount = button.getAttribute('data-amount');
        
        // Update the modal's content
        const modalFeeId = document.getElementById('student_fee_id');
        const modalFeeName = document.getElementById('fee_name');
        const modalAmount = document.getElementById('amount');
        
        modalFeeId.value = feeId;
        modalFeeName.value = feeName;
        modalAmount.value = amount;
        modalAmount.setAttribute('max', amount);
    });
}
});