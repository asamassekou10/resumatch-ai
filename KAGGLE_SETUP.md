# Kaggle API Setup - Quick Guide

## What You Need
- A Kaggle account (free at https://www.kaggle.com)
- API credentials (one-time setup)

## Step-by-Step Setup

### 1️⃣ Create Kaggle Account (if needed)
- Visit https://www.kaggle.com/signup
- Sign up with email or Google/GitHub

### 2️⃣ Get API Credentials

**On Windows:**

1. Go to https://www.kaggle.com/settings/account
2. Scroll down to "API" section
3. Click **"Create New API Token"**
   - This downloads `kaggle.json` file
   - Save it somewhere you can access

### 3️⃣ Move Credentials to Right Location

**On Windows PowerShell:**
```powershell
# Check if .kaggle directory exists
Test-Path "$env:USERPROFILE\.kaggle"

# Create directory if it doesn't exist
mkdir "$env:USERPROFILE\.kaggle" -Force

# Copy kaggle.json to the directory
Copy-Item "C:\Users\<YourUsername>\Downloads\kaggle.json" `
          "$env:USERPROFILE\.kaggle\kaggle.json"
```

**On Windows Command Prompt:**
```cmd
# Create directory if needed
if not exist "%USERPROFILE%\.kaggle" mkdir "%USERPROFILE%\.kaggle"

# Copy kaggle.json
copy "C:\Users\<YourUsername>\Downloads\kaggle.json" "%USERPROFILE%\.kaggle\kaggle.json"
```

**On Mac/Linux:**
```bash
mkdir -p ~/.kaggle
cp ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

### 4️⃣ Verify Setup

**Windows PowerShell:**
```powershell
Test-Path "$env:USERPROFILE\.kaggle\kaggle.json"
# Should return: True
```

**Windows CMD or Mac/Linux:**
```bash
ls ~/.kaggle/kaggle.json
# Should show the file
```

## Now You're Ready!

### Option A: Local Exploration (Recommended)

**Step 1: Install dependencies**
```bash
pip install kagglehub pandas numpy
```

**Step 2: Run exploration**
```bash
cd path/to/AI\ RESUME\ ANALYZER
python explore_dataset_local.py
```

**Step 3: Wait for analysis**
- Download takes 5-10 minutes
- Analysis takes 2-3 minutes
- You'll see detailed report in terminal

### Option B: Docker Exploration

**Step 1: Rebuild Docker**
```bash
docker-compose build backend
```

**Step 2: Run in Docker**
```bash
docker-compose exec backend python explore_kaggle_resumes.py
```

**Note:** Docker needs Kaggle credentials mounted. Easier to use Option A first.

## What Happens Next

The script will:
1. ✅ Download dataset (~1-2 GB)
2. ✅ Analyze structure and file types
3. ✅ Sample resume content
4. ✅ Count keywords
5. ✅ Generate quality score (0-100)
6. ✅ Provide recommendations

## Troubleshooting

### ❌ "kagglehub not found"
```bash
pip install kagglehub
```

### ❌ "Authentication failed"
Check these:
1. Is kaggle.json in correct location?
   - Windows: `C:\Users\<YourUsername>\.kaggle\kaggle.json`
   - Mac/Linux: `~/.kaggle/kaggle.json`

2. Is it the right file?
   - Should contain `username` and `key` fields
   - Not empty

3. Try creating new token:
   - https://www.kaggle.com/settings/account
   - Delete old token
   - Create new API token
   - Re-download kaggle.json

### ❌ "Connection timeout"
- Check internet connection
- Dataset is large (1-2 GB), may take time
- Try again later if rate limited

### ❌ "Out of memory"
- Script only samples, shouldn't need much RAM
- Close other applications
- Try on machine with more RAM

## What the Score Means

After exploration, you'll get a score 0-100:

| Score | Meaning | Action |
|-------|---------|--------|
| **80-100** | Excellent | Proceed with full ML training |
| **60-79** | Good | FastText embeddings only |
| **40-59** | Moderate | Evaluate carefully |
| **0-39** | Limited | Skip ML, use alternatives |

## Next Step

1. **Run the exploration:**
   ```bash
   python explore_dataset_local.py
   ```

2. **Share the results with me** (especially the score and recommendation)

3. **We'll decide together** on which approach to take:
   - FastText embeddings (4-6 hours)
   - Job role classifier (8-12 hours)
   - Combined (1-2 weeks)
   - Or alternative approach

---

**Questions?** See [EXPLORATION_GUIDE.md](EXPLORATION_GUIDE.md) for detailed info.
