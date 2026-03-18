// Form Validation for Login and Create Profile
document.addEventListener('DOMContentLoaded', () => {
    // Login Form Validation
    const loginForm = document.querySelector('#login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            const email = loginForm.querySelector('#email').value;
            const password = loginForm.querySelector('#password').value;
            const errorDiv = loginForm.querySelector('#error-message');

            if (!validateEmail(email)) {
                e.preventDefault();
                showAlert(errorDiv, 'Please enter a valid email address.', 'error');
            } else if (password.length < 6) {
                e.preventDefault();
                showAlert(errorDiv, 'Password must be at least 6 characters.', 'error');
            }
        });
    }

    // Create Profile Form Validation
    const profileForm = document.querySelector('#profile-form');
    if (profileForm) {
        profileForm.addEventListener('submit', (e) => {
            const name = profileForm.querySelector('#name').value;
            const email = profileForm.querySelector('#email').value;
            const password = profileForm.querySelector('#password').value;
            const errorDiv = profileForm.querySelector('#error-message');

            if (name.trim() === '') {
                e.preventDefault();
                showAlert(errorDiv, 'Name is required.', 'error');
            } else if (!validateEmail(email)) {
                e.preventDefault();
                showAlert(errorDiv, 'Please enter a valid email address.', 'error');
            } else if (password.length < 6) {
                e.preventDefault();
                showAlert(errorDiv, 'Password must be at least 6 characters.', 'error');
            }
        });
    }

    // Updated: Enhanced Feedback Form Validation
    const feedbackForm = document.querySelector('#feedback-form');
    if (feedbackForm) {
        feedbackForm.addEventListener('submit', (e) => {
            const feedback = feedbackForm.querySelector('#feedback').value;
            const errorDiv = feedbackForm.querySelector('#error-message');
            if (feedback.trim() === '') {
                e.preventDefault();
                showAlert(errorDiv, 'Feedback is required.', 'error');
            } else {
                // Updated: Log successful submission attempt for debugging
                console.log('Feedback form submitted:', feedback);
            }
        });
    }

    // Event Filtering on Attendee Dashboard
    const eventFilter = document.querySelector('#event-filter');
    if (eventFilter) {
        eventFilter.addEventListener('input', () => {
            const filterValue = eventFilter.value.toLowerCase();
            const eventCards = document.querySelectorAll('.event-card');

            eventCards.forEach(card => {
                const title = card.querySelector('.event-title').textContent.toLowerCase();
                const date = card.querySelector('.event-date').textContent;
                if (title.includes(filterValue) || date.includes(filterValue)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }

    // Fade-in Animation for Page Elements
    const elements = document.querySelectorAll('.fade-in');
    elements.forEach(element => {
        element.classList.add('opacity-0');
        setTimeout(() => {
            element.classList.remove('opacity-0');
            element.classList.add('opacity-100');
        }, 100);
    });
});

// Email Validation Function
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Show Alert Function
function showAlert(element, message, type) {
    element.textContent = message;
    element.className = `text-center p-2 mb-4 rounded ${type === 'error' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`;
    setTimeout(() => {
        element.textContent = '';
        element.className = 'hidden';
    }, 3000);
}

// RSVP Button Click Feedback
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('rsvp-button')) {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'fixed top-4 right-4 p-4 bg-green-100 text-green-700 rounded shadow';
        alertDiv.textContent = 'RSVP submitted successfully!';
        document.body.appendChild(alertDiv);
        setTimeout(() => alertDiv.remove(), 3000);

}

});

// Updated: Refined Feedback Button Click Feedback
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('feedback-button')) {
        const feedbackForm = document.querySelector('#feedback-form');
        const feedback = feedbackForm ? feedbackForm.querySelector('#feedback').value : '';
        if (feedback.trim() !== '') {
            const alertDiv = document.createElement('div');
            alertDiv.className = 'fixed top-4 right-4 p-4 bg-green-100 text-green-700 rounded shadow';
            alertDiv.textContent = 'Feedback submitted successfully!';
            document.body.appendChild(alertDiv);
            setTimeout(() => alertDiv.remove(), 3000);
            // Updated: Log for debugging
            console.log('Feedback button clicked, submitting form');
        } else {
            // Updated: Prevent submission and show error if feedback is empty
            e.preventDefault();
            const errorDiv = feedbackForm.querySelector('#error-message');
            showAlert(errorDiv, 'Feedback is required.', 'error');
            console.log('Feedback button clicked, but feedback is empty');
        }
    }
});
