function authValidation(event) {
    event.preventDefault();
    const form = event.target;

    const emailInput = form.querySelector('input[type="text"]');
    const passwordInput = form.querySelector('input[type="password"]');

    if (!window.messages) {
        window.messages = [];
    }

    // --- valida email ---
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

    // --- valida senha se for cadastro ---
    if (emailInput && emailInput.getAttribute("name") === "signup-login") {
        if (passwordInput) {
            const password = passwordInput.value.trim();
            const msgPass = "A senha precisa ter 8 a 20 caracteres";
            const hasDigits = "A senha precisa contar números"
            const specialCharacterMessage = "A senha precisa ter caracter especial";
            const uppercaseLetter = 'A senha precisa ter uma letra maiúscula'
            const lowercaseLetter = 'A senha precisa ter uma letra minúscula'
            const noSpace = 'A senha não pode conter espaço'

            updateMessage(
                msgPass,
                (password.length >= 8 && password.length <= 20)
                    ? "Success"
                    : "Error"
            );

            updateMessage(
                hasDigits,
                /[0-9]/.test(password)
                    ? "Success"
                    : "Error"
            );
            updateMessage(
                specialCharacterMessage,
                /[!@#$%^&*(),.?":{}|<>]/.test(password)
                    ? "Success"
                    : "Error"
            );

            updateMessage(
                uppercaseLetter,
                /[A-Z]/.test(password)
                    ? "Success"
                    : "Error"
            );
            updateMessage(
                lowercaseLetter,
                /[a-z]/.test(password)
                    ? "Success"
                    : "Error"
            );
            updateMessage(
                noSpace,
                /[ ]/.test(password)
                    ? "Error"
                    : "Success"
            );
        }

    }

    const hasError = window.messages.some(m => m.status === "Error");
    if (!hasError) {
        form.submit();
    } else {
        showErrorMessage(window.messages);
        return false;
    }
}

// --- Atualiza ou insere mensagem no array ---
function updateMessage(text, status) {
    const idx = window.messages.findIndex(m => m.text === text);
    if (idx === -1) {
        window.messages.push({ text, status });
    } else {
        window.messages[idx].status = status;
    }
}

// --- validação em tempo real para senha ---
document.addEventListener("DOMContentLoaded", () => {
    const passwordInput = document.querySelector('#signup-password');
    const msgPass = "A senha precisa ter 8 a 20 caracteres";
    const hasDigits = "A senha precisa contar números"
    const specialCharacterMessage = "A senha precisa ter caracter especial";
    const uppercaseLetter = 'A senha precisa ter uma letra maiúscula'
    const lowercaseLetter = 'A senha precisa ter uma letra minúscula'
    const noSpace = 'A senha não pode conter espaço'


    if (passwordInput) {
        passwordInput.addEventListener("input", function () {
            const password = passwordInput.value;
            updateMessage(
                msgPass,
                (password.length >= 8 && password.length <= 20)
                    ? "Success"
                    : "Error"
            );

            updateMessage(
                hasDigits,
                /[0-9]/.test(password)
                    ? "Success"
                    : "Error"
            );
            updateMessage(
                specialCharacterMessage,
                /[!@#$%^&*(),.?":{}|<>]/.test(password)
                    ? "Success"
                    : "Error"
            );
            updateMessage(
                uppercaseLetter,
                /[A-Z]/.test(password)
                    ? "Success"
                    : "Error"
            );
            updateMessage(
                lowercaseLetter,
                /[a-z]/.test(password)
                    ? "Success"
                    : "Error"
            );
            updateMessage(
                noSpace,
                /[ ]/.test(password)
                    ? "Error"
                    : "Success"
            );

            showErrorMessage(window.messages);
        });
    }

    const emailInput = document.querySelector('input[name="signup-login"], input[name="login"]');
    const msgEmail = "O formato do email está errado!";

    if (emailInput) {
        emailInput.addEventListener("input", function () {
            const email = emailInput.value.trim();
            const atIndex = email.indexOf("@");
            const dotIndex = email.lastIndexOf(".");
            updateMessage(
                msgEmail,
                (atIndex > 0 && dotIndex > atIndex + 1 && dotIndex < email.length - 1)
                    ? "Success"
                    : "Error"
            );
            showErrorMessage(window.messages);
        });
    }
});

// --- renderiza mensagens ---
function showErrorMessage(message) {
    const error_message = document.querySelector('.error-messages');

    if (typeof message === "string") {
        error_message.innerHTML = "";
        const element = document.createElement('p');
        element.id = 'error-message';
        element.textContent = message;
        error_message.appendChild(element);

        requestAnimationFrame(() => {
            element.classList.add('show');
        });

        setTimeout(function () {
            element.classList.remove('show');
            setTimeout(() => element.remove(), 2000);
        }, 10000);

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
            error_message.appendChild(div);

            requestAnimationFrame(() => {
                div.classList.add('show');
            });
        }

        div.textContent = item.text;
        div.style.color = (item.status === "Error") ? "red" : "green";
    });
}
