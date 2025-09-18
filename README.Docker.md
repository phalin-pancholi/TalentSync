# TalentSync Docker Setup

This document provides instructions for running the TalentSync application using Docker.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose V2
- At least 4GB RAM available
- Ports 3000, 8001, and 27017 available

## Quick Start

### Production Setup

1. **Clone and navigate to the project directory:**
   ```bash
   cd /app
   ```

2. **Build and start all services:**
   ```bash
   docker-compose up --build -d
   ```

3. **Access the applications:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8001/api
   - MongoDB: mongodb://localhost:27017

4. **View logs:**
   ```bash
   docker-compose logs -f
   ```

5. **Stop all services:**
   ```bash
   docker-compose down
   ```

### Development Setup

1. **Start development environment with hot reload:**
   ```bash
   docker-compose -f docker-compose.dev.yml up --build
   ```

2. **Features in development mode:**
   - Hot reload for both frontend and backend
   - Source code mounted as volumes
   - Development optimized builds
   - Separate development database

## Service Details

### Frontend (React)
- **Production**: Multi-stage build with Nginx
- **Development**: Node.js with hot reload
- **Port**: 3000
- **Health check**: HTTP GET on /

### Backend (FastAPI)
- **Runtime**: Python 3.11
- **Port**: 8001
- **Health check**: HTTP GET on /api/
- **Features**: Auto-reload in development

### Database (MongoDB)
- **Version**: 7.0
- **Port**: 27017
- **Credentials**: admin/password123
- **Database**: talentsync_db (prod) / talentsync_dev_db (dev)
- **Initialization**: Automatic with sample data

## Environment Variables

### Backend (.env)
```env
MONGO_URL=mongodb://admin:password123@mongodb:27017/talentsync_db?authSource=admin
DB_NAME=talentsync_db
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env)
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

## Docker Commands Reference

### Build specific service:
```bash
docker-compose build frontend
docker-compose build backend
```

### Scale services:
```bash
docker-compose up --scale backend=2
```

### View service status:
```bash
docker-compose ps
```

### Execute commands in containers:
```bash
# Backend shell
docker-compose exec backend bash

# Frontend shell
docker-compose exec frontend sh

# MongoDB shell
docker-compose exec mongodb mongosh -u admin -p password123
```

### Clean up:
```bash
# Remove containers and networks
docker-compose down

# Remove containers, networks, and volumes
docker-compose down -v

# Remove everything including images
docker-compose down -v --rmi all
```

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Check what's using the port
   lsof -i :3000
   lsof -i :8001
   lsof -i :27017
   
   # Kill process or change ports in docker-compose.yml
   ```

2. **Permission errors:**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   ```

3. **MongoDB connection issues:**
   ```bash
   # Check MongoDB logs
   docker-compose logs mongodb
   
   # Verify database connectivity
   docker-compose exec backend python -c "
   import pymongo
   client = pymongo.MongoClient('mongodb://admin:password123@mongodb:27017/')
   print(client.server_info())
   "
   ```

4. **Frontend not loading:**
   ```bash
   # Check if backend is accessible
   curl http://localhost:8001/api/
   
   # Rebuild frontend
   docker-compose build --no-cache frontend
   ```

### Health Checks

All services include health checks:
```bash
# View health status
docker-compose ps

# Check individual service health
docker inspect --format='{{.State.Health.Status}}' talentsync-frontend
docker inspect --format='{{.State.Health.Status}}' talentsync-backend
docker inspect --format='{{.State.Health.Status}}' talentsync-mongodb
```

### Performance Optimization

1. **Production optimizations:**
   - Multi-stage builds reduce image size
   - Nginx serves static files efficiently
   - Non-root users for security
   - Gzip compression enabled

2. **Development optimizations:**
   - Volume mounts for hot reload
   - Separate development database
   - Development-specific configurations

## Monitoring and Logs

### Real-time logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mongodb
```

### Container resource usage:
```bash
docker stats
```

## Security Considerations

1. **Change default passwords** in production
2. **Use environment variables** for sensitive data
3. **Non-root users** in all containers
4. **Security headers** configured in Nginx
5. **Network isolation** with Docker networks

## Backup and Restore

### Backup MongoDB data:
```bash
docker-compose exec mongodb mongodump --username admin --password password123 --authenticationDatabase admin --out /data/backup
```

### Restore MongoDB data:
```bash
docker-compose exec mongodb mongorestore --username admin --password password123 --authenticationDatabase admin /data/backup
```