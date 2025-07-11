document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('contactForm');
    const formStatus = document.getElementById('formStatus');

    // פונקציות עזר להצגת/הסתרת הודעות שגיאה
    function displayError(fieldId, message) {
        const errorElement = document.getElementById(fieldId + 'Error');
        if (errorElement) {
            errorElement.textContent = message;
        }
    }

    function clearError(fieldId) {
        const errorElement = document.getElementById(fieldId + 'Error');
        if (errorElement) {
            errorElement.textContent = '';
        }
    }

    function clearAllErrors() {
        const errorMessages = document.querySelectorAll('.error-message');
        errorMessages.forEach(el => el.textContent = '');
        formStatus.textContent = '';
        formStatus.className = '';
    }

    // ולידציה של הטופס
    function validateForm() {
        clearAllErrors();
        let isValid = true;

        const name = document.getElementById('name').value.trim();
        const email = document.getElementById('email').value.trim();
        const phone = document.getElementById('phone').value.trim();
        const message = document.getElementById('message').value.trim();

        if (!name) {
            displayError('name', 'שדה שם הוא חובה.');
            isValid = false;
        }

        if (!email) {
            displayError('email', 'שדה אימייל הוא חובה.');
            isValid = false;
        } else {
            // ולידציית פורמט אימייל בסיסית
            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailPattern.test(email)) {
                displayError('email', 'כתובת אימייל אינה תקינה.');
                isValid = false;
            }
        }

        if (phone) {
            // ולידציית פורמט טלפון בסיסית (מספרים בלבד, אופציונלי מקף)
            const phonePattern = /^[0-9\-]+$/;
            if (!phonePattern.test(phone)) {
                displayError('phone', 'מספר טלפון יכול להכיל רק מספרים ומקפים.');
                isValid = false;
            }
        }

        if (!message) {
            displayError('message', 'שדה הודעה הוא חובה.');
            isValid = false;
        }

        return isValid;
    }

    form.addEventListener('submit', async function (event) {
        event.preventDefault(); // מונע שליחה רגילה של הטופס

        if (!validateForm()) {
            formStatus.textContent = 'אנא תקן את השגיאות בטופס.';
            formStatus.className = 'error';
            return;
        }

        formStatus.textContent = 'שולח...';
        formStatus.className = '';

        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        try {
            const response = await fetch('/submit_form', { // הנתיב לשרת ה-Python
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            if (response.ok) {
                const result = await response.json();
                formStatus.textContent = result.message || 'הטופס נשלח בהצלחה!';
                formStatus.className = 'success';
                form.reset(); // איפוס הטופס
                clearAllErrors(); // ניקוי כל הודעות השגיאה כולל שגיאות שדה
            } else {
                const errorResult = await response.json();
                formStatus.textContent = errorResult.message || 'אירעה שגיאה בשליחת הטופס. נסה שוב מאוחר יותר.';
                formStatus.className = 'error';
            }
        } catch (error) {
            console.error('Error submitting form:', error);
            formStatus.textContent = 'אירעה שגיאת רשת. בדוק את חיבור האינטרנט שלך.';
            formStatus.className = 'error';
        }
    });
});