# MapLY ML Services - Deployment Guide

Complete guide for deploying MapLY ML Services to production environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Docker Deployment](#docker-deployment)
- [Cloud Platforms](#cloud-platforms)
  - [AWS](#aws-deployment)
  - [Google Cloud Platform](#google-cloud-platform)
  - [Azure](#azure-deployment)
- [Kubernetes](#kubernetes-deployment)
- [Traditional VPS](#traditional-vps-deployment)
- [Environment Configuration](#environment-configuration)
- [Monitoring & Logging](#monitoring--logging)
- [Security](#security)
- [Scaling](#scaling)

---

## Prerequisites

- Docker and Docker Compose (for containerized deployments)
- Cloud provider account (AWS, GCP, or Azure)
- Domain name (optional, for production)
- SSL certificate (recommended for production)

---

## Docker Deployment

### Local Docker

```bash
# Build the image
docker build -t maply-ml-services:latest .

# Run the container
docker run -d \
  -p 8000:8000 \
  -e API_HOST=0.0.0.0 \
  -e API_PORT=8000 \
  -v $(pwd)/data:/app/data:ro \
  -v $(pwd)/logs:/app/logs \
  --name maply-ml-api \
  maply-ml-services:latest

# Check logs
docker logs -f maply-ml-api

# Stop container
docker stop maply-ml-api
```

### Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

---

## AWS Deployment

### Option 1: AWS ECS (Elastic Container Service)

1. **Build and push Docker image to ECR**

```bash
# Authenticate to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Create ECR repository
aws ecr create-repository --repository-name maply-ml-services

# Tag and push image
docker tag maply-ml-services:latest \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com/maply-ml-services:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/maply-ml-services:latest
```

2. **Create ECS Task Definition**

Create `task-definition.json`:

```json
{
  "family": "maply-ml-services",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "4096",
  "containerDefinitions": [
    {
      "name": "maply-ml-api",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/maply-ml-services:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "API_HOST", "value": "0.0.0.0"},
        {"name": "API_PORT", "value": "8000"},
        {"name": "LOG_LEVEL", "value": "INFO"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/maply-ml-services",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

3. **Create ECS Service**

```bash
# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
  --cluster maply-cluster \
  --service-name maply-ml-service \
  --task-definition maply-ml-services \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

### Option 2: AWS EC2

```bash
# SSH into EC2 instance
ssh -i key.pem ec2-user@<instance-ip>

# Install Docker
sudo yum update -y
sudo yum install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user

# Clone repository and deploy
git clone <repository-url>
cd ml_services
docker-compose up -d
```

### Option 3: AWS Lambda (for serverless)

Use AWS Lambda with API Gateway for serverless deployment. Note: May require modifications for cold start optimization.

---

## Google Cloud Platform

### Cloud Run (Recommended)

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/<project-id>/maply-ml-services

# Deploy to Cloud Run
gcloud run deploy maply-ml-services \
  --image gcr.io/<project-id>/maply-ml-services \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --port 8000 \
  --set-env-vars "API_HOST=0.0.0.0,API_PORT=8000,LOG_LEVEL=INFO"

# Get service URL
gcloud run services describe maply-ml-services --region us-central1
```

### Google Kubernetes Engine (GKE)

```bash
# Create cluster
gcloud container clusters create maply-cluster \
  --num-nodes=3 \
  --machine-type=n1-standard-2

# Deploy to cluster (see Kubernetes section)
```

---

## Azure Deployment

### Azure Container Instances

```bash
# Login to Azure
az login

# Create resource group
az group create --name maply-rg --location eastus

# Create container registry
az acr create --resource-group maply-rg --name maplyregistry --sku Basic

# Build and push image
az acr build --registry maplyregistry --image maply-ml-services:latest .

# Deploy container
az container create \
  --resource-group maply-rg \
  --name maply-ml-api \
  --image maplyregistry.azurecr.io/maply-ml-services:latest \
  --cpu 2 \
  --memory 4 \
  --registry-login-server maplyregistry.azurecr.io \
  --registry-username <username> \
  --registry-password <password> \
  --dns-name-label maply-ml-api \
  --ports 8000 \
  --environment-variables API_HOST=0.0.0.0 API_PORT=8000
```

---

## Kubernetes Deployment

### Deployment Configuration

Create `k8s-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: maply-ml-services
spec:
  replicas: 3
  selector:
    matchLabels:
      app: maply-ml-api
  template:
    metadata:
      labels:
        app: maply-ml-api
    spec:
      containers:
      - name: maply-ml-api
        image: maply-ml-services:latest
        ports:
        - containerPort: 8000
        env:
        - name: API_HOST
          value: "0.0.0.0"
        - name: API_PORT
          value: "8000"
        - name: LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: maply-ml-service
spec:
  selector:
    app: maply-ml-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Deploy to Kubernetes

```bash
# Apply deployment
kubectl apply -f k8s-deployment.yaml

# Check status
kubectl get deployments
kubectl get pods
kubectl get services

# View logs
kubectl logs -f deployment/maply-ml-services

# Scale deployment
kubectl scale deployment maply-ml-services --replicas=5
```

---

## Traditional VPS Deployment

### Using systemd

1. **Install dependencies**

```bash
sudo apt update
sudo apt install python3.11 python3.11-venv nginx
```

2. **Setup application**

```bash
cd /opt
sudo git clone <repository-url> maply-ml-services
cd maply-ml-services/ml_services
sudo python3.11 -m venv .venv
sudo .venv/bin/pip install -r requirements.txt
```

3. **Create systemd service**

Create `/etc/systemd/system/maply-ml-api.service`:

```ini
[Unit]
Description=MapLY ML Services API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/maply-ml-services/ml_services
Environment="PATH=/opt/maply-ml-services/ml_services/.venv/bin"
ExecStart=/opt/maply-ml-services/ml_services/.venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

4. **Start service**

```bash
sudo systemctl daemon-reload
sudo systemctl enable maply-ml-api
sudo systemctl start maply-ml-api
sudo systemctl status maply-ml-api
```

5. **Configure Nginx**

Create `/etc/nginx/sites-available/maply-ml-api`:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/maply-ml-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Environment Configuration

### Production Environment Variables

```bash
# API Settings
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false

# CORS (update with your frontend domains)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Performance
MAX_WORKERS=4
REQUEST_TIMEOUT=30

# Security (add if implementing authentication)
SECRET_KEY=your-secret-key-here
```

---

## Monitoring & Logging

### CloudWatch (AWS)

```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb
```

### Google Cloud Logging

Logs are automatically sent to Cloud Logging when using Cloud Run or GKE.

### Prometheus & Grafana

Add metrics endpoint and configure Prometheus scraping:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'maply-ml-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

---

## Security

### SSL/TLS

Use Let's Encrypt for free SSL certificates:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.com
```

### Firewall

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### API Authentication (Optional)

Consider implementing:
- API keys
- OAuth2
- JWT tokens

---

## Scaling

### Horizontal Scaling

- **Docker Compose**: Increase replicas in `docker-compose.yml`
- **Kubernetes**: Use `kubectl scale`
- **Cloud Services**: Configure auto-scaling policies

### Vertical Scaling

Increase resources (CPU, memory) based on monitoring metrics.

### Load Balancing

Use:
- AWS Application Load Balancer
- Google Cloud Load Balancing
- Azure Load Balancer
- Nginx (for VPS)

---

## Troubleshooting

### Common Issues

1. **Model not loading**
   - Check memory allocation
   - Verify model files are accessible
   - Check logs for detailed errors

2. **High response times**
   - Increase workers
   - Add caching
   - Scale horizontally

3. **CORS errors**
   - Update `CORS_ORIGINS` in environment variables
   - Verify frontend domain is included

### Health Checks

```bash
# Check API health
curl http://your-domain/health

# Check metrics
curl http://your-domain/metrics
```

---

## Backup & Recovery

### Data Backup

```bash
# Backup data directory
tar -czf data-backup-$(date +%Y%m%d).tar.gz data/

# Backup to S3
aws s3 cp data-backup-$(date +%Y%m%d).tar.gz s3://your-bucket/backups/
```

### Disaster Recovery

- Maintain infrastructure as code (Terraform, CloudFormation)
- Regular backups of data and configurations
- Document recovery procedures
- Test recovery process regularly

---

## Support

For deployment support:
- Review logs for detailed error messages
- Check cloud provider documentation
- Open an issue on GitHub
- Contact support team
