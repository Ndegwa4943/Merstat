// formHandler.js - Universal form submission handler
document.addEventListener('DOMContentLoaded', () => {
    // Initialize all forms with data-api-endpoint attribute
    document.querySelectorAll('form[data-api-endpoint]').forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;
            const endpoint = form.getAttribute('data-api-endpoint');
            
            // Disable button during submission
            submitBtn.disabled = true;
            submitBtn.innerHTML = `
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                Submitting...
            `;
            
            try {
                const formData = new FormData(form);
                const response = await fetch(endpoint, {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    // Show success message
                    showAlert('success', result.message);
                    form.reset();
                    
                    // For file inputs, clear them after reset
                    form.querySelectorAll('input[type="file"]').forEach(input => {
                        input.value = '';
                    });
                } else {
                    showAlert('danger', result.message || 'Submission failed');
                }
            } catch (error) {
                showAlert('danger', 'Network error: ' + error.message);
            } finally {
                // Re-enable button
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
            }
        });
    });
});

function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Prepend to the form or to a specific alerts container
    const container = document.getElementById('alerts-container') || document.body;
    container.prepend(alertDiv);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.classList.remove('show');
        setTimeout(() => alertDiv.remove(), 150);
    }, 5000);
}