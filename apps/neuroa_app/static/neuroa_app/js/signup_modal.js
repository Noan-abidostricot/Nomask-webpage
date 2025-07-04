function activateLoginTab() {
    window.loginTab.classList.remove('unselected');
    window.loginTab.classList.add('selected');
    window.signUpTab.classList.remove('selected');
    window.signUpTab.classList.add('unselected');
    window.signUpDiv.classList.add('hidden');
    window.loginDiv.classList.remove('hidden');
    window.loginForm.classList.remove('hidden');
    window.modalTitle.textContent = 'Bienvenue';
    return false;
}

function activateSignUpTab() {
    window.signUpTab.classList.remove('unselected');
    window.signUpTab.classList.add('selected');
    window.loginTab.classList.remove('selected');
    window.loginTab.classList.add('unselected');
    window.loginDiv.classList.add('hidden');
    window.signUpDiv.classList.remove('hidden');
    window.signUpForm.classList.remove('hidden');
    window.modalTitle.textContent = 'Inscrivez-vous';
    return false;
}

function validateEmail() {
    const email = window.emailInput.value;
    const maxLength = 320;
    const userRegex = /^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*$|^"([\001-\010\013\014\016-\037!#-\]-\177]|\\[\001-\011\013\014\016-\177])*"$/i;
    const domainRegex = /^(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z0-9-]{2,63})$/i;
    const literalRegex = /^\[([A-F0-9:.]+)\]$/i;
    const domainAllowlist = ['localhost'];

    if (email === '') {
        window.emailError.textContent = '';
        return false;
    }

    if (!email || !email.includes('@') || email.length > maxLength) {
        window.emailError.textContent = 'Entrez une adresse email valide.';
        return false;
    }

    const [userPart, domainPart] = email.split('@');

    if (!userRegex.test(userPart)) {
        window.emailError.textContent = 'La partie utilisateur de l\'email est invalide.';
        return false;
    }

    if (!domainAllowlist.includes(domainPart) && !validateDomainPart(domainPart, domainRegex, literalRegex)) {
        window.emailError.textContent = 'La partie domaine de l\'email est invalide.';
        return false;
    }

    window.emailError.textContent = '';
    return true;
}

function validateDomainPart(domainPart, domainRegex, literalRegex) {
    if (domainRegex.test(domainPart)) {
        return true;
    }

    const literalMatch = literalRegex.exec(domainPart);
    if (literalMatch) {
        // const ipAddress = literalMatch[1];
        return true;
    }

    return false;
}

function checkPassword() {
    const passwordValue = window.password.value;
    if (passwordValue === '') {
        window.passwordErrors.classList.add('hidden');
        return false;
    }

    let isValid = true;
    window.passwordErrors.classList.remove('hidden');

    if (passwordValue.length < 10) {
        document.getElementById('lengthError').classList.remove('hidden');
        isValid = false;
    } else {
        document.getElementById('lengthError').classList.add('hidden');
    }

    if (!/[A-Z]/.test(passwordValue)) {
        document.getElementById('uppercaseError').classList.remove('hidden');
        isValid = false;
    } else {
        document.getElementById('uppercaseError').classList.add('hidden');
    }

    if (!/[a-z]/.test(passwordValue)) {
        document.getElementById('lowercaseError').classList.remove('hidden');
        isValid = false;
    } else {
        document.getElementById('lowercaseError').classList.add('hidden');
    }

    if (!/\d/.test(passwordValue)) {
        document.getElementById('digitError').classList.remove('hidden');
        isValid = false;
    } else {
        document.getElementById('digitError').classList.add('hidden');
    }

    if (isValid) {
        window.passwordErrors.classList.add('hidden');
    }

    return isValid;
}

function updateSubmitButton() {
    const isEmailValid = validateEmail();
    const isPasswordValid = checkPassword();
    const isFirstNameFilled = window.firstNameInput.value.trim() !== '';
    const isLastNameFilled = window.lastNameInput.value.trim() !== '';

    const isFormValid = isEmailValid && isPasswordValid && window.isConditionsAccepted && isFirstNameFilled && isLastNameFilled;

    window.submitButton.disabled = !isFormValid;

    if (window.submitButton.disabled) {
        window.submitButton.classList.add('button_disabled');
        window.submitButton.classList.remove('button_save_drawer');
    } else {
        window.submitButton.classList.add('button_save_drawer');
        window.submitButton.classList.remove('button_disabled');
    }
}

function maskEmail(email) {
    const [localPart, domain] = email.split('@');
    return `${localPart[0]}${'*'.repeat(localPart.length - 2)}${localPart[localPart.length - 1]}@${domain}`;
}

function init() {
    window.signUpModal = document.getElementById('signUpModal');
    window.loginTab = document.getElementById('loginTab');
    window.signUpTab = document.getElementById('signUpTab');
    window.loginDiv = document.getElementById('loginDiv');
    window.signUpDiv = document.getElementById('signUpDiv');
    window.loginForm = document.getElementById('loginForm');
    window.signUpForm = document.getElementById('signUpForm');
    window.modalTitle = document.getElementById('modalTitle');
    window.signUpNav = document.getElementById('signUpNav');
    window.toggleLoginPassword = document.getElementById('toggleLoginPassword');
    window.togglePassword = document.getElementById('togglePassword');
    window.loginPassword = document.getElementById('loginPassword');
    window.loginEmail = document.getElementById('loginEmail');
    window.password = document.getElementById('password');
    window.forgotPassword = document.getElementById('forgotPassword');
    window.showConditions = document.getElementById('showConditions');
    window.firstNameInput = document.getElementById('firstName');
    window.lastNameInput = document.getElementById('lastName');
    window.emailInput = document.getElementById('email');
    window.emailError = document.getElementById('emailError');
    window.passwordErrors = document.getElementById('passwordErrors');
    window.submitButton = document.getElementById('signUpSubmitButton');
    window.signUpValidCheckbox = document.getElementById('signUpValidCheckbox');
    window.modalContent = document.getElementById('modalContent');
    window.conditionsContent = document.getElementById('conditionsContent');
    window.backButton = document.getElementById('backButton');
    window.resendEmailButton = document.getElementById('resendEmailButton');
    window.maskedEMail = document.getElementById('maskedEmail');
    window.urlParams = new URLSearchParams(window.location.search);
    window.isConditionsAccepted = false;
    window.out_of_modal_click = false;

    activateLoginTab();
    window.loginTab.addEventListener('click', activateLoginTab);
    window.signUpTab.addEventListener('click', activateSignUpTab);

    window.toggleLoginPassword.addEventListener('click', () => {
        if (window.loginPassword.type == 'password') {
            window.loginPassword.type = 'text';
            window.toggleLoginPassword.classList.remove('fa-eye');
            window.toggleLoginPassword.classList.add('fa-eye-slash');
        } else {
            window.loginPassword.type = 'password';
            window.toggleLoginPassword.classList.remove('fa-eye-slash');
            window.toggleLoginPassword.classList.add('fa-eye');
        }
    });

    window.togglePassword.addEventListener('click', () => {
        if (window.password.type == 'password') {
            window.password.type = 'text';
            window.togglePassword.classList.remove('fa-eye');
            window.togglePassword.classList.add('fa-eye-slash');
        } else {
            window.password.type = 'password';
            window.togglePassword.classList.remove('fa-eye-slash');
            window.togglePassword.classList.add('fa-eye');
        }
    });

    window.forgotPassword.addEventListener('click', function(e) {
        e.preventDefault();
    });

    window.showConditions.addEventListener('click', function(e) {
        e.preventDefault();
        window.modalContent.classList.add('hidden');
        window.conditionsContent.classList.remove('hidden');
    });

    window.backButton.addEventListener('click', function() {
        window.modalContent.classList.remove('hidden');
        window.conditionsContent.classList.add('hidden');
        updateSubmitButton();
    });

    window.firstNameInput.addEventListener('input', updateSubmitButton);

    window.emailInput.addEventListener('input', function() {
        validateEmail();
        updateSubmitButton();
    });

    window.password.addEventListener('input', function() {
        checkPassword();
        updateSubmitButton();
    });

    window.signUpValidCheckbox.addEventListener('change', function() {
        window.isConditionsAccepted = event.target.checked;
        const validateConditionsCheckbox = document.getElementById('validateConditions');
        if (validateConditionsCheckbox) {
            validateConditionsCheckbox.checked = window.isConditionsAccepted;
        }

        updateSubmitButton();
    });

    window.signUpForm.addEventListener('submit', function(e) {
        e.preventDefault();
        if (window.firstNameInput.value.trim() !== '' && window.lastNameInput.value.trim() !== '' && validateEmail() && checkPassword() && window.signUpValidCheckbox.checked) {
            const formData = new FormData(window.signUpForm);
            fetch(window.signUpForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': window.csrf_token
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    email = data.email;
                    document.getElementById('errorMessages').textContent = '';
                    document.getElementById('successMessages').textContent = data.message;
                    window.modalTitle.textContent = 'Félicitations !';
                    window.signUpNav.classList.add('hidden');
                    document.getElementById('modalContent').classList.add('hidden');
                    document.getElementById('registrationSuccess').classList.remove('hidden');
                    document.getElementById('registrationSuccessMessage').textContent = data.message;
                    window.maskedEMail.textContent = maskEmail(data.email);
                    if (data.message === "Validation par e-mail actuellement indisponible"){
                        document.getElementById('resendEmailSection').classList.add('hidden')
                    }
                } else {
                    document.getElementById('successMessages').textContent = '';
                    document.getElementById('errorMessages').textContent = Object.values(data.errors).join(', ');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('successMessages').textContent = '';
                document.getElementById('errorMessages').textContent = 'Une erreur est survenue. Veuillez réessayer.';
            });
        }
    });

    document.getElementById('resetModal').addEventListener('click', function(e) {
        e.preventDefault();
        window.signUpNav.classList.remove('hidden');
        document.getElementById('modalContent').classList.remove('hidden');
        document.getElementById('registrationSuccess').classList.add('hidden');
        document.getElementById('successMessages').textContent = '';
        window.signUpForm.reset();
        activateLoginTab();
    });

    resendEmailButton.addEventListener('click', function() {
        const email = window.emailInput.value ? window.emailInput.value : window.loginEmail.value ;
        fetch('/send-validation-mail/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.csrf_token
            },
            body: JSON.stringify({ email: email })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('errorMessages').textContent = '';
                document.getElementById('successMessages').textContent = data.message;
            } else {
                document.getElementById('successMessages').textContent = '';
                document.getElementById('errorMessages').textContent = data.message;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('successMessages').textContent = '';
            document.getElementById('errorMessages') = "Une erreur s'est produite. Veuillez réessayer plus tard.";
        });
    });

    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(window.loginForm);
        fetch(window.loginForm.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': window.csrf_token
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('errorMessages').textContent = '';
                document.getElementById('successMessages').textContent = data.message;
                setTimeout(() => {
                    window.location.reload();
                }, 500);
            } else {
                document.getElementById('successMessages').textContent = '';
                if (!data.unverified_mail){
                    document.getElementById('errorMessages').textContent = data.message;
                }else{
                    document.getElementById('errorMessages').textContent = '';
                    email = data.email;
                    window.modalTitle.textContent = 'Vérification de votre adresse email';
                    window.signUpNav.classList.add('hidden');
                    document.getElementById('modalContent').classList.add('hidden');
                    document.getElementById('registrationSuccess').classList.remove('hidden');
                    document.getElementById('registrationSuccessMessage').textContent = data.message;
                    window.maskedEMail.textContent = maskEmail(data.email);
                    if (data.mail_resend_fail){
                        document.getElementById('resendEmailSection').classList.add('hidden')
                    }
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('successMessages').textContent = '';
            document.getElementById('errorMessages').textContent = 'Une erreur est survenue. Veuillez réessayer.';
        });
    });

    // Fermer la modale en cliquant en dehors
    window.signUpModal.addEventListener('mousedown', function(e) {
        if (e.target === window.signUpModal) {
            window.out_of_modal_click = true;
        }
    });

    window.signUpModal.addEventListener('mouseup', function(e) {
        if (e.target === window.signUpModal && window.out_of_modal_click) {
            window.out_of_modal_click = false;
            window.signUpModal.classList.add('hidden');
        }
    });

    updateSubmitButton();
}