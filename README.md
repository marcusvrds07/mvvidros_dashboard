# MV Vidros Dashboard

Dashboard administrativo desenvolvido para a **MV Vidros & Serralheria**, com o objetivo de facilitar o **gerenciamento de estoque, vendas e usuários** em um ambiente moderno, profissional e intuitivo.

---

## 🚀 Tecnologias Utilizadas
- **Python (Flask)** – Backend
- **HTML5 / CSS3 / JavaScript** – Estrutura e interatividade
- **Docker (Após Finalização do Projeto)** – Ambiente isolado
---

## ⚙️ Funcionalidades
- 📦 **Gestão de Estoque** – Controle de produtos disponíveis e em falta.  
- 💰 **Controle de Vendas** – Monitoramento diário e mensal de vendas.  
- 📊 **Relatórios Dinâmicos** – Gráficos de desempenho em tempo real.  
- 👤 **Gerenciamento de Usuários** – Criação e controle de acessos e permissões. 

---

## 🛠️ Instalação e Uso

### Pré-requisitos
- Python 3.10+  
- Virtualenv

### Passos
```bash
# Clone este repositório
git clone https://github.com/user_name/mvvidros-dashboard.git

# Acesse a pasta do projeto
cd mvvidros-dashboard

# Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows

# Instale as dependências
pip install -r requirements.txt

# Rode o servidor Flask
flask --app main run
