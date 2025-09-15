// --- garante que window.messages sempre exista ---
if (!window.messages) {
    window.messages = [];
}

let validationActive = false;

// --- Atualiza ou insere mensagem no array ---
function updateMessage(text, status) {
    if (!window.messages) {
        window.messages = [];
    }

    const idx = window.messages.findIndex(m => m.text === text);
    if (idx === -1) {
        window.messages.push({ text, status });
    } else {
        window.messages[idx].status = status;
    }
}

// --- renderiza mensagens ---
function showErrorMessage(message, selector = '.error-messages') {
    const error_message = document.querySelector(selector);

    if (!error_message) return;

    if (typeof message === "string") {
        let element = error_message.querySelector('p');
        if (!element) {
            element = document.createElement('p');
            element.textContent = message;
            error_message.innerHTML = "";
            error_message.appendChild(element);
            requestAnimationFrame(() => {
                element.classList.add('show');
            });
        } else {
            element.textContent = message;
        }
        return;
    }

    message.forEach(item => {
        let div = error_message.querySelector(
            '.several-error-message[data-msg="' + item.text + '"]'
        );

        if (!div) {
            div = document.createElement('div');
            div.classList.add('several-error-message');
            div.setAttribute('data-msg', item.text);
            div.textContent = item.text;
            error_message.appendChild(div);
            requestAnimationFrame(() => {
                div.classList.add('show');
            });
        } else {
            div.textContent = item.text;
        }

        div.style.color = (item.status === "Error") ? "red" : "green";
    });
}

// --- executa a validação ---
function runValidation(form) {
    const emailInput = form.querySelector('input[type="text"]');
    const passwordInput = form.querySelector('input[type="password"]');
    const passwordConfirmInput = form.querySelector('#password-confirm');

    window.messages = [];

    if (emailInput) {
        const email = emailInput.value.trim();
        const atIndex = email.indexOf("@");
        const dotIndex = email.lastIndexOf(".");
        const msgEmail = "O formato do email está errado!";

        updateMessage(
            msgEmail,
            (atIndex > 0 && dotIndex > atIndex + 1 && dotIndex < email.length - 1)
                ? "Success"
                : "Error"
        );
    }

    if ((emailInput && emailInput.getAttribute("name") === "signup-login") || passwordConfirmInput) {
        if (passwordInput || passwordConfirmInput) {
            const password = passwordInput.value.trim();
            const msgPass = "A senha precisa ter 8 a 20 caracteres";
            const hasDigits = "A senha precisa conter números";
            const specialCharacterMessage = "A senha precisa ter caracter especial";
            const uppercaseLetter = 'A senha precisa ter uma letra maiúscula';
            const lowercaseLetter = 'A senha precisa ter uma letra minúscula';
            const noSpace = 'A senha não pode conter espaço';
            const notSame = 'As senhas não são iguais';

            updateMessage(msgPass, (password.length >= 8 && password.length <= 20) ? "Success" : "Error");
            updateMessage(hasDigits, /[0-9]/.test(password) ? "Success" : "Error");
            updateMessage(specialCharacterMessage, /[!@#$%^&*(),.?":{}|<>]/.test(password) ? "Success" : "Error");
            updateMessage(uppercaseLetter, /[A-Z]/.test(password) ? "Success" : "Error");
            updateMessage(lowercaseLetter, /[a-z]/.test(password) ? "Success" : "Error");
            updateMessage(noSpace, /[ ]/.test(password) ? "Error" : "Success");

            if (passwordConfirmInput) {
                const passwordConfirm = passwordConfirmInput.value;
                updateMessage(
                    notSame,
                    (password === passwordConfirm && passwordConfirm.length > 0) ? "Success" : "Error"
                );
            }
        }
    }
}

// --- validação principal no submit ---
function authValidation(event) {
    event.preventDefault();
    const form = event.target;

    validationActive = true;
    runValidation(form);

    const hasError = window.messages.some(m => m.status === "Error");
    if (!hasError) {
        form.submit();
    } else {
        showErrorMessage(window.messages);
        return false;
    }
}

// --- validação em tempo real após o submit inicial ---
document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("form");

    const allInputs = document.querySelectorAll('input[type="text"], input[type="password"]');
    allInputs.forEach(input => {
        input.addEventListener("input", () => {
            if (validationActive) {
                runValidation(form);
                showErrorMessage(window.messages);
            }
        });
    });
});