document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("#userInfoModal form");

    form.addEventListener("submit", (event) => {
        event.preventDefault();
        let errors = {};

        // --- Nome ---
        const nameInput = form.querySelector("#full_name");
        const name = nameInput.value.trim();
        const names = name.split(" ");
        if (!/^[A-Za-zÀ-ÖØ-öø-ÿ\s]+$/.test(name)) {
            errors["#error-nome"] = "O nome informado precisa conter apenas letras!";
        } else if (names[0].length < 3) {
            errors["#error-nome"] = "O seu primeiro nome precisa ter pelo menos 3 letras!";
        } else if (names.length < 2) {
            errors["#error-nome"] = "Você precisa informar um nome e um sobrenome!";
        }

        // --- Data ---
        const dateInput = form.querySelector("#date_of_birth");
        const dateValue = dateInput.value;
        if (!/^\d{4}-\d{2}-\d{2}$/.test(dateValue)) {
            errors["#error-date"] = "Formato Inválido";
        } else {
            const inputDate = new Date(dateValue);
            const today = new Date();
            if (isNaN(inputDate.getTime())) {
                errors["#error-date"] = "A data informada não é uma data válida no calendário.";
            } else if (inputDate > today) {
                errors["#error-date"] = "A data informada está no futuro.";
            }
        }

        // --- CPF ---
        const cpfInput = form.querySelector("#cpf");
        let cpf = cpfInput.value.replace(/\D/g, "");
        if (cpf.length !== 11) {
            errors["#error-cpf"] = "O formato do CPF está incorreto.";
        } else if (/^(\d)\1+$/.test(cpf)) {
            errors["#error-cpf"] = "O CPF não pode conter todos os números iguais.";
        } else {
            // valida dígitos verificadores
            let soma = 0;
            for (let i = 0; i < 9; i++) soma += parseInt(cpf[i]) * (10 - i);
            let resto = (soma * 10) % 11;
            resto = resto === 10 ? 0 : resto;
            if (resto !== parseInt(cpf[9])) {
                errors["#error-cpf"] = "O CPF digitado é inválido.";
            }
            soma = 0;
            for (let i = 0; i < 10; i++) soma += parseInt(cpf[i]) * (11 - i);
            resto = (soma * 10) % 11;
            resto = resto === 10 ? 0 : resto;
            if (resto !== parseInt(cpf[10])) {
                errors["#error-cpf"] = "O CPF digitado é inválido.";
            }
        }

        // --- Telefone ---
        const telInput = form.querySelector("#telephone_number");
        const tel = telInput.value.replace(/\D/g, "");
        if (tel.length < 10 || tel.length > 11) {
            errors["#error-telephone"] = "O número não corresponde a um número de telefone válido.";
        }

        // --- Exibe erros ---
        document.querySelectorAll(".error-messages").forEach(div => div.innerHTML = "");
        if (Object.keys(errors).length > 0) {
            for (const [selector, message] of Object.entries(errors)) {
                const container = document.querySelector(selector);
                if (container) container.innerHTML = `<p style="color:red">${message}</p>`;
            }
        } else {
            form.submit();
        }
    });
});