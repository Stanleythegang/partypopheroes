# GitHub Integration Guide for Hamro Platform

## 🔗 Connect Your Project to GitHub

### Step 1: Create a New Repository on GitHub

1. Go to [GitHub](https://github.com) and log in
2. Click the **"+"** icon in the top-right corner
3. Select **"New repository"**
4. Repository details:
   - **Name**: `hamro`
   - **Description**: "Full-stack e-commerce platform built with React, FastAPI, and MongoDB"
   - **Visibility**: Public or Private (your choice)
   - **DO NOT** initialize with README (we already have one)
5. Click **"Create repository"**

### Step 2: Save Code to GitHub (From Emergent Platform)

If you're using **Emergent's built-in GitHub integration**:

1. Look for the GitHub icon or "Save to GitHub" option in the Emergent UI
2. Authenticate with your GitHub account if prompted
3. Select the repository you just created (`hamro`)
4. The code will be automatically pushed

### Step 3: Manual Git Setup (Alternative Method)

If you prefer manual setup or need to push from local:

```bash
# Navigate to your project directory
cd /app

# Initialize git (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Hamro platform with React + FastAPI + MongoDB"

# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/hamro.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 4: Create .gitignore (Important!)

Make sure you have a `.gitignore` file to exclude sensitive and unnecessary files:

```bash
# Create .gitignore
cat > /app/.gitignore << 'EOF'
# Environment variables
**/.env
.env.local
.env.*.local

# Dependencies
**/node_modules/
**/__pycache__/
**/*.pyc
**/*.pyo
**/*.pyd
.Python
**/.venv/
**/venv/
**/env/

# Build outputs
**/build/
**/dist/
**/.next/

# IDE
**/.vscode/
**/.idea/
**/*.swp
**/*.swo

# OS
**/.DS_Store
**/Thumbs.db

# Logs
**/*.log
**/logs/

# Testing
**/.pytest_cache/
**/coverage/
**/.coverage

# Misc
**/*.pid
**/*.seed
**/*.pid.lock
EOF
```

## 📦 Repository Structure

Your GitHub repository will have this structure:

```
hamro/
├── frontend/              # React application
│   ├── src/
│   │   ├── components/
│   │   │   └── ui/       # Shadcn UI components
│   │   ├── App.js
│   │   ├── App.css
│   │   └── index.js
│   ├── package.json
│   └── .env              # (excluded from git)
│
├── backend/              # FastAPI application
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── auth.py       # Authentication module
│   │   ├── products.py   # Products module
│   │   └── ai.py         # AI services module
│   ├── server.py         # Main FastAPI server
│   ├── requirements.txt
│   └── .env             # (excluded from git)
│
├── README.md            # Main documentation
├── GITHUB_SETUP.md      # This file
└── .gitignore          # Git ignore rules
```

## 🚀 Deployment Information

### Current Deployment

Your Hamro platform is currently deployed on **Emergent's managed infrastructure**:

- **Frontend URL**: https://ecomm-replica-15.preview.emergentagent.com
- **Backend API**: https://ecomm-replica-15.preview.emergentagent.com/api
- **API Docs**: https://ecomm-replica-15.preview.emergentagent.com/docs

### Deployment Status

✅ Frontend: Running on port 3000 (with hot reload)
✅ Backend: Running on port 8001 (managed by supervisor)
✅ MongoDB: Connected and operational
✅ All modules: Auth, Products, AI - Loaded successfully

## 🔄 Continuous Development Workflow

### Making Changes

1. **Edit Code**: Make changes in your Emergent workspace
2. **Test Locally**: Changes auto-reload (no restart needed for code changes)
3. **Commit to Git**: 
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin main
   ```

### When to Restart Services

Only restart when:
- Installing new npm packages: `sudo supervisorctl restart frontend`
- Installing new Python packages: `sudo supervisorctl restart backend`
- Modifying .env files: `sudo supervisorctl restart all`

### Check Service Status

```bash
# Check all services
sudo supervisorctl status

# View logs
tail -f /var/log/supervisor/backend.*.log
tail -f /var/log/supervisor/frontend.*.log
```

## 📝 Environment Variables

### Required Environment Variables

**Backend (.env)**:
```bash
MONGO_URL=mongodb://localhost:27017/
DB_NAME=hamro_db
```

**Frontend (.env)**:
```bash
REACT_APP_BACKEND_URL=https://ecomm-replica-15.preview.emergentagent.com
```

**⚠️ Important**: 
- Never commit `.env` files to GitHub
- Share environment variable templates instead
- Each developer should create their own `.env` files locally

## 🛠️ Next Steps After GitHub Setup

1. **Add Collaborators**: Invite team members to your repository
2. **Set up Branch Protection**: Protect your `main` branch
3. **Configure Secrets**: Add any API keys as GitHub Secrets (not in .env)
4. **Documentation**: Keep README.md updated with new features
5. **Issues & Projects**: Use GitHub Issues for task tracking

## 📞 Support

- **Emergent Platform**: Contact support for deployment issues
- **GitHub Issues**: Use your repository's Issues tab for feature requests and bugs
- **Documentation**: Refer to README.md for setup and API documentation

---

**Ready to collaborate!** 🎉

Once you push to GitHub, your team can clone and run the project locally following the instructions in README.md.
