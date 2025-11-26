#!/usr/bin/env python3
"""
Explore the multi-industry Kaggle resume dataset

Dataset: noorsaeed/resume-datasets
This should cover multiple industries beyond just IT

Quick Start:
1. pip install kagglehub pandas numpy
2. python explore_multi_industry_dataset.py
"""

import os
import sys
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
    """Download the multi-industry resume dataset"""
    logger.info("📥 Downloading multi-industry resume dataset...")
    logger.info("   Dataset: noorsaeed/resume-datasets")

    try:
        import kagglehub
    except ImportError:
        logger.error("❌ kagglehub not installed. Install with: pip install kagglehub")
        return None

    try:
        path = kagglehub.dataset_download("noorsaeed/resume-datasets")
        logger.info(f"✅ Dataset downloaded to: {path}")
        return path
    except Exception as e:
        logger.error(f"❌ Failed to download dataset: {str(e)}")
        return None


def explore_dataset(dataset_path):
    """Thoroughly explore the dataset structure and content"""
    logger.info("\n📊 ANALYZING MULTI-INDUSTRY DATASET")
    logger.info("=" * 70)

    path = Path(dataset_path)

    # Count files by type
    files_by_ext = defaultdict(list)
    all_files = []

    for item in path.rglob('*'):
        if item.is_file():
            ext = item.suffix if item.suffix else 'no_extension'
            files_by_ext[ext].append(item)
            all_files.append(item)

    # Summary statistics
    total_files = len(all_files)
    logger.info(f"\n📈 Total files: {total_files}")

    logger.info(f"\n📋 Files by type:")
    for ext, files in sorted(files_by_ext.items(), key=lambda x: len(x[1]), reverse=True):
        logger.info(f"  {ext:15s}: {len(files):6d} files")

    # Analyze different file types
    csv_files = files_by_ext.get('.csv', [])
    json_files = files_by_ext.get('.json', [])
    txt_files = files_by_ext.get('.txt', [])
    pdf_files = files_by_ext.get('.pdf', [])

    logger.info(f"\n🔍 Detailed Analysis:")
    logger.info(f"   CSV files:  {len(csv_files)}")
    logger.info(f"   JSON files: {len(json_files)}")
    logger.info(f"   TXT files:  {len(txt_files)}")
    logger.info(f"   PDF files:  {len(pdf_files)}")

    # Analyze CSV files (likely to have structured data)
    if csv_files:
        logger.info(f"\n📊 CSV Files Analysis:")
        analyze_csv_files(csv_files[:5])  # Analyze first 5

    # Analyze JSON files
    if json_files:
        logger.info(f"\n📄 JSON Files Analysis:")
        analyze_json_files(json_files[:3])  # Analyze first 3

    # Sample text/resume files
    if txt_files:
        logger.info(f"\n📝 Text Files Sample:")
        sample_text_files(txt_files[:3])

    # Calculate total size
    total_size = sum(f.stat().st_size for f in all_files)
    total_size_gb = total_size / (1024 ** 3)
    logger.info(f"\n💾 Total dataset size: {total_size_gb:.2f} GB")

    # Extract job categories/titles
    logger.info(f"\n💼 Job Categories/Industries:")
    analyze_job_categories(csv_files, json_files, txt_files)

    return {
        'total_files': total_files,
        'csv_count': len(csv_files),
        'json_count': len(json_files),
        'txt_count': len(txt_files),
        'pdf_count': len(pdf_files),
        'total_size_gb': total_size_gb,
        'files_by_ext': dict((k, len(v)) for k, v in files_by_ext.items())
    }


def analyze_csv_files(csv_files):
    """Analyze CSV files for structure and content"""
    try:
        import pandas as pd
    except ImportError:
        logger.warning("⚠️  pandas not installed, skipping CSV analysis")
        return

    for file_path in csv_files[:3]:
        try:
            logger.info(f"\n  📋 {file_path.name}")

            # Read with sample
            df = pd.read_csv(file_path, nrows=5)

            logger.info(f"     Shape: {df.shape[0]}+ rows, {df.shape[1]} columns")
            logger.info(f"     Columns: {list(df.columns)[:10]}")

            # Check for job/category columns
            col_lower = [c.lower() for c in df.columns]
            if any('job' in c or 'title' in c or 'category' in c for c in col_lower):
                logger.info(f"     ✅ Has job/category information!")

                # Try to extract unique jobs
                for col in df.columns:
                    if 'job' in col.lower() or 'title' in col.lower() or 'category' in col.lower():
                        try:
                            unique_jobs = df[col].unique()[:10]
                            logger.info(f"     Sample {col}: {unique_jobs}")
                        except:
                            pass

            # Show first row preview
            logger.info(f"     First row preview:")
            for col in df.columns[:5]:
                val = str(df[col].iloc[0])[:60].replace('\n', ' ')
                logger.info(f"       {col}: {val}")

        except Exception as e:
            logger.error(f"     Error analyzing: {str(e)}")


def analyze_json_files(json_files):
    """Analyze JSON files for structure"""
    for file_path in json_files[:3]:
        try:
            logger.info(f"\n  📄 {file_path.name}")

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                try:
                    data = json.load(f)
                except:
                    logger.info(f"     ⚠️  Invalid JSON format")
                    continue

            if isinstance(data, list):
                logger.info(f"     Array with {len(data)} items")
                if data and isinstance(data[0], dict):
                    logger.info(f"     Keys in first item: {list(data[0].keys())[:10]}")

            elif isinstance(data, dict):
                logger.info(f"     Dictionary with keys: {list(data.keys())[:10]}")
                for k, v in list(data.items())[:3]:
                    if isinstance(v, str):
                        preview = v[:60].replace('\n', ' ')
                        logger.info(f"       {k}: {preview}")
                    elif isinstance(v, (list, dict)):
                        logger.info(f"       {k}: {type(v).__name__} ({len(v)} items)")

        except Exception as e:
            logger.error(f"     Error: {str(e)}")


def sample_text_files(txt_files):
    """Sample text/resume files"""
    import random
    samples = random.sample(txt_files, min(3, len(txt_files)))

    for i, file_path in enumerate(samples, 1):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            logger.info(f"\n  📝 Sample {i}: {file_path.name}")
            logger.info(f"     Size: {len(content)} bytes")

            # Show preview
            preview = content[:250].replace('\n', ' ')
            logger.info(f"     Preview: {preview}...")

            # Try to detect job/industry from content
            content_lower = content.lower()
            if any(word in content_lower for word in ['python', 'java', 'code', 'developer']):
                logger.info(f"     🔹 Likely IT/Developer role")
            elif any(word in content_lower for word in ['sales', 'client', 'revenue', 'quota']):
                logger.info(f"     🔹 Likely Sales role")
            elif any(word in content_lower for word in ['design', 'ui', 'ux', 'photoshop']):
                logger.info(f"     🔹 Likely Design role")
            elif any(word in content_lower for word in ['manage', 'leadership', 'team', 'budget']):
                logger.info(f"     🔹 Likely Management role")
            elif any(word in content_lower for word in ['teach', 'education', 'student', 'class']):
                logger.info(f"     🔹 Likely Education role")
            elif any(word in content_lower for word in ['nurse', 'medical', 'patient', 'health']):
                logger.info(f"     🔹 Likely Healthcare role")

        except Exception as e:
            logger.error(f"     Error: {str(e)}")


def analyze_job_categories(csv_files, json_files, txt_files):
    """Try to extract job categories/industries from the data"""
    try:
        import pandas as pd
    except:
        return

    categories_found = Counter()
    industries_found = Counter()

    # Check CSV files for job categories
    for csv_file in csv_files[:5]:
        try:
            df = pd.read_csv(csv_file, nrows=100)

            # Look for job/category columns
            for col in df.columns:
                col_lower = col.lower()
                if 'job' in col_lower or 'title' in col_lower or 'category' in col_lower:
                    for val in df[col].dropna().unique()[:20]:
                        job_str = str(val).strip()
                        if len(job_str) > 2:
                            categories_found[job_str] += 1

                elif 'industry' in col_lower or 'field' in col_lower:
                    for val in df[col].dropna().unique()[:20]:
                        ind_str = str(val).strip()
                        if len(ind_str) > 2:
                            industries_found[ind_str] += 1
        except:
            pass

    if categories_found:
        logger.info(f"\n  Found job categories:")
        for job, count in categories_found.most_common(15):
            logger.info(f"    - {job}")

    if industries_found:
        logger.info(f"\n  Found industries:")
        for industry, count in industries_found.most_common(15):
            logger.info(f"    - {industry}")


def generate_report(stats):
    """Generate comprehensive report"""
    logger.info("\n" + "=" * 70)
    logger.info("📊 MULTI-INDUSTRY DATASET ASSESSMENT")
    logger.info("=" * 70)

    # Calculate score
    score = 0

    # Size and volume
    if stats['total_files'] > 1000:
        score += 30
        logger.info(f"\n✅ Excellent file count: {stats['total_files']:,} files")
    elif stats['total_files'] > 500:
        score += 20
        logger.info(f"\n✅ Good file count: {stats['total_files']:,} files")
    else:
        score += 10
        logger.info(f"\n⚠️  Moderate file count: {stats['total_files']:,} files")

    # Structured data (CSV/JSON better than PDF/TXT)
    structured = stats['csv_count'] + stats['json_count']
    if structured > 100:
        score += 30
        logger.info(f"✅ Excellent structured data: {structured} CSV/JSON files")
    elif structured > 10:
        score += 20
        logger.info(f"✅ Good structured data: {structured} CSV/JSON files")
    elif structured > 0:
        score += 15
        logger.info(f"⚠️  Some structured data: {structured} CSV/JSON files")
    else:
        score += 5
        logger.info(f"⚠️  Limited structured data (mostly unstructured)")

    # Dataset size
    if stats['total_size_gb'] > 2:
        score += 40
        logger.info(f"✅ Excellent dataset size: {stats['total_size_gb']:.2f} GB")
    elif stats['total_size_gb'] > 1:
        score += 30
        logger.info(f"✅ Good dataset size: {stats['total_size_gb']:.2f} GB")
    elif stats['total_size_gb'] > 0.5:
        score += 20
        logger.info(f"⚠️  Moderate size: {stats['total_size_gb']:.2f} GB")
    else:
        score += 10
        logger.info(f"⚠️  Small dataset: {stats['total_size_gb']:.2f} GB")

    logger.info(f"\n{'OVERALL SCORE':<30}: {score}/100")

    # Recommendations
    logger.info(f"\n💡 RECOMMENDATION:")
    if score >= 80:
        logger.info("   ✅ EXCELLENT - Suitable for comprehensive multi-industry keyword extraction")
        logger.info("   This dataset can support:")
        logger.info("   - Keywords across all industries")
        logger.info("   - Job category classification")
        logger.info("   - Industry-specific skill mapping")
        logger.info("   - Comprehensive resume analysis system")

    elif score >= 60:
        logger.info("   ✅ GOOD - Useful for multi-industry keyword expansion")
        logger.info("   Can extract keywords from various fields")
        logger.info("   May need some data preprocessing")

    elif score >= 40:
        logger.info("   ⚠️  MODERATE - Limited usefulness for comprehensive system")
        logger.info("   May need to supplement with other data sources")

    else:
        logger.info("   ❌ LIMITED - Not suitable as primary source")

    return score


def main():
    """Main exploration"""
    logger.info("🚀 MULTI-INDUSTRY RESUME DATASET EXPLORATION")
    logger.info("=" * 70)
    logger.info("Dataset: noorsaeed/resume-datasets")
    logger.info("=" * 70)

    # Check dependencies
    try:
        import kagglehub
        import pandas
        import numpy
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        logger.error("   Install with: pip install kagglehub pandas numpy")
        sys.exit(1)

    # Download
    dataset_path = download_dataset()
    if not dataset_path:
        sys.exit(1)

    # Analyze
    stats = explore_dataset(dataset_path)

    # Generate report
    score = generate_report(stats)

    # Final message
    logger.info("\n" + "=" * 70)
    logger.info("✅ EXPLORATION COMPLETE!")
    logger.info("=" * 70)
    logger.info(f"\nScore: {score}/100")
    logger.info("\n📋 Next Steps:")
    logger.info("1. Review analysis above")
    logger.info("2. This covers multiple industries (not just IT)")
    logger.info("3. If score is good, we can extract keywords across all fields")
    logger.info("4. Share results and we'll decide on implementation")


if __name__ == '__main__':
    main()
