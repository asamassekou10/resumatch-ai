"""
Kaggle Resume Dataset Exploration Script

Downloads and analyzes the snehaanbhawal/resume-dataset from Kaggle.
Provides comprehensive insights to decide if data is suitable for training.

Run with: python explore_kaggle_resumes.py
Requires: kagglehub, pandas, numpy
"""

import os
import json
import logging
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def download_dataset():
    """Download Kaggle resume dataset"""
    logger.info("📥 Downloading Kaggle resume dataset...")

    try:
        import kagglehub
    except ImportError:
        logger.error("❌ kagglehub not installed. Install with: pip install kagglehub")
        return None

    try:
        path = kagglehub.dataset_download("snehaanbhawal/resume-dataset")
        logger.info(f"✅ Dataset downloaded to: {path}")
        return path
    except Exception as e:
        logger.error(f"❌ Failed to download dataset: {str(e)}")
        return None


def explore_directory_structure(dataset_path):
    """Explore the directory structure of the dataset"""
    logger.info("\n📂 DIRECTORY STRUCTURE")
    logger.info("=" * 60)

    path = Path(dataset_path)

    # List all directories and files
    items = list(path.rglob('*'))

    # Categorize by type
    files_by_ext = defaultdict(list)
    directories = []

    for item in items:
        if item.is_dir():
            directories.append(item)
        else:
            ext = item.suffix if item.suffix else 'no_extension'
            files_by_ext[ext].append(item)

    logger.info(f"\nDirectories found: {len(directories)}")
    for d in directories[:10]:  # Show first 10
        logger.info(f"  📁 {d.relative_to(path)}")
    if len(directories) > 10:
        logger.info(f"  ... and {len(directories) - 10} more")

    logger.info(f"\nFiles by extension:")
    for ext, files in sorted(files_by_ext.items(), key=lambda x: len(x[1]), reverse=True):
        logger.info(f"  {ext}: {len(files)} files")

    return files_by_ext, directories


def analyze_resume_files(dataset_path, files_by_ext):
    """Analyze resume files - determine format and structure"""
    logger.info("\n📄 RESUME FILE ANALYSIS")
    logger.info("=" * 60)

    # Check for common formats
    txt_files = files_by_ext.get('.txt', [])
    pdf_files = files_by_ext.get('.pdf', [])
    json_files = files_by_ext.get('.json', [])
    docx_files = files_by_ext.get('.docx', [])
    csv_files = files_by_ext.get('.csv', [])

    logger.info(f"\nResume formats detected:")
    logger.info(f"  TXT files:  {len(txt_files)}")
    logger.info(f"  PDF files:  {len(pdf_files)}")
    logger.info(f"  JSON files: {len(json_files)}")
    logger.info(f"  DOCX files: {len(docx_files)}")
    logger.info(f"  CSV files:  {len(csv_files)}")

    total_resumes = len(txt_files) + len(pdf_files) + len(json_files) + len(docx_files)
    logger.info(f"\nTotal resumes: {total_resumes}")

    return {
        'txt': txt_files,
        'pdf': pdf_files,
        'json': json_files,
        'docx': docx_files,
        'csv': csv_files
    }


def sample_text_files(txt_files, sample_size=3):
    """Sample and analyze text files"""
    logger.info(f"\n📋 SAMPLE TEXT FILE ANALYSIS (sampling {min(sample_size, len(txt_files))} files)")
    logger.info("=" * 60)

    if not txt_files:
        logger.info("❌ No text files found")
        return

    import random
    samples = random.sample(txt_files, min(sample_size, len(txt_files)))

    resume_lengths = []
    keyword_counts = defaultdict(int)

    for i, file_path in enumerate(samples, 1):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            logger.info(f"\n📌 Sample {i}: {file_path.name}")
            logger.info(f"   Length: {len(content)} characters")

            # Show first 300 characters
            preview = content[:300].replace('\n', ' ')
            logger.info(f"   Preview: {preview}...")

            resume_lengths.append(len(content))

            # Count some common keywords
            content_lower = content.lower()
            for keyword in ['python', 'java', 'javascript', 'sql', 'react', 'job', 'experience', 'skills', 'education']:
                if keyword in content_lower:
                    keyword_counts[keyword] += 1

        except Exception as e:
            logger.error(f"   ❌ Error reading file: {str(e)}")

    if resume_lengths:
        logger.info(f"\n📊 Resume Length Statistics:")
        logger.info(f"   Average: {sum(resume_lengths) / len(resume_lengths):.0f} characters")
        logger.info(f"   Min: {min(resume_lengths)} characters")
        logger.info(f"   Max: {max(resume_lengths)} characters")

    logger.info(f"\n🔍 Common Keywords in Samples:")
    for keyword, count in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True):
        logger.info(f"   {keyword}: found in {count}/{len(samples)} samples")


def sample_json_files(json_files, sample_size=2):
    """Sample and analyze JSON files"""
    logger.info(f"\n📋 SAMPLE JSON FILE ANALYSIS (sampling {min(sample_size, len(json_files))} files)")
    logger.info("=" * 60)

    if not json_files:
        logger.info("❌ No JSON files found")
        return

    import random
    samples = random.sample(json_files, min(sample_size, len(json_files)))

    for i, file_path in enumerate(samples, 1):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                data = json.load(f)

            logger.info(f"\n📌 Sample {i}: {file_path.name}")

            if isinstance(data, dict):
                logger.info(f"   Type: Dictionary with keys: {list(data.keys())}")

                # Show sample values
                for key, value in list(data.items())[:5]:
                    if isinstance(value, str):
                        preview = str(value)[:100].replace('\n', ' ')
                        logger.info(f"   {key}: {preview}...")
                    elif isinstance(value, (list, dict)):
                        logger.info(f"   {key}: {type(value).__name__} with {len(value)} items")
                    else:
                        logger.info(f"   {key}: {value}")

            elif isinstance(data, list):
                logger.info(f"   Type: List with {len(data)} items")
                if data:
                    logger.info(f"   First item: {type(data[0])}")
                    if isinstance(data[0], dict):
                        logger.info(f"   First item keys: {list(data[0].keys())[:10]}")

        except json.JSONDecodeError as e:
            logger.error(f"   ❌ Invalid JSON: {str(e)}")
        except Exception as e:
            logger.error(f"   ❌ Error reading file: {str(e)}")


def analyze_csv_files(csv_files):
    """Analyze CSV files if present"""
    logger.info(f"\n📋 CSV FILE ANALYSIS")
    logger.info("=" * 60)

    if not csv_files:
        logger.info("❌ No CSV files found")
        return

    try:
        import pandas as pd
    except ImportError:
        logger.warning("⚠️  pandas not installed. Skipping CSV analysis.")
        return

    for file_path in csv_files[:3]:  # Analyze first 3
        try:
            logger.info(f"\n📌 {file_path.name}")

            df = pd.read_csv(file_path, nrows=10)

            logger.info(f"   Shape: {df.shape[0]} rows, {df.shape[1]} columns")
            logger.info(f"   Columns: {list(df.columns)}")

            # Show sample
            logger.info(f"   First row preview:")
            for col in df.columns[:5]:
                value = str(df[col].iloc[0])[:80].replace('\n', ' ')
                logger.info(f"     {col}: {value}")

        except Exception as e:
            logger.error(f"   ❌ Error analyzing: {str(e)}")


def generate_quality_report(dataset_path, file_stats):
    """Generate quality assessment report"""
    logger.info("\n📊 DATA QUALITY ASSESSMENT")
    logger.info("=" * 60)

    total_files = sum(len(files) for files in file_stats.values())

    quality_scores = {
        'format_variety': 0,
        'volume': 0,
        'structure': 0,
        'completeness': 0
    }

    # Format variety score
    formats_present = sum(1 for files in file_stats.values() if files)
    quality_scores['format_variety'] = min(formats_present / 3 * 100, 100)  # Max 100

    # Volume score
    if total_files >= 1000:
        quality_scores['volume'] = 100
    elif total_files >= 500:
        quality_scores['volume'] = 80
    elif total_files >= 100:
        quality_scores['volume'] = 60
    elif total_files >= 10:
        quality_scores['volume'] = 40
    else:
        quality_scores['volume'] = 20

    # Structure score (bonus if organized)
    dataset_p = Path(dataset_path)
    subdirs = len([d for d in dataset_p.iterdir() if d.is_dir()])
    if subdirs > 5:
        quality_scores['structure'] = 100
    elif subdirs > 2:
        quality_scores['structure'] = 80
    else:
        quality_scores['structure'] = 50

    # Overall completeness
    if 'csv' in file_stats and file_stats['csv']:
        quality_scores['completeness'] = 100  # CSV likely has metadata
    elif 'json' in file_stats and file_stats['json']:
        quality_scores['completeness'] = 80
    else:
        quality_scores['completeness'] = 50

    avg_score = sum(quality_scores.values()) / len(quality_scores)

    logger.info(f"\nQuality Scores (0-100):")
    for metric, score in quality_scores.items():
        bar = "█" * int(score / 10) + "░" * (10 - int(score / 10))
        logger.info(f"  {metric:20s}: {bar} {score:.0f}%")

    logger.info(f"\n{'OVERALL QUALITY SCORE':<20s}: {avg_score:.0f}%")

    # Recommendation
    logger.info(f"\n💡 RECOMMENDATION:")
    if avg_score >= 80:
        logger.info("   ✅ Excellent - Dataset is well-suited for training")
        logger.info("   Recommended: Proceed with FastText embeddings + Job classifier")
    elif avg_score >= 60:
        logger.info("   ⚠️  Good - Dataset has potential but needs some processing")
        logger.info("   Recommended: Start with FastText embeddings only")
    elif avg_score >= 40:
        logger.info("   ⚠️  Moderate - Dataset needs significant processing")
        logger.info("   Recommended: Explore further or use simpler approach")
    else:
        logger.info("   ❌ Limited - Dataset may not be suitable for training")
        logger.info("   Recommended: Continue with manual keyword curation")


def create_summary_report(dataset_path, file_stats):
    """Create a summary report file"""
    report_path = Path(dataset_path).parent / "DATASET_EXPLORATION_REPORT.md"

    total_files = sum(len(files) for files in file_stats.values())

    report = f"""# Kaggle Resume Dataset - Exploration Report

## Summary
- **Dataset**: snehaanbhawal/resume-dataset
- **Downloaded**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Total Files**: {total_files}

## File Format Distribution
- Text files (.txt): {len(file_stats.get('txt', []))}
- PDF files (.pdf): {len(file_stats.get('pdf', []))}
- JSON files (.json): {len(file_stats.get('json', []))}
- DOCX files (.docx): {len(file_stats.get('docx', []))}
- CSV files (.csv): {len(file_stats.get('csv', []))}

## Key Findings
See terminal output for detailed analysis.

## Recommended Next Steps
1. Check the terminal output above for data quality assessment
2. Review sample file contents to understand data structure
3. Decide on training approach:
   - **Option A**: FastText embeddings (quick win)
   - **Option B**: Job role classifier (more complex)
   - **Option C**: Combined approach (best results)

## Notes
- If volume >= 1000 resumes: Suitable for all training approaches
- If volume >= 500 resumes: Good for embeddings, classifier needs more data
- If volume < 500 resumes: Limited use, prefer manual curation approach
- If JSON/CSV available: Better for structured learning
- If only text files: Limited metadata, harder for job classification

---
Generated by explore_kaggle_resumes.py
"""

    try:
        with open(report_path, 'w') as f:
            f.write(report)
        logger.info(f"\n📝 Report saved to: {report_path}")
    except Exception as e:
        logger.error(f"Failed to save report: {str(e)}")


def main():
    """Main exploration workflow"""
    logger.info("🚀 KAGGLE RESUME DATASET EXPLORATION")
    logger.info("=" * 60)

    # Step 1: Download dataset
    dataset_path = download_dataset()
    if not dataset_path:
        logger.error("❌ Failed to download dataset. Exiting.")
        return

    # Step 2: Explore directory structure
    file_stats, directories = explore_directory_structure(dataset_path)

    # Step 3: Analyze resume files
    resume_files = analyze_resume_files(dataset_path, file_stats)

    # Step 4: Sample and analyze different file types
    if resume_files['txt']:
        sample_text_files(resume_files['txt'], sample_size=3)

    if resume_files['json']:
        sample_json_files(resume_files['json'], sample_size=2)

    if resume_files['csv']:
        analyze_csv_files(resume_files['csv'])

    # Step 5: Generate quality report
    generate_quality_report(dataset_path, file_stats)

    # Step 6: Create summary report
    create_summary_report(dataset_path, file_stats)

    logger.info("\n" + "=" * 60)
    logger.info("✅ EXPLORATION COMPLETE")
    logger.info("=" * 60)
    logger.info("\n📋 Next steps:")
    logger.info("1. Review the analysis above")
    logger.info("2. Check quality scores and recommendations")
    logger.info("3. Decide on training approach:")
    logger.info("   - FastText embeddings")
    logger.info("   - Job role classifier")
    logger.info("   - Combined approach")
    logger.info("4. Let me know which direction you'd like to take!")


if __name__ == '__main__':
    main()
