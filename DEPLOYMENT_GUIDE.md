# Deployment Guide - Fraud Detection API

## What is Deployment?

**Deployment** is the process of making your application available to users on the internet. Instead of running it only on your local computer (localhost), deployment puts it on a server that's accessible from anywhere.

### Why Deploy?
- ✅ Make your API accessible to others
- ✅ Share your fraud detection system with clients/users
- ✅ Run 24/7 without keeping your computer on
- ✅ Professional production environment
- ✅ Better performance and scalability

---

## Deployment Options

### 1. **Heroku** (Easiest - Recommended for Beginners)
- Free tier available
- Simple deployment process
- Automatic scaling
- Built-in monitoring

### 2. **AWS (Amazon Web Services)**
- Most popular cloud platform
- Very scalable
- Professional grade
- Pay-as-you-go pricing

### 3. **Google Cloud Platform (GCP)**
- Good free tier
- Easy to use
- Good for ML/AI projects

### 4. **DigitalOcean**
- Simple and affordable
- Good documentation
- $5/month starting price

### 5. **Railway** or **Render**
- Modern platforms
- Easy deployment
- Free tiers available

---

## Prerequisites

Before deploying, make sure you have:

1. ✅ Your code is working locally
2. ✅ All dependencies in `requirements.txt`
3. ✅ Model file in `Models/` directory
4. ✅ Git repository (optional but recommended)

---

## Option 1: Deploy to Heroku (Recommended)

### Step 1: Install Heroku CLI

**Linux:**
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

**Or download from:** https://devcenter.heroku.com/articles/heroku-cli

### Step 2: Login to Heroku

```bash
heroku login
```

### Step 3: Create Heroku App

```bash
# Navigate to your project
cd /home/sara/Downloads/Fraude_Detection_Project

# Create a new Heroku app
heroku create fraud-detection-api

# Or with a custom name
heroku create your-app-name
```

### Step 4: Prepare for Deployment

Make sure you have:
- `Procfile` (already created ✓)
- `requirements.txt` (already created ✓)
- `runtime.txt` (optional - specify Python version)

Create `runtime.txt`:
```bash
echo "python-3.11.0" > runtime.txt
```

### Step 5: Initialize Git (if not already done)

```bash
git init
git add .
git commit -m "Initial commit - Fraud Detection API"
```

### Step 6: Deploy

```bash
# Add Heroku remote
heroku git:remote -a fraud-detection-api

# Deploy
git push heroku main
# Or if using master branch:
git push heroku master
```

### Step 7: Upload Model File

Since Heroku has ephemeral filesystem, you need to store your model elsewhere or use Heroku's storage:

**Option A: Use Heroku Config Vars (for small files)**
```bash
# Not recommended for large model files
```

**Option B: Use AWS S3 or similar (Recommended)**
- Upload model to S3
- Download on app startup

**Option C: Include in Git (if model is small)**
```bash
git add Models/fraud_detection_model.pkl
git commit -m "Add model file"
git push heroku main
```

### Step 8: Open Your App

```bash
heroku open
```

Your API will be available at: `https://your-app-name.herokuapp.com`

---

## Option 2: Deploy to AWS (EC2)

### Step 1: Create AWS Account
- Go to https://aws.amazon.com
- Create free account (12 months free tier)

### Step 2: Launch EC2 Instance

1. Go to EC2 Dashboard
2. Click "Launch Instance"
3. Choose:
   - **Name**: fraud-detection-api
   - **AMI**: Ubuntu Server 22.04 LTS
   - **Instance Type**: t2.micro (Free tier)
   - **Key Pair**: Create new or use existing
   - **Security Group**: Allow HTTP (80), HTTPS (443), and Custom TCP (8000)

### Step 3: Connect to Instance

```bash
# Download your key pair
# Make it executable
chmod 400 your-key.pem

# Connect
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### Step 4: Install Dependencies on Server

```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install Python
sudo apt install python3 python3-pip python3-venv -y

# Install nginx (for reverse proxy)
sudo apt install nginx -y
```

### Step 5: Upload Your Code

**Option A: Using Git**
```bash
# On your local machine
git add .
git commit -m "Ready for deployment"
git push origin main

# On EC2 instance
git clone https://github.com/yourusername/fraud-detection-api.git
cd fraud-detection-api
```

**Option B: Using SCP**
```bash
# On your local machine
scp -i your-key.pem -r /home/sara/Downloads/Fraude_Detection_Project ubuntu@your-ec2-ip:~/
```

### Step 6: Setup Application

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test locally
uvicorn app:app --host 0.0.0.0 --port 8000
```

### Step 7: Setup Systemd Service

Create service file:
```bash
sudo nano /etc/systemd/system/fraud-api.service
```

Add this content:
```ini
[Unit]
Description=Fraud Detection API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/Fraude_Detection_Project
Environment="PATH=/home/ubuntu/Fraude_Detection_Project/venv/bin"
ExecStart=/home/ubuntu/Fraude_Detection_Project/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl daemon-reload
sudo systemctl start fraud-api
sudo systemctl enable fraud-api
```

### Step 8: Setup Nginx Reverse Proxy

```bash
sudo nano /etc/nginx/sites-available/fraud-api
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com or your-ec2-ip;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/fraud-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Option 3: Deploy to Google Cloud Platform

### Step 1: Install Google Cloud SDK

```bash
# Linux
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
```

### Step 2: Create Project

```bash
gcloud projects create fraud-detection-api
gcloud config set project fraud-detection-api
```

### Step 3: Deploy to Cloud Run

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/fraud-detection-api/fraud-api

gcloud run deploy fraud-api \
  --image gcr.io/fraud-detection-api/fraud-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1
```

---

## Option 4: Deploy with Docker (Any Platform)

### Step 1: Build Docker Image

```bash
docker build -t fraud-detection-api .
```

### Step 2: Test Locally

```bash
docker run -p 8000:8000 fraud-detection-api
```

### Step 3: Push to Docker Hub

```bash
# Login to Docker Hub
docker login

# Tag image
docker tag fraud-detection-api yourusername/fraud-detection-api

# Push
docker push yourusername/fraud-detection-api
```

### Step 4: Deploy Anywhere

Now you can deploy this Docker image to:
- AWS ECS
- Google Cloud Run
- Azure Container Instances
- DigitalOcean App Platform
- Railway
- Render

---

## Quick Deployment Scripts

### Heroku Quick Deploy

```bash
#!/bin/bash
# deploy-heroku.sh

echo "Deploying to Heroku..."

# Check if logged in
heroku auth:whoami || heroku login

# Create app if doesn't exist
heroku create fraud-detection-api 2>/dev/null || echo "App already exists"

# Deploy
git push heroku main

echo "Deployment complete!"
heroku open
```

### AWS Quick Deploy

Use the provided `aws-deploy.sh` script:
```bash
chmod +x aws-deploy.sh
./aws-deploy.sh
```

---

## Post-Deployment Checklist

After deployment, verify:

- [ ] API is accessible at the URL
- [ ] Health endpoint works: `/health`
- [ ] Model loads correctly
- [ ] Predictions work: `/predict`
- [ ] Web interface loads: `/`
- [ ] Static files are served correctly
- [ ] CORS is configured (if needed)
- [ ] Environment variables are set
- [ ] Logs are accessible
- [ ] Monitoring is set up

---

## Environment Variables

Set these in your deployment platform:

```bash
# Heroku
heroku config:set PYTHONUNBUFFERED=1

# AWS/GCP
export PYTHONUNBUFFERED=1
```

---

## Monitoring Your Deployment

### Heroku
```bash
# View logs
heroku logs --tail

# Check status
heroku ps
```

### AWS
```bash
# View logs
sudo journalctl -u fraud-api -f
```

### Health Check
Visit: `https://your-app-url/health`

---

## Troubleshooting

### Common Issues:

1. **Model not found**
   - Ensure model file is included in deployment
   - Check file paths are correct

2. **Port issues**
   - Heroku: Use `$PORT` environment variable
   - Update `Procfile` if needed

3. **Static files not loading**
   - Check static file paths
   - Verify `static/` directory is included

4. **Dependencies missing**
   - Check `requirements.txt` is complete
   - Run `pip freeze > requirements.txt` to update

---

## Cost Comparison

| Platform | Free Tier | Paid Starting |
|----------|-----------|---------------|
| Heroku | 550-1000 hours/month | $7/month |
| AWS EC2 | 750 hours/month | ~$10/month |
| GCP Cloud Run | 2M requests/month | Pay per use |
| Railway | $5 credit/month | $5/month |
| Render | Free tier available | $7/month |

---

## Recommended for Your Project

**For Beginners:** Heroku or Railway
- Easiest setup
- Good free tiers
- Great documentation

**For Production:** AWS or GCP
- More control
- Better scalability
- Professional features

**For Quick Testing:** Render or Railway
- Fast deployment
- Modern platforms
- Easy to use

---

## Next Steps

1. Choose a deployment platform
2. Follow the specific guide above
3. Test your deployed API
4. Share the URL with users
5. Monitor performance
6. Set up backups

Good luck with your deployment! 🚀


