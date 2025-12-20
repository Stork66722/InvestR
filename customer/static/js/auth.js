// ========== InvestR Authentication JavaScript ==========

document.addEventListener('DOMContentLoaded', function() {
    
    // ========== Password Toggle Functionality ==========
    document.querySelectorAll('.password-toggle').forEach(button => {
        button.addEventListener('click', function() {
            const wrapper = this.closest('.password-input-wrapper');
            const input = wrapper.querySelector('input');
            const eyeIcon = this.querySelector('.eye-icon');
            const eyeOffIcon = this.querySelector('.eye-off-icon');
            
            if (input.type === 'password') {
                input.type = 'text';
                eyeIcon.style.display = 'none';
                eyeOffIcon.style.display = 'block';
            } else {
                input.type = 'password';
                eyeIcon.style.display = 'block';
                eyeOffIcon.style.display = 'none';
            }
        });
    });

    // ========== Password Strength Meter ==========
    const passwordInput = document.getElementById('password');
    const strengthMeter = document.getElementById('passwordStrength');
    
    if (passwordInput && strengthMeter) {
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            
            if (password.length === 0) {
                strengthMeter.style.display = 'none';
                return;
            }
            
            strengthMeter.style.display = 'block';
            
            const strength = calculatePasswordStrength(password);
            const fill = strengthMeter.querySelector('.strength-fill');
            const text = strengthMeter.querySelector('.strength-text');
            
            // Remove all classes
            fill.classList.remove('weak', 'medium', 'strong');
            text.classList.remove('weak', 'medium', 'strong');
            
            // Add appropriate class
            fill.classList.add(strength.level);
            text.classList.add(strength.level);
            text.textContent = strength.text;
        });
    }
    
    // ========== Password Match Validation ==========
    const password2Input = document.getElementById('password2');
    const matchHint = document.getElementById('matchHint');
    
    if (passwordInput && password2Input && matchHint) {
        password2Input.addEventListener('input', function() {
            const password = passwordInput.value;
            const password2 = this.value;
            
            if (password2.length === 0) {
                matchHint.style.display = 'none';
                return;
            }
            
            matchHint.style.display = 'block';
            matchHint.classList.remove('match', 'no-match');
            
            if (password === password2) {
                matchHint.classList.add('match');
                matchHint.textContent = '✓ Passwords match';
            } else {
                matchHint.classList.add('no-match');
                matchHint.textContent = '✗ Passwords do not match';
            }
        });
    }
    
    // ========== Form Loading State ==========
    const forms = document.querySelectorAll('.auth-form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const button = this.querySelector('.btn-loading');
            if (button) {
                button.classList.add('loading');
                button.disabled = true;
            }
        });
    });
    
});

// ========== Password Strength Calculator ==========
function calculatePasswordStrength(password) {
    let score = 0;
    
    // Length
    if (password.length >= 8) score += 1;
    if (password.length >= 12) score += 1;
    
    // Has lowercase
    if (/[a-z]/.test(password)) score += 1;
    
    // Has uppercase
    if (/[A-Z]/.test(password)) score += 1;
    
    // Has numbers
    if (/[0-9]/.test(password)) score += 1;
    
    // Has special characters
    if (/[^A-Za-z0-9]/.test(password)) score += 1;
    
    // Determine strength level
    if (score <= 2) {
        return { level: 'weak', text: 'Weak' };
    } else if (score <= 4) {
        return { level: 'medium', text: 'Medium' };
    } else {
        return { level: 'strong', text: 'Strong' };
    }
}
