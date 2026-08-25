# FiniBot — educação financeira pelo Telegram 🤖💰

O **Fini** é um bot de educação financeira voltado a jovens de 13 a 21 anos. Pelo Telegram, ele ajuda a registrar receitas e gastos, acompanhar metas, entender o orçamento e aprender conceitos financeiros com uma linguagem simples e próxima.

> O conteúdo do bot é educativo e não substitui orientação financeira profissional.

## Funcionalidades

- registro de receitas e gastos por comandos ou linguagem natural;
- confirmação, edição e correção de lançamentos antes e depois de salvá-los;
- resumo mensal com categorias, comparação com o mês anterior e insights contextualizados;
- exportação do controle financeiro e das metas em planilha `.xlsx`;
- criação de metas e atualização de progresso;
- simulador para comparar gastar, guardar e investir;
- trilha `/aprender` com cards, quizzes e mini-desafios de educação financeira;
- perguntas e respostas com contexto do perfil e do mês do usuário;
- desafios semanais em rotação determinística;
- pontos, níveis e constância cumulativa, sem perda de progresso por inatividade;
- envio de foto com legenda financeira — a aplicação não baixa nem persiste a imagem e extrai o lançamento somente da legenda, sem OCR.

## Stack

| Componente | Tecnologia |
|---|---|
| Canal | Telegram Bot API + `python-telegram-bot` |
| Backend/API | FastAPI + Python 3.12 |
| LLM principal | API OpenAI-compatible, configurável para xAI, Groq, OpenRouter e outros provedores |
| LLM local | Ollama com `gemma3:4b` como fallback |
| Banco de dados | PostgreSQL 16 + SQLAlchemy assíncrono |
| Sessões e limites | Redis 7 para contexto, rate limiting e rascunhos temporários |
| Planilhas | OpenPyXL |
| Infraestrutura | Docker Compose |
| Qualidade e CI | Pytest, Black, Ruff e GitHub Actions |

## Pré-requisitos

- Git;
- Docker com o plugin Docker Compose para o início rápido;
- Python 3.12 para executar a aplicação diretamente no host.

## Início rápido com Docker

### 1. Clone e configure o projeto

```bash
git clone https://github.com/eumoas/finibot.git
cd finibot
cp .env.example .env
```

Edite o `.env` e informe o token do Telegram. Para os recursos de IA, configure um provedor principal ou habilite o Ollama:

- `TELEGRAM_BOT_TOKEN`: token criado pelo [@BotFather](https://t.me/BotFather);
- `LLM_API_KEY`: chave do provedor de LLM escolhido;
- `LLM_BASE_URL` e `LLM_MODEL`: endpoint e modelo desse provedor;
- `TELEGRAM_SECRET_TOKEN` e `ADMIN_API_KEY`: substitua os valores de exemplo por segredos aleatórios em produção.

O `.env.example` traz uma configuração principal e um exemplo alternativo para Groq.

### 2. Inicie os serviços

```bash
docker compose up -d --build fini-api
```

O Compose inicia também PostgreSQL e Redis. Na primeira execução, a aplicação cria o esquema atual do banco e cadastra os desafios iniciais.

Confira a aplicação:

```bash
curl http://localhost:8000/health
docker compose logs --tail=100 fini-api
```

Para encerrar sem apagar os volumes:

```bash
docker compose down
```

### 3. Fallback local com Ollama (opcional)

```bash
docker compose up -d ollama
docker compose exec ollama ollama pull gemma3:4b
```

Com a aplicação executada pelo Compose, mantenha `OLLAMA_BASE_URL=http://ollama:11434`.

## Desenvolvimento local

Use o Docker apenas para PostgreSQL e Redis e execute a API no host:

```bash
docker compose up -d postgres redis

python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt -r requirements-dev.txt
```

Como o processo Python estará fora da rede do Compose, ajuste estas linhas no `.env`:

```dotenv
DATABASE_URL=postgresql+asyncpg://fini:finidev123@localhost:5433/finibot
REDIS_URL=redis://localhost:6379/0
OLLAMA_BASE_URL=http://localhost:11435
ENVIRONMENT=development
```

Se alterar `POSTGRES_PASSWORD`, use a mesma senha dentro de `DATABASE_URL`.
A linha `OLLAMA_BASE_URL` só é necessária para o fallback local; nesse caso, inicie o serviço e baixe o modelo conforme a etapa opcional acima.

Inicie o servidor com recarregamento automático:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Em desenvolvimento, o bot usa **long polling**. Em produção, ele usa webhook quando `ENVIRONMENT=production` e `WEBHOOK_URL` está configurada.

### Banco de dados e migrações

Uma instalação nova recebe o esquema atual automaticamente no primeiro startup. **Não execute o Alembic em uma base nova criada dessa forma:** a cadeia atual de migrações parte de um esquema legado e não funciona como baseline de um banco vazio ou recém-criado.

Para atualizar uma base de uma versão anterior compatível, faça backup, teste a restauração e use o comando adequado ao ambiente:

```bash
# Aplicação executada no host, com as URLs locais no .env
python -m alembic upgrade head

# Aplicação e banco executados pelo Compose
docker compose run --rm fini-api alembic upgrade head
```

## Variáveis de ambiente

| Variável | Uso |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Token do bot no Telegram |
| `TELEGRAM_SECRET_TOKEN` | Validação das requisições recebidas pelo webhook |
| `LLM_API_KEY` | Chave da API OpenAI-compatible principal |
| `LLM_BASE_URL` | URL completa do endpoint de chat completions do provedor |
| `LLM_MODEL` | Modelo utilizado pelo provedor principal |
| `OLLAMA_BASE_URL` | Endereço do serviço Ollama |
| `OLLAMA_MODEL` | Modelo local utilizado como fallback |
| `DATABASE_URL` | Conexão assíncrona com PostgreSQL |
| `POSTGRES_PASSWORD` | Senha do PostgreSQL no Compose; deve coincidir com `DATABASE_URL` |
| `REDIS_URL` | Conexão com Redis |
| `ENVIRONMENT` | `development`, `test` ou `production` |
| `DEBUG` | Habilita recursos de desenvolvimento, como `GET /docs` |
| `LOG_LEVEL` | Nível de logging, como `INFO` ou `DEBUG` |
| `WEBHOOK_URL` | URL pública base da aplicação em produção, sem barra final |
| `ADMIN_API_KEY` | Proteção do endpoint administrativo |
| `MAX_MESSAGES_PER_HOUR` | Limite de mensagens por usuário a cada hora |
| `CONTEXT_WINDOW_SIZE` | Quantidade de mensagens mantidas no contexto curto |

Consulte [`.env.example`](.env.example) para partir de uma configuração de desenvolvimento. Nunca envie o arquivo `.env` ou chaves reais ao repositório.

## Como conversar com o Fini

Além dos comandos, o bot reconhece mensagens como:

```text
gastei R$ 18,50 em um lanche hoje
recebi R$ 200 de mesada
viagem com a galera - R$ 800
se eu guardar R$ 50 por mês durante 1 ano, quanto dá?
como posso organizar melhor meus gastos?
```

## Comandos do bot

| Comando | Descrição |
|---|---|
| `/start` | Iniciar a apresentação e o onboarding |
| `/ajuda` ou `/help` | Abrir o menu de ajuda |
| `/gasto` | Registrar uma despesa |
| `/receita` | Registrar uma entrada de dinheiro |
| `/gastos` | Ver exemplos e ajuda sobre lançamentos |
| `/resumo` | Consultar saldo, categorias, metas e insights do mês |
| `/planilha` | Exportar o controle mensal em `.xlsx` |
| `/corrigir` | Corrigir um lançamento já salvo |
| `/restart` | Apagar lançamentos, metas, pontos e constância após confirmação |
| `/meta` | Criar uma meta financeira |
| `/metas` | Consultar metas e atualizar o progresso |
| `/simular` | Simular quanto guardar ao longo do tempo |
| `/desafio` | Ver o desafio da semana |
| `/aprender` | Abrir a trilha de educação financeira |
| `/pontos` | Consultar pontuação e nível |

## Modos de execução e endpoints

| Rota | Finalidade |
|---|---|
| `GET /health` | Consultar o status de execução (liveness) da aplicação |
| `POST /telegram/webhook` | Receber atualizações do Telegram em produção |
| `GET /admin/stats` | Consultar estatísticas básicas com o header `X-API-Key` |
| `GET /docs` | Abrir a documentação interativa quando `DEBUG=true` |

Para webhook, configure `ENVIRONMENT=production`, uma `WEBHOOK_URL` pública com HTTPS e o mesmo `TELEGRAM_SECRET_TOKEN` esperado pela aplicação.

### Checklist de produção

- use `ENVIRONMENT=production` e `DEBUG=false`;
- defina `WEBHOOK_URL` com HTTPS e sem barra final;
- substitua `TELEGRAM_SECRET_TOKEN`, `ADMIN_API_KEY` e as credenciais do banco por valores fortes;
- mantenha `POSTGRES_PASSWORD` e a senha presente em `DATABASE_URL` sincronizadas;
- disponibilize PostgreSQL e Redis persistentes antes de iniciar a aplicação.

## Estrutura do projeto

```text
app/
├── api/             # handlers do Telegram e roteamento de comandos
├── content/         # conteúdos da trilha de aprendizagem
├── core/            # configuração, banco de dados e Redis
├── db/              # carga inicial de dados
├── flows/           # jornadas de finanças, metas, ensino e simulação
├── models/          # modelos SQLAlchemy
├── prompts/         # prompts e templates de mensagens
├── repositories/    # acesso aos dados
├── services/        # LLM, sessões e gamificação
└── main.py          # aplicação FastAPI e ciclo de vida do bot

migrations/          # migrações Alembic
tests/unit/          # testes unitários
.github/workflows/   # integração contínua
```

## Dados e privacidade

- PostgreSQL persiste o cadastro, os lançamentos, as metas, o progresso dos desafios e o histórico de perguntas e respostas do Q&A;
- Redis mantém contexto curto, contadores de rate limiting e rascunhos temporários, com expiração de uma hora;
- fotos enviadas ao bot não são baixadas nem armazenadas pela aplicação; apenas a legenda é processada.

## Testes e qualidade

```bash
python -m pytest tests/unit/ -v --cov=app
python -m black --check app/ tests/
python -m ruff check app/ tests/
```

O workflow executa essas verificações em pushes para `main` e `develop` e em pull requests para `main`. Em pushes para `main`, ele também contém uma etapa de deploy no Fly.io, dependente das credenciais e da configuração do ambiente de destino.

## Documentação

- [Especificação funcional v2](spec_fini_v2.md)
- [Software Design Document v2](SDD_Fini_v2.md)
- [Visão do produto](project.md)
- [Arquitetura inicial](design.md)
- [Especificação inicial](spec.md)
- [Software Design Document v1](SDD_Fini_v1.0.md)
