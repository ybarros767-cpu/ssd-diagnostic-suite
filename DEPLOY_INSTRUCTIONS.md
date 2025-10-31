# 🚀 Instruções de Deploy - SSD Diagnostic Suite v2.5.1

## ✅ Status do Projeto

- ✅ Código corrigido e atualizado
- ✅ Frontend buildado
- ✅ Docker Compose configurado
- ✅ Nginx configurado
- ✅ Scripts de deploy criados

## 📋 Pré-requisitos

1. Docker e Docker Compose instalados
2. Node.js e npm (para build do frontend)
3. Arquivo `.env` configurado na raiz do projeto

## 🚀 Deploy Automático

Execute o script de deploy:

```bash
./DEPLOY.sh
```

O script irá:
1. Limpar containers antigos
2. Verificar e rebuildar o frontend se necessário
3. Verificar arquivo `.env`
4. Construir imagens Docker
5. Subir containers
6. Verificar status dos serviços

## 🔧 Deploy Manual

Se preferir fazer manualmente:

```bash
# 1. Build do frontend
cd ssd-diagnostic-suite
npm run build
cd ..

# 2. Copiar build para dist
cp -r ssd-diagnostic-suite/build-output/* dist/

# 3. Build e subir containers
sudo docker compose build --no-cache
sudo docker compose up -d

# 4. Verificar status
sudo docker ps
curl http://localhost:8000/health
curl http://localhost:8080
```

## 🌐 URLs Após Deploy

- **Dashboard**: http://localhost:8080
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📝 Verificar Logs

```bash
# Backend
sudo docker logs -f ssd_backend

# Nginx
sudo docker logs -f ssd_nginx

# Todos os containers
sudo docker compose logs -f
```

## 🛑 Parar Serviços

```bash
sudo docker compose down
```

## 🔄 Reiniciar Serviços

```bash
sudo docker compose restart
```

## ⚙️ Configuração do .env

O arquivo `.env` deve conter:

```env
GROQ_API_KEY=sua_chave_aqui
APP_ENV=production
```

## 📦 Estrutura do Projeto

```
ssd-diagnostic-suite/
├── ssd-diagnostic-suite/
│   ├── backend/          # Código backend (FastAPI)
│   ├── src/             # Código frontend (React)
│   └── build-output/     # Build do frontend
├── dist/                # Build final do frontend (usado pelo nginx)
├── docker-compose.yml   # Configuração Docker Compose
├── nginx.conf          # Configuração Nginx
└── .env                # Variáveis de ambiente
```

## 🔍 Troubleshooting

### Backend não inicia
```bash
sudo docker logs ssd_backend
```

### Frontend não carrega
- Verifique se o diretório `dist/` existe e tem conteúdo
- Verifique logs do nginx: `sudo docker logs ssd_nginx`

### Porta em uso
```bash
sudo lsof -i :8000
sudo lsof -i :8080
# Matar processos se necessário
```

## ✅ Checklist de Deploy

- [ ] Docker está rodando
- [ ] Arquivo `.env` existe e está configurado
- [ ] Frontend foi buildado (`dist/` existe)
- [ ] Containers foram construídos
- [ ] Containers estão rodando
- [ ] Backend responde em `/health`
- [ ] Frontend carrega em `http://localhost:8080`

