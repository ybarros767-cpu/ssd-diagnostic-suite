# 🚀 Configuração do GitHub Actions para Deploy Automático

## 📋 Visão Geral

O projeto possui workflows do GitHub Actions configurados para:
- ✅ **CI (Continuous Integration)**: Build e testes em pull requests
- ✅ **Deploy Automático**: Deploy automático quando houver push em `main`

## 🔧 Configuração

### 1. Secrets Necessárias no GitHub

Acesse: **Settings > Secrets and variables > Actions**

Adicione os seguintes secrets:

#### Para Deploy SSH:
- `DEPLOY_HOST`: IP ou hostname do servidor (ex: `192.168.1.100` ou `deploy.exemplo.com`)
- `DEPLOY_USER`: Usuário SSH (ex: `yuri-server` ou `root`)
- `DEPLOY_SSH_KEY`: Chave privada SSH completa
  ```bash
  # Para gerar e copiar:
  cat ~/.ssh/id_ed25519_deploy
  ```
- `DEPLOY_PORT`: Porta SSH (padrão: `22`)
- `DEPLOY_PATH`: Caminho do projeto no servidor (padrão: `/opt/ssd-diagnostic-suite`)

#### Opcionais (Docker Hub):
- `DOCKER_USERNAME`: Usuário Docker Hub (opcional)
- `DOCKER_PASSWORD`: Senha Docker Hub (opcional)

### 2. Gerar Chave SSH para Deploy

```bash
# Gerar chave (se ainda não tiver)
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/id_ed25519_actions

# Copiar chave pública para servidor
ssh-copy-id -i ~/.ssh/id_ed25519_actions.pub usuario@servidor

# Mostrar chave privada (adicione como secret DEPLOY_SSH_KEY)
cat ~/.ssh/id_ed25519_actions
```

### 3. Workflows Disponíveis

#### CI Workflow (`.github/workflows/ci.yml`)
- Executa em pull requests e pushes
- Faz build do frontend
- Testa sintaxe Python
- Constrói imagens Docker
- Testa containers

#### Deploy Workflow (`.github/workflows/deploy.yml`)
- Executa apenas em push para `main`
- Faz build completo
- Faz deploy via SSH no servidor
- Executa `./deploy.sh` no servidor remoto

## 📝 Como Funciona

1. **Push para main** → Dispara deploy automático
2. **Workflow executa** → Build frontend e Docker
3. **SSH no servidor** → Clona/pull do código
4. **Executa deploy.sh** → Deploy completo

## 🔍 Ver Status

Acesse: **Actions** tab no GitHub

## ⚠️ Troubleshooting

### Deploy falha por SSH
- Verifique se `DEPLOY_SSH_KEY` está correta
- Teste conexão SSH manualmente
- Verifique se chave pública está no servidor

### Build falha
- Verifique logs em **Actions** > **Run** > **Logs**
- Verifique se dependências estão corretas

### Container não inicia
- Verifique logs do Docker no servidor
- Verifique portas 8000 e 8080 disponíveis

## 🎯 Próximos Passos

Após configurar os secrets:
1. Faça push para `main`
2. Verifique **Actions** tab
3. Deploy será executado automaticamente

## 📚 Recursos

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [SSH Action](https://github.com/appleboy/ssh-action)

