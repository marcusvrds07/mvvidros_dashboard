from password_validator import PasswordValidator
from email_validator import validate_email, EmailNotValidError, EmailUndeliverableError
import phonenumbers, re
from datetime import datetime

def email_validator(email):
    try:
        validate_email(email)
        return True
    except (EmailNotValidError, EmailUndeliverableError):
        return False

def password_validator(password):
    password_policy = PasswordValidator()

    # regras para a senha
    password_policy\
    .min(8)\
    .max(20)\
    .has().uppercase()\
    .has().lowercase()\
    .has().digits()\
    .has().symbols()\
    .has().no().spaces()\

    return password_policy.validate(password)


# Função criada para garantir validade do CPF
def check_cpf(cpf):
    # Expressão regular que valida o formato padrão do CPF: 000.000.000-00
    standard_format = r'^(\d{3})\.(\d{3})\.(\d{3})-(\d{2})$'

    weight_1 = [10, 9, 8, 7, 6, 5, 4, 3, 2]
    weight_2 = [11, 10, 9, 8, 7, 6, 5, 4, 3, 2]

    # --- Função auxiliar para formatar CPF sem pontuação para o padrão 000.000.000-00
    def format_cpf(no_cpf_format):
        return f'{no_cpf_format[0:3]}.{no_cpf_format[3:6]}.{no_cpf_format[6:9]}-{no_cpf_format[9:]}'

    # --- Função auxiliar para validar os dois últimos dígitos (dígitos verificadores)
    def check_end_digits(no_cpf_format):
        first_digit = (sum((weight_1[i] * int(no_cpf_format[i])) for i in range(len(weight_1))) * 10) % 11
        second_digit = (sum((weight_2[i] * int(no_cpf_format[i])) for i in range(len(weight_2))) * 10) % 11

        first_digit = 0 if first_digit > 9 else first_digit
        second_digit = 0 if second_digit > 9 else second_digit

        digit_checker = int(str(f'{first_digit}{second_digit}'))

        if no_cpf_format[0] * 11 != no_cpf_format:
            if digit_checker == int(no_cpf_format[-2:]):
                return True, format_cpf(no_cpf_format)  # retorna CPF formatado se válido
            return False, 'O CPF digitado é inválido.'
        return False, 'O CPF não pode conter todos os números iguais.'

    # --- Verifica se o CPF já veio no formato 000.000.000-00
    match = re.match(standard_format, cpf)

    if match:
        # junta os grupos da regex para pegar só os números
        no_cpf_format = "".join([match.group(i) for i in range(1, 5)])
        return check_end_digits(no_cpf_format)
    elif len(cpf) == 11:
        # se vier só com 11 dígitos, tenta validar também
        return check_end_digits(cpf)

    # caso não caia em nenhum cenário válido
    return False, 'O formato do CPF está incorreto.'


# Função que verifica se o numero é do brasil e se está no formato correto
def check_phone_number(number):
    if not number:
        return False, 'O número de telefone não pode ser vazio!'
    phone_number = phonenumbers.parse(number, "BR")
    if phonenumbers.is_valid_number(phone_number):
        return True, phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    else:
        return False, 'O número não corresponde a um número de telefone'

def check_name(name):
    names = name.split(' ')
    if not name.replace(' ', '').isalpha():
        return False, 'O nome informado precisa conter apenas letras!'
    if len(names[0]) < 3:
        return False, 'O seu primeiro nome precisa ter pelo menos de 3 letras!'
    if len(names) < 2:
        return False, 'Você precisa informar um nome e um sobrenome!'
    return True, name

def check_date(date_of_input, format=False):
    if format:
        format_date = f'{date_of_input[8:]}/{date_of_input[5:7]}/{date_of_input[0:4]}'
    else:
        current_date = datetime.now()
        standard_format = r'^(\d{4})-(\d{2})-(\d{2})$'

        if not re.match(standard_format, date_of_input):
            return False, 'Formato Inválido'

        try:
            informed_date = datetime.strptime(date_of_input, '%Y-%m-%d')
        except ValueError:
            return False, 'A data informada não é uma data válida no calendário.'

        if informed_date > current_date:
            return False, 'A data informada está no futuro.'
        
    return True, date_of_input if not format else format_date