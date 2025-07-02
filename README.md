## Rodando o projeto

### Configuração Primária ⚙️
1 - Clone o repositório do projeto:
```bash
mkdir django-project
git clone <project-repository-url>
```

2 - Configure o ambiente virtual:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```
3 - Copie o template de variáveis de ambiente, e preencha o mesmo com os valores necessários:
```bash
cp env.example .env
```

4 - Instale as dependências do projeto:
```bash
pip install -r requirements.txt
```

5 - Rode as migrações do banco de dados:
```bash
python manage.py makemigrations
python manage.py migrate
```
---

### Rodar o projeto através do Docker 🐳
```bash
docker compose docker-compose.yml up --build
```
- Acesse a aplicação em `http://0.0.0.0:8000/`

---

### Rodar o projeto localmente 🏡
```bash
python manage.py runserver
```
- Acesse a aplicação em `http://0.0.0.0:8000/`
---


