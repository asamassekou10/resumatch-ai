# Kaggle Resume Dataset Exploration Guide

## Overview
Before we decide whether to train on the Kaggle resume dataset, we need to explore it thoroughly to understand:
- Dataset structure and format
- Data volume and quality
- Whether it has useful labels/metadata
- Whether the effort to process it is worthwhile

## Prerequisites

### 1. Install Kaggle API Credentials

You'll need a Kaggle account to download the dataset.

**Step 1: Create/Log into Kaggle Account**
- Go to https://www.kaggle.com/
- Create an account or log in

**Step 2: Get API Credentials**
- Go to https://www.kaggle.com/settings/account
- Click "Create New API Token"
- This downloads `kaggle.json`

**Step 3: Place Credentials in Right Location**

**On Windows (Local):**
```
C:\Users\<YourUsername>\.kaggle\kaggle.json
```

**In Docker:**
```
~/.kaggle/kaggle.json  (inside container)
```

## Running the Exploration

### Option A: Local Exploration (Recommended First)

**Step 1: Install dependencies locally**
```bash
pip install kagglehub pandas numpy scikit-learn
```

**Step 2: Run exploration script**
```bash
cd backend
python explore_kaggle_resumes.py
```

**Step 3: Review output**
- Script will download dataset
- Analyze structure and files
- Show samples
- Generate quality report
- Save `DATASET_EXPLORATION_REPORT.md`

### Option B: Docker Exploration

**Step 1: Rebuild Docker with new requirements**
```bash
docker-compose build backend
```

**Step 2: Run inside Docker**
```bash
docker-compose exec backend python explore_kaggle_resumes.py
```

## What the Script Does

### 1. **Downloads Dataset**
```
📥 Downloading Kaggle resume dataset...
```
Downloads the snehaanbhawal/resume-dataset (typically ~1-2GB)

### 2. **Explores Directory Structure**
```
📂 DIRECTORY STRUCTURE
- Lists all directories and files
- Counts files by type (.txt, .pdf, .json, .csv, .docx)
- Shows file organization
```

### 3. **Analyzes File Formats**
```
📄 RESUME FILE ANALYSIS
- Text files (.txt): 2247
- PDF files (.pdf): 0
- JSON files (.json): 0
- CSV files (.csv): 1
- Total resumes: 2247
```

### 4. **Samples and Previews Files**
```
📋 SAMPLE TEXT FILE ANALYSIS
- Reads 3 random text files
- Shows preview content
- Analyzes resume length
- Counts common keywords (python, java, sql, etc.)
```

### 5. **Generates Quality Report**
```
📊 DATA QUALITY ASSESSMENT

Quality Scores (0-100):
  format_variety      : ████████░░ 80%
  volume              : ██████████ 100%
  structure           : ████████░░ 80%
  completeness        : ████████░░ 80%

OVERALL QUALITY SCORE  : 85%

RECOMMENDATION:
✅ Excellent - Dataset is well-suited for training
Recommended: Proceed with FastText embeddings + Job classifier
```

## Understanding the Results

### Quality Score Interpretation

**80-100% (Excellent)**
- ✅ Dataset is well-suited for training
- ✅ Proceed with FastText embeddings
- ✅ Can add job role classifier
- Timeline: 1-2 weeks for full implementation

**60-79% (Good)**
- ⚠️ Dataset needs some processing
- ✅ Start with FastText embeddings only
- ⚠️ Classifier needs more data
- Timeline: 3-5 days for embeddings

**40-59% (Moderate)**
- ⚠️ Significant processing needed
- ✅ Explore further before committing
- ⚠️ Might not be worth effort
- Recommendation: Assess cost-benefit

**Below 40% (Limited)**
- ❌ Dataset not suitable for training
- ✅ Continue with manual curation
- ❌ Skip machine learning approach
- Recommendation: Stick with keyword database

## Decision Tree

After exploration, you'll be able to make informed decision:

```
Is quality score > 80%?
├─ YES → Proceed with full implementation
│        ├─ FastText embeddings (4-6 hours)
│        └─ Job role classifier (8-12 hours)
│
└─ NO → Is quality score > 60%?
   ├─ YES → FastText embeddings only (4-6 hours)
   └─ NO → Consider alternatives
          ├─ Manual keyword expansion
          ├─ Using embeddings from pre-trained model
          └─ Skip ML approach entirely
```

## What We'll Learn

After exploration, we'll know:

1. **Dataset Structure**
   - How are resumes organized?
   - What formats are they in?
   - Is there metadata/labels?

2. **Data Quality**
   - How many resumes?
   - How clean is the text?
   - What's the average quality?

3. **Content Analysis**
   - What keywords are common?
   - What job titles appear?
   - What industries are represented?

4. **Feasibility**
   - Is dataset large enough?
   - Is processing reasonable?
   - Worth the effort?

## Next Steps After Exploration

### If Score ≥ 80%: Full Implementation
We'll build:
1. **FastText Embeddings** (4-6 hours)
   - Train on resume text
   - Get semantic similarity
   - Integrate into KeywordManager

2. **Job Role Classifier** (8-12 hours)
   - Train to detect job titles
   - Classify resumes automatically
   - Use for context-aware scoring

3. **Integration** (2-4 hours)
   - Add to keyword extraction
   - Update scoring logic
   - Test and validate

### If Score 60-79%: Embeddings Only
We'll build:
1. **FastText Embeddings** (4-6 hours)
   - Train on resume text
   - Improve keyword similarity
   - Integrate into KeywordManager

2. **Testing & Validation** (2-3 hours)
   - Measure improvements
   - Compare before/after
   - Document results

### If Score < 60%: Alternative Approach
Options:
1. **Use Pre-trained Embeddings**
   - Use fasttext.en pre-trained model
   - No training needed
   - Good baseline results

2. **Manual Keyword Expansion**
   - Manually add more keywords to database
   - Use domain expertise
   - No ML needed

3. **Hybrid Approach**
   - Keep current system
   - Add fuzzy matching rules
   - Improve gradually over time

## Timeline

| Phase | Time | Depends On |
|-------|------|-----------|
| Exploration | 15 min | Script completion |
| Decision | 30 min | Your preference |
| FastText Training | 4-6 hrs | Volume/quality |
| Job Classifier | 8-12 hrs | Labeled data |
| Integration | 2-4 hrs | API updates |
| Testing | 2-3 hrs | Validation |
| **TOTAL** | **1-2 weeks** | Full approach |

## Common Issues & Solutions

### Issue: Kaggle API not found
**Solution:**
```bash
pip install kagglehub
```

### Issue: Authentication failed
**Solution:**
- Ensure `~/.kaggle/kaggle.json` exists
- Check permissions: `chmod 600 ~/.kaggle/kaggle.json`
- Create new token from kaggle.com/settings/account

### Issue: Out of memory
**Solution:**
- Script only samples data, shouldn't use much RAM
- If still issues, reduce sample_size in script

### Issue: Very slow download
**Solution:**
- Dataset is 1-2GB
- May take 5-10 minutes on normal connection
- Be patient!

## Questions?

After running exploration, we'll have answers to:
1. **Is the dataset useful?** (quality score will tell us)
2. **What format is it?** (text, JSON, CSV, PDF?)
3. **How much data?** (number of resumes)
4. **What's in it?** (keywords, structure, metadata?)
5. **Should we train on it?** (recommendation based on scores)

Once you have the exploration results, share them and we'll decide together on the next approach!

---

**Ready to explore? Run this:**
```bash
python backend/explore_kaggle_resumes.py
```
