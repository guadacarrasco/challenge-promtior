# Railway Deployment Guide

## Prerequisites

1. **GitHub Account** with code pushed
2. **Railway Account** (free tier available at https://railway.app)
3. Local testing complete and working

## Step-by-Step Deployment

### Step 1: Prepare GitHub Repository

Ensure all code is pushed to GitHub:

```bash
# Check current branch
git branch

# Push to main branch
git push origin main

# Verify all changes are pushed
git status  # Should show "nothing to commit"
```

### Step 2: Create Railway Account

1. Go to https://railway.app
2. Sign up with GitHub (recommended)
3. Authorize Railway to access your GitHub account

### Step 3: Create New Railway Project

1. Login to Railway dashboard
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository
5. Select `main` branch for auto-deploy

### Step 4: Configure Environment Variables

In Railway project settings, add environment variables:

```env
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama2
VECTOR_STORE_PATH=/app/chroma_data
DEBUG=False
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
```

**Important**: Set `DEBUG=False` for production!

### Step 5: Configure Port

The Dockerfile already specifies port 8000. Railway will automatically detect this.

To set a custom domain:
1. Go to **Settings**
2. Click **"Generate Domain"**
3. Copy the provided URL

### Step 6: Monitor Deployment

Railway automatically triggers deployment on push to main:

1. Go to **Deployments** tab
2. Watch the build progress
3. Check logs if issues occur

Deployment typically takes 3-5 minutes.

### Step 7: Test Production Deployment

Once deployed, test the API:

```bash
# Replace with your Railway URL
export RAILWAY_URL="https://your-railway-url.railway.app"

# Health check
curl $RAILWAY_URL/api/health

# Test chat
curl -X POST $RAILWAY_URL/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Promtior?"}'

# Test frontend
open $RAILWAY_URL
```

## Advanced Configuration

### Persistent Storage

For production, use persistent volumes:

1. In Railway dashboard, go to **Storage**
2. Create a volume at `/app/chroma_data`
3. This ensures vector store survives deployments

### Custom Domain

1. Go to **Settings**
2. Add custom domain if you own one
3. Update frontend `NEXT_PUBLIC_API_URL` if needed

### Environment-Specific Config

Create `.railway.json` in root (optional):

```json
{
  "build": {
    "dockerfile": "Dockerfile",
    "context": "."
  }
}
```

## Monitoring

### View Logs

```bash
# In Railway dashboard, click "Logs" tab
# Filter by service (backend)
# Search for errors
```

### Common Issues

**Issue**: "Build failed"
- Check Dockerfile syntax
- Verify all dependencies in pyproject.toml
- Check Node dependencies in package.json

**Issue**: "Service crashed"
- Check logs for errors
- Often related to missing environment variables
- Verify Ollama connectivity

**Issue**: "Vector store empty"
- Vector store initialization might not have run
- Add POST request trigger or run manually
- Check persistent storage is set up

### Performance Monitoring

Railway dashboard shows:
- CPU usage
- Memory usage
- Network I/O
- Build duration

Monitor key metrics during deployment and first uses.

## Troubleshooting

### Deployment Won't Start

1. Check Dockerfile builds locally:
   ```bash
   docker build -t test .
   docker run -p 8000:8000 test
   ```

2. Verify environment variables
3. Check Railway logs for specific errors

### API Not Responding

1. Check health endpoint: `GET /api/health`
2. View application logs in Railway
3. Verify vector store is initialized

### Slow Responses

- First request may be slow (model loading)
- LLaMA2 on small instance may be slower
- Consider upgrading Railway plan if needed

## Rollback

To rollback to previous deployment:

1. Go to **Deployments**
2. Right-click on previous deployment
3. Select **"Redeploy"**

## Next Steps After Deployment

### Set Up Custom Domain

```bash
# If you own a domain
# Update DNS to point to Railway URL
# Configure in Railway settings
```

### Enable Monitoring

```bash
# Set up alerts in Railway dashboard
# Monitor error rates
# Track performance metrics
```

### Automated Updates

Railway automatically deploys on:
- Push to main branch
- Manual redeploy button
- Scheduled redeploy (if configured)

### Support

For Railway-specific issues:
- Check Railway docs: https://docs.railway.app
- Contact Railway support
- Check GitHub issues for common problems

## Cost Estimates

Railway free tier includes:
- 500 CPU hours/month
- 100 GB storage
- Approximately 50-100 hrs of continuous service

For higher usage, consider paid plans.

## Production Checklist

- [ ] All tests passing locally
- [ ] `DEBUG=False` in environment
- [ ] Custom domain configured
- [ ] Persistent storage set up
- [ ] Environment variables configured
- [ ] Health check working
- [ ] Chat endpoint responding
- [ ] Logs being monitored
- [ ] Rollback plan in place
- [ ] Documentation updated

## Deployment Complete!

Your Promtior RAG Chatbot is now live!

Access at: `https://your-railway-url.railway.app`

Share the link with users and start getting feedback!

