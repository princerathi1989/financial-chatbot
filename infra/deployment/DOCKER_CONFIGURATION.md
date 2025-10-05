# Multi-Agent Chatbot - Docker Configuration

## Development Setup

### Docker Compose for Local Development

```yaml
version: '3.8'

services:
  chatbot:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DEBUG=true
      - LOG_LEVEL=DEBUG
    volumes:
      - ./storage:/app/storage
      - ./logs:/app/logs
    depends_on:
      - chromadb
    restart: unless-stopped

  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000"
    volumes:
      - chroma_data:/chroma/chroma
    environment:
      - CHROMA_SERVER_HOST=0.0.0.0
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    restart: unless-stopped

volumes:
  chroma_data:
  prometheus_data:
  grafana_data:
```

## Production Dockerfile

```dockerfile
# Multi-stage build for production
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r chatbot && useradd -r -g chatbot chatbot

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/storage /app/logs && \
    chown -R chatbot:chatbot /app

# Switch to non-root user
USER chatbot

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

## Kubernetes Deployment

### Namespace
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: chatbot-system
```

### ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: chatbot-config
  namespace: chatbot-system
data:
  LOG_LEVEL: "INFO"
  MAX_FILE_SIZE_MB: "50"
  RAG_TOP_K_RESULTS: "5"
  SUMMARY_MAX_LENGTH: "500"
  MCQ_NUM_QUESTIONS: "5"
```

### Secret
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: chatbot-secrets
  namespace: chatbot-system
type: Opaque
data:
  OPENAI_API_KEY: <base64-encoded-api-key>
```

### Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chatbot
  namespace: chatbot-system
spec:
  replicas: 3
  selector:
    matchLabels:
      app: chatbot
  template:
    metadata:
      labels:
        app: chatbot
    spec:
      containers:
      - name: chatbot
        image: chatbot:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: chatbot-secrets
              key: OPENAI_API_KEY
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: chatbot-config
              key: LOG_LEVEL
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
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
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: chatbot-service
  namespace: chatbot-system
spec:
  selector:
    app: chatbot
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

### Ingress
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: chatbot-ingress
  namespace: chatbot-system
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - chatbot.example.com
    secretName: chatbot-tls
  rules:
  - host: chatbot.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: chatbot-service
            port:
              number: 80
```

## Environment Variables

### Required Variables
- `OPENAI_API_KEY`: OpenAI API key for LLM access

### Optional Variables
- `DEBUG`: Enable debug mode (default: false)
- `LOG_LEVEL`: Logging level (default: INFO)
- `MAX_FILE_SIZE_MB`: Maximum file size in MB (default: 50)
- `CHROMA_PERSIST_DIRECTORY`: ChromaDB persistence directory
- `UPLOAD_DIRECTORY`: File upload directory

## Monitoring Configuration

### Prometheus Configuration
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'chatbot'
    static_configs:
      - targets: ['chatbot:8000']
    metrics_path: /metrics
    scrape_interval: 5s
```

### Grafana Dashboard
```json
{
  "dashboard": {
    "title": "Multi-Agent Chatbot Metrics",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      }
    ]
  }
}
```

## Security Considerations

### Network Policies
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: chatbot-network-policy
  namespace: chatbot-system
spec:
  podSelector:
    matchLabels:
      app: chatbot
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to: []
    ports:
    - protocol: TCP
      port: 443  # HTTPS for OpenAI API
```

### Pod Security Policy
```yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: chatbot-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
```

## Backup and Recovery

### Database Backup
```bash
#!/bin/bash
# backup-chromadb.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/chromadb"
mkdir -p $BACKUP_DIR

# Backup ChromaDB data
kubectl exec -n chatbot-system deployment/chromadb -- \
  tar -czf /tmp/chromadb-backup-$DATE.tar.gz /chroma/chroma

# Copy backup to local storage
kubectl cp chatbot-system/chromadb-pod:/tmp/chromadb-backup-$DATE.tar.gz \
  $BACKUP_DIR/chromadb-backup-$DATE.tar.gz

echo "Backup completed: $BACKUP_DIR/chromadb-backup-$DATE.tar.gz"
```

### Application Data Backup
```bash
#!/bin/bash
# backup-app-data.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/app-data"
mkdir -p $BACKUP_DIR

# Backup application data
kubectl exec -n chatbot-system deployment/chatbot -- \
  tar -czf /tmp/app-data-backup-$DATE.tar.gz /app/storage

# Copy backup to local storage
kubectl cp chatbot-system/chatbot-pod:/tmp/app-data-backup-$DATE.tar.gz \
  $BACKUP_DIR/app-data-backup-$DATE.tar.gz

echo "Backup completed: $BACKUP_DIR/app-data-backup-$DATE.tar.gz"
```
