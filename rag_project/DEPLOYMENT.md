# SmartDocs AI Pro - Deployment Guide

## Prerequisites

- Docker installed on your system
- Docker Compose installed (for multi-service deployment)
- At least 2GB RAM available
- Ports 8000 and 8501 available

## Quick Start with Docker Compose

### 1. Navigate to the project directory
```bash
cd rag_project
```

### 2. Build and start the services
```bash
docker-compose up --build
```

This will:
- Build the Docker image
- Start the Flask backend on port 8000
- Start the Streamlit frontend on port 8501
- Mount the data directory for persistence

### 3. Access the application
- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000

### 4. Stop the services
```bash
docker-compose down
```

## Deployment Options

### Option 1: Docker Compose (Recommended)
Best for local development and simple deployments.

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Option 2: Docker Standalone
Run backend and frontend separately.

**Backend:**
```bash
cd rag_project
docker build -t smartdocs-backend .
docker run -p 8000:8000 -v $(pwd)/data:/app/data smartdocs-backend python backend/app.py
```

**Frontend:**
```bash
docker run -p 8501:8501 -v $(pwd)/data:/app/data smartdocs-backend streamlit run src/app.py --server.port=8501 --server.address=0.0.0.0
```

### Option 3: Cloud Deployment

#### Deploy to Render (Free Tier)
1. Create `render.yaml` in project root
2. Push to GitHub
3. Connect Render to your repository
4. Render will auto-deploy

#### Deploy to Railway
1. Install Railway CLI: `npm install -g @railway/cli`
2. Login: `railway login`
3. Initialize: `railway init`
4. Deploy: `railway up`

#### Deploy to AWS/Azure/GCP
Use the Docker image and deploy to:
- AWS ECS/Fargate
- Azure Container Instances
- Google Cloud Run

## Environment Variables

Create a `.env` file in the `rag_project` directory:

```env
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=0

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Backend URL (for frontend)
RAG_BACKEND_URL=http://localhost:8000

# Data Directory
DATA_DIR=/app/data
```

## Data Persistence

The `data/` directory is mounted as a Docker volume:
- `data/uploads/` - Uploaded documents
- `data/docs/` - Ingested documents
- `data/vector_store.sqlite` - Vector database
- `data/embedder.pkl` - Embedding model
- `data/chat_history.sqlite` - Chat history

Data persists across container restarts.

## Production Considerations

### Security
- Use HTTPS in production
- Add authentication (API keys, OAuth)
- Implement rate limiting
- Use secrets management for sensitive data

### Performance
- Use Gunicorn for production Flask deployment
- Enable caching for frequently accessed data
- Consider using a production vector database (Pinecone, Weaviate)
- Implement CDN for static assets

### Monitoring
- Add health check endpoints
- Implement logging aggregation
- Set up error tracking (Sentry)
- Monitor resource usage

### Scaling
- Use load balancer for multiple backend instances
- Implement horizontal scaling for Streamlit
- Use managed database services for production
- Consider serverless deployment for cost optimization

## Troubleshooting

### Port Already in Use
```bash
# Check what's using the ports
netstat -tulpn | grep :8000
netstat -tulpn | grep :8501

# Kill the process or change ports in docker-compose.yml
```

### Container Won't Start
```bash
# Check logs
docker-compose logs smartdocs-backend
docker-compose logs smartdocs-frontend

# Rebuild without cache
docker-compose build --no-cache
```

### Data Not Persisting
```bash
# Check volume mounts
docker-compose ps

# Verify data directory permissions
ls -la data/
```

### Backend Connection Issues
```bash
# Test backend health
curl http://localhost:8000/health

# Check if backend is running
docker-compose ps smartdocs-backend
```

## Maintenance

### Backup Data
```bash
# Backup data directory
tar -czf smartdocs-backup-$(date +%Y%m%d).tar.gz data/

# Restore
tar -xzf smartdocs-backup-YYYYMMDD.tar.gz
```

### Update Application
```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up --build -d
```

### Clean Up
```bash
# Stop and remove containers
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v

# Remove images
docker rmi smartdocs-backend smartdocs-frontend
```

## Support

For issues or questions:
1. Check the logs: `docker-compose logs -f`
2. Review this deployment guide
3. Check the main README.md
4. Open an issue on GitHub
