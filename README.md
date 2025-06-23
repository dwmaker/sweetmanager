## Executando com Docker

Para facilitar a execução e o deploy do Sweet Manager, o projeto já inclui arquivos prontos para uso com Docker e Docker Compose. Isso garante que todas as dependências e configurações estejam corretas, independentemente do ambiente local.

### Requisitos do Projeto
- **Python 3.11** (imagem base: `python:3.11-slim`)
- Dependências Python são instaladas via `requirements.txt` dentro de um ambiente virtual isolado (`.venv`)
- O projeto é executado por um usuário não-root (`sweetuser`) para maior segurança

### Variáveis de Ambiente
- O arquivo `.env` pode ser utilizado para definir variáveis de ambiente sensíveis (ex: chaves secretas, configurações de banco de dados). Por padrão, o `docker-compose.yml` já está preparado para ler esse arquivo, basta descomentar a linha `env_file: ./.env` se necessário.

### Instruções para Build e Execução
1. **Build e subida dos containers:**
   ```sh
   docker compose up --build
   ```
   Isso irá:
   - Construir a imagem Docker do projeto
   - Instalar todas as dependências Python no ambiente virtual
   - Copiar o código-fonte e scripts necessários
   - Iniciar o serviço principal do Django

2. **Acesso à aplicação:**
   - O serviço principal expõe a porta **8000**. Acesse em: [http://localhost:8000](http://localhost:8000)

### Configurações Especiais
- O projeto já está preparado para uso com banco de dados externo (ex: PostgreSQL), mas por padrão não inclui um serviço de banco no `docker-compose.yml`. Caso deseje utilizar um banco externo, adicione o serviço correspondente e ajuste as variáveis de ambiente no `.env` e no `docker-compose.yml`.
- Para persistência de arquivos estáticos ou mídia, adicione volumes conforme necessário (veja os comentários no `docker-compose.yml`).
- O script de entrada do container é `/docker-entrypoint.sh`, já incluído e com permissões corretas.

### Resumo dos Serviços e Portas
- **python-app**: Serviço principal Django
  - Porta exposta: **8000**

> Dica: Para customizações adicionais (como adicionar banco de dados, volumes ou outros serviços), utilize os exemplos comentados no próprio `docker-compose.yml`.
