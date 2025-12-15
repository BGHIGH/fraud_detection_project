# GitLab Pipeline Troubleshooting Guide

## Common Pipeline Failures and Solutions

### 1. Build Stage Fails: Docker Build Error

**Error**: `Cannot connect to the Docker daemon` or `docker build failed`

**Solutions**:
- ✅ **Fixed**: Updated Docker-in-Docker configuration in `.gitlab-ci.yml`
- Make sure Container Registry is enabled in GitLab (Settings → General → Visibility)
- Check if you have Docker runner available (GitLab.com provides shared runners)

**Check**:
```bash
# Verify Dockerfile exists
ls -la Dockerfile

# Check if all required files are committed
git status
```

### 2. Build Stage Fails: Missing Files

**Error**: `COPY failed: file not found` or `requirements.txt not found`

**Solutions**:
- Make sure all files are committed to git:
  ```bash
  git add .
  git commit -m "Add all files"
  git push
  ```
- Check `.gitignore` doesn't exclude important files
- Verify `requirements.txt` exists

### 3. Test Stage Fails: Model File Not Found

**Error**: `FileNotFoundError: Models/fraud_detection_model.pkl`

**Solutions**:
- **Important**: The model file must be committed to git:
  ```bash
  # Check if model is in git
  git ls-files Models/fraud_detection_model.pkl
  
  # If not, add it
  git add Models/fraud_detection_model.pkl
  git commit -m "Add model file"
  git push
  ```
- If model is too large (>10MB), use Git LFS:
  ```bash
  git lfs install
  git lfs track "*.pkl"
  git add .gitattributes
  git add Models/fraud_detection_model.pkl
  git commit -m "Add model with Git LFS"
  git push
  ```

### 4. Build Stage Fails: Container Registry Authentication

**Error**: `unauthorized: authentication required` or `401 Unauthorized`

**Solutions**:
- Container Registry is automatically enabled on GitLab.com
- For self-hosted GitLab, enable it in Settings → General → Visibility
- The `CI_REGISTRY_USER` and `CI_REGISTRY_PASSWORD` are automatically provided by GitLab

### 5. Pipeline Fails: Runner Not Available

**Error**: `No runners available` or `This job is stuck`

**Solutions**:
- On GitLab.com: Shared runners are enabled by default
- Check Settings → CI/CD → Runners
- For self-hosted: Make sure you have runners registered

### 6. Test Stage Fails: Import Error

**Error**: `ModuleNotFoundError` or `ImportError`

**Solutions**:
- Check `requirements.txt` includes all dependencies
- Verify Python version matches (3.11)
- Test locally first:
  ```bash
  pip install -r requirements.txt
  python3 -c "from app import app"
  ```

## How to Debug Pipeline Failures

### Step 1: Check Pipeline Logs

1. Go to **CI/CD** → **Pipelines**
2. Click on the failed pipeline
3. Click on the failed job (build/test/deploy)
4. Scroll through the logs to find the error

### Step 2: Check Common Issues

```bash
# 1. Verify all files are committed
git status

# 2. Check if model file exists locally
ls -la Models/fraud_detection_model.pkl

# 3. Test Docker build locally
docker build -t fraud-detection-test .

# 4. Test app locally
python3 -c "from app import app; print('OK')"
```

### Step 3: Check GitLab Settings

1. **Container Registry**: Settings → General → Visibility → Enable "Container Registry"
2. **Runners**: Settings → CI/CD → Runners → Check if runners are available
3. **Variables**: Settings → CI/CD → Variables → Check if needed variables are set

## Quick Fixes

### Fix 1: Add Missing Files

```bash
# Add all files including model
git add Models/fraud_detection_model.pkl
git add .
git commit -m "Add missing files"
git push
```

### Fix 2: Use Git LFS for Large Model

```bash
# Install Git LFS
git lfs install

# Track .pkl files
git lfs track "*.pkl"
git add .gitattributes

# Add model
git add Models/fraud_detection_model.pkl
git commit -m "Add model with Git LFS"
git push
```

### Fix 3: Simplify Pipeline (Remove Docker Build)

If Docker build keeps failing, you can temporarily disable it:

```yaml
# Comment out build stage temporarily
# build:
#   stage: build
#   ...
```

## Check Your Pipeline Status

1. **Pipeline ID**: Check the pipeline number (e.g., #2215027269)
2. **Commit**: Check which commit failed (dd56c3d8)
3. **Stage**: See which stage failed (build/test/deploy)
4. **Job**: Click on the failed job to see detailed logs

## Most Common Fix

**90% of failures are due to missing model file in git:**

```bash
# Make sure model is committed
git add Models/fraud_detection_model.pkl
git commit -m "Add model file"
git push

# Then re-run pipeline
```

## Still Having Issues?

1. **Check the exact error** in pipeline logs
2. **Verify all files** are committed to git
3. **Test locally** before pushing
4. **Check GitLab documentation** for your GitLab version

## Success Checklist

- ✅ All files committed to git
- ✅ Model file included (or using Git LFS)
- ✅ Container Registry enabled
- ✅ Runners available
- ✅ Dockerfile exists and is correct
- ✅ requirements.txt is complete
- ✅ Pipeline configuration is valid

