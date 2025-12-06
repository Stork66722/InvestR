/**
 * Global utility functions for Admin pages.
 */

// 1. Shorthand for document.getElementById
const $ = id => document.getElementById(id);

// 2. Clear alerts (must be called from the page with the specific IDs)
function clearAlerts(warnEl, okEl) {
    warnEl.style.display = 'none';
    okEl.style.display = 'none';
}

// 3. Helper for Django CSRF token (required for POST requests)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}