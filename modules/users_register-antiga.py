import bcrypt
from modules.verification import check_cpf, check_date, check_phone_number, password_validador, check_username, check_name
from modules.sql.load_sql import load_sql

# Função para registrar um novo usuário
def registration(username, cursor, connection, placeholder, admin=False, new_user=False):
    if not admin and not new_user:
        while True:
            username = input('Digite um email para alterarmos: ').strip()
            if not username:
                continue
            result = check_username(cursor, connection, username, placeholder)
            if result == True:
                from modules.auth import login_user
                print('O login informado ja existe em nosso sistema')
                login_user(cursor, connection, placeholder, username)
                return False
            elif result == 'False':
                continue
            break
    elif admin:
        print("\nCriando o acesso administrativo")
        username = input('Digite um email: ').strip()
    elif new_user:
        while True:
            username = input('Digite um email para criarmos um novo usuario: ').strip()
            if not username:
                continue
            result = check_username(cursor, connection, username, placeholder)
            if result == True:
                from modules.auth import login_user
                print('O login informado ja existe em nosso sistema')
                continue
            elif result == 'False':
                continue
            break

    # Captura, valida(senha fraca) e criptografa a senha
    while True:
        password = input('Informe sua senha para cadastro: ').strip()
        if password_validador(password):
            print('Login e senha criados. Para finalizar, por favor, forneça mais alguns dados pessoais.')
            break
        else:
            print('\nSenha fraca! A senha deve ter: 8-20 caracteres, letra maiúscula e minúscula , números, caractere especial e não pode conter espaços.\n')
            continue
        
    salt = bcrypt.gensalt()
    password = bcrypt.hashpw(password.encode(), salt)
    
    query_insert_login = load_sql('modules/sql/queries/insert_login.sql').replace('?', placeholder)
    
    # Inserção dos dados no banco
    if admin:
        administrator = 1 if placeholder == "?"  else True
    else:
        administrator = 0 if placeholder == "?"  else False
    cursor.execute(query_insert_login, (username, password, administrator))
    login_id = cursor.lastrowid
    
    # Captura das informações adicionais do usuário
    while True:
        name = input('Nome completo: ').strip()
        if check_name(name):
            break
        
    while True:
        date = input('Data de nascimento (DD/MM/YYYY): ').strip()
        
        verified_date = check_date(date)
        if verified_date:
            break

    while True:
        phone_number = input('Número de telefone: ').strip()
        if check_phone_number(phone_number):
            break
    while True:
        cpf = input('CPF: ').strip()
        cpf = check_cpf(cpf)

        if cpf:
            break
    
    query_insert_user = load_sql('modules/sql/queries/insert_user.sql').replace('?', placeholder)

    cursor.execute(query_insert_user, (login_id, name, verified_date, phone_number, cpf))
    user_id = cursor.lastrowid

    # #parei na parte de criação do sistema de inserir as perms ao criar um usuario!
    # user_permissions = [
    #     (user_id,),
    #     ('Gerenciar Vendas',),
    #     ('Gerenciar Estoque',),
    #     ('Gerenciar Insumos',),
    # ]
    # cursor.execute('INSERT INTO ')
    connection.commit()
    print("Cadastro realizado com sucesso.")