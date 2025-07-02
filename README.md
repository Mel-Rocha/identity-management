# Configuração Primária 1️⃣

## Preparando o ambiente ⚙️
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

## Scripts Automatizados 🛠️
Defina permissão de execução para os scripts de ajuda no diretório `dev_helpers/scripts/`:
```bash
chmod +x dev_helpers/scripts/*
```
---
## Rodando o Projeto 🛞

### Docker 🐳
```bash
docker compose docker-compose.yml up --build
```
- Acesse a aplicação em `http://0.0.0.0:8000/`

---

### localmente 🏡
```bash
python manage.py runserver
```
- Acesse a aplicação em `http://0.0.0.0:8000/`
---
## Qualidade de código 🔍
### Testes e estilo
Execute o seguinte comando para mensurar a qualidade do código, incluindo testes e verificação de estilo PEP8:
```bash
./dev_helpers/scripts/validate_quality.sh
```
---
### Testes unitários 🧪
Rode os testes do projeto
````bash
coverage run -m pytest
````
Geração de relatório de corbertura de testes.
````bash
coverage report -m
````

---
### Estilo PEP8 💎
Execute o linter do projeto
````bash
make lint
````
---