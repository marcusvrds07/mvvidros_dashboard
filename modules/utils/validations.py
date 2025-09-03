from password_validator import PasswordValidator

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