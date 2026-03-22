# CineReserve

API REST para gerenciamento de filmes e sessoes de cinema, com cadastro de usuarios, autenticacao JWT, painel administrativo do Django e seed para popular o banco com dados iniciais.

## Stack usada

- Python 3.11+
- Django 5
- Django REST Framework
- Simple JWT
- Python Decouple
- SQLite ou PostgreSQL

## Como instalar dependencias

### Opcao 1: usando `venv` + `pip`

```powershell
python -m venv venv
venv\Scripts\activate
pip install django djangorestframework python-decouple "psycopg[binary]" djangorestframework-simplejwt
```

### Opcao 2: usando Poetry

```powershell
poetry install
```

## Como configurar `.env`

Crie um arquivo `.env` na raiz do projeto com base no `.env.example`.

### Exemplo com SQLite

```env
DJANGO_SECRET_KEY=sua-chave-secreta-aqui
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DJANGO_DATABASE_ENGINE=sqlite
```

### Exemplo com PostgreSQL

```env
DJANGO_SECRET_KEY=sua-chave-secreta-aqui
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DJANGO_DATABASE_ENGINE=postgres
DB_NAME=cinereserve
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

## Como rodar migracoes

```powershell
python manage.py migrate
```

## Como criar superusuario

```powershell
python manage.py createsuperuser
```

## Como executar servidor

```powershell
python manage.py runserver
```

Aplicacao disponivel em `http://127.0.0.1:8000/`.

## Interface web

Tambem foram adicionadas telas HTML integradas ao backend para demonstrar as funcionalidades iniciais:

- `GET /login/` para login de usuarios
- `GET /register/` para cadastro de usuarios
- `GET /movies/` para listar todos os filmes ativos

Fluxo sugerido:

1. Acesse `http://127.0.0.1:8000/register/` para criar um usuario.
2. Faca login em `http://127.0.0.1:8000/login/`.
3. Depois do login, a interface redireciona para `http://127.0.0.1:8000/movies/`.

Observacao: a tela de filmes depende de um token JWT armazenado no navegador apos o login.

## Como rodar seed

O projeto possui um comando que cria 5 filmes e pelo menos 3 sessoes para cada um.

```powershell
python manage.py seed_movies
```

## Exemplos de endpoints

### Filmes

- `GET /api/movies/`
- `GET /api/movies/{id}/`

### Sessoes do filme

- `GET /api/movies/{movie_id}/sessions/`
- `POST /api/movies/{movie_id}/sessions/`

Exemplo de criacao de sessao:

```http
POST /api/movies/1/sessions/
Content-Type: application/json

{
  "room_number": 3,
  "start_time": "2026-03-20T19:00:00Z",
  "end_time": "2026-03-20T21:00:00Z"
}
```

Observacao: o sistema nao permite cadastrar duas sessoes ativas na mesma sala com horarios sobrepostos.

### Autenticacao

- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/refresh/`

Exemplo de cadastro:

```http
POST /api/auth/register/
Content-Type: application/json

{
  "username": "admin",
  "email": "admin@example.com",
  "password": "123456"
}
```

## Exemplo de login JWT

Requisicao:

```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "123456"
}
```

Resposta esperada:

```json
{
  "refresh": "seu_refresh_token",
  "access": "seu_access_token"
}
```

Exemplo de uso do token nas rotas autenticadas:

```http
Authorization: Bearer seu_access_token
```

Exemplo para renovar o token:

```http
POST /api/auth/refresh/
Content-Type: application/json

{
  "refresh": "seu_refresh_token"
}
```
