# Deploy

## 1. GitHub Pages

No repositório → Settings → Pages → Source: **GitHub Actions**

## 2. S3 — Acesso público

Bucket: `nbds-podcast` (us-east-2)

### Desativar Block Public Access

```bash
aws s3api put-public-access-block \
  --bucket nbds-podcast \
  --public-access-block-configuration \
  BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false
```

### Bucket policy (leitura pública)

```bash
aws s3api put-bucket-policy --bucket nbds-podcast --policy '{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::nbds-podcast/*"
  }]
}'
```

### CORS (para o audio player)

```bash
aws s3api put-bucket-cors --bucket nbds-podcast --cors-configuration '{
  "CORSRules": [{
    "AllowedOrigins": ["https://nabocadosol.github.io"],
    "AllowedMethods": ["GET"],
    "AllowedHeaders": ["*"],
    "MaxAgeSeconds": 86400
  }]
}'
```

## 3. Upload de arquivos

```bash
aws s3 sync arquivos/ s3://nbds-podcast/ --exclude "*.txt" --exclude "*.md" --exclude "*.json" --exclude "*.html"
```
