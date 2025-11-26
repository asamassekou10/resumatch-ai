#!/usr/bin/env python3
"""
Local Kaggle Resume Dataset Exploration Script

This is a simplified version that can be run locally without Docker.
It will download the dataset and provide comprehensive analysis.

Quick Start:
1. pip install kagglehub pandas numpy
2. Set up Kaggle credentials (see EXPLORATION_GUIDE.md)
3. python explore_dataset_local.py
"""

import os
import sys
import json
import logging
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if required packages are installed"""
    logger.info("📦 Checking dependencies...")

    packages = {
        'kagglehub': 'kagglehub',
        'pandas': 'pandas',
        'numpy': 'numpy'
    }

    missing = []
    for name, package in packages.items():
        try:
            __import__(name)
            logger.info(f"✅ {name} installed")
        except ImportError:
            logger.error(f"❌ {name} not installed")
            missing.append(package)

    if missing:
        logger.error("\n⚠️  Missing packages! Install with:")
        logger.error(f"   pip install {' '.join(missing)}")
        return False

    return True


def check_kaggle_credentials():
    """Check if Kaggle credentials are configured"""
    logger.info("\n🔐 Checking Kaggle credentials...")

    # Check for credentials in standard location
    kaggle_dir = Path.home() / '.kaggle'
    kaggle_json = kaggle_dir / 'kaggle.json'

    if kaggle_json.exists():
        logger.info(f"✅ Found kaggle.json at {kaggle_json}")
        # Check permissions
        if os.stat(kaggle_json).st_mode & 0o077:
            logger.warning("⚠️  Warning: kaggle.json has loose permissions")
            logger.info(f"   Run: chmod 600 {kaggle_json}")
        return True
    else:
        logger.error(f"❌ kaggle.json not found at {kaggle_json}")
        logger.error("\n📋 How to set up Kaggle credentials:")
        logger.error("1. Go to https://www.kaggle.com/settings/account")
        logger.error("2. Click 'Create New API Token'")
        logger.error("3. Move downloaded kaggle.json to ~/.kaggle/")
        logger.error("4. Run: chmod 600 ~/.kaggle/kaggle.json")
        return False


def download_dataset():
    """Download Kaggle resume dataset"""
    logger.info("\n📥 Downloading Kaggle resume dataset...")
    logger.info("   (This may take 5-10 minutes on first run)")

    try:
        import kagglehub
        logger.info("   Downloading from: snehaanbhawal/resume-dataset")

        path = kagglehub.dataset_download("snehaanbhawal/resume-dataset")
        logger.info(f"✅ Dataset downloaded to: {path}")
        return path

    except Exception as e:
        logger.error(f"❌ Download failed: {str(e)}")
        logger.error("\n   Troubleshooting:")
        logger.error("   - Ensure Kaggle credentials are valid")
        logger.error("   - Check internet connection")
        logger.error("   - Try again later if rate limited")
        return None


def analyze_dataset(dataset_path):
    """Analyze the downloaded dataset"""
    logger.info("\n📊 ANALYZING DATASET")
    logger.info("=" * 60)

    path = Path(dataset_path)

    # Count files by type
    files_by_ext = defaultdict(list)
    for item in path.rglob('*'):
        if item.is_file():
            ext = item.suffix if item.suffix else 'no_extension'
            files_by_ext[ext].append(item)

    # Summary
    total_files = sum(len(files) for files in files_by_ext.values())
    logger.info(f"\nTotal files: {total_files}")
    logger.info(f"\nFiles by type:")
    for ext, files in sorted(files_by_ext.items(), key=lambda x: len(x[1]), reverse=True):
        logger.info(f"  {ext:15s}: {len(files):6d} files")

    # Analyze text files
    txt_files = files_by_ext.get('.txt', [])
    if txt_files:
        logger.info(f"\n📋 Sample Analysis ({min(3, len(txt_files))} text files):")
        import random
        samples = random.sample(txt_files, min(3, len(txt_files)))

        for i, file_path in enumerate(samples, 1):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                logger.info(f"\n  Sample {i}: {file_path.name}")
                logger.info(f"    Size: {len(content)} bytes")

                # Show preview
                preview = content[:200].replace('\n', ' ')
                logger.info(f"    Preview: {preview}...")

            except Exception as e:
                logger.error(f"    Error: {str(e)}")

    # JSON/CSV analysis
    json_files = files_by_ext.get('.json', [])
    csv_files = files_by_ext.get('.csv', [])

    if csv_files:
        logger.info(f"\n📋 CSV Files detected: {len(csv_files)}")
        logger.info("   (May contain structured resume data)")

    if json_files:
        logger.info(f"\n📋 JSON Files detected: {len(json_files)}")
        logger.info("   (May contain structured resume data)")

    # Size analysis
    total_size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
    total_size_gb = total_size / (1024 ** 3)
    logger.info(f"\n💾 Total dataset size: {total_size_gb:.2f} GB")

    return {
        'total_files': total_files,
        'files_by_ext': dict(files_by_ext),
        'txt_count': len(txt_files),
        'json_count': len(json_files),
        'csv_count': len(csv_files),
        'total_size_gb': total_size_gb
    }


def generate_recommendation(stats):
    """Generate recommendation based on analysis"""
    logger.info("\n" + "=" * 60)
    logger.info("💡 ANALYSIS SUMMARY & RECOMMENDATIONS")
    logger.info("=" * 60)

    txt_count = stats['txt_count']
    json_count = stats['json_count']
    csv_count = stats['csv_count']
    total_size = stats['total_size_gb']

    logger.info(f"\nDataset Statistics:")
    logger.info(f"  Total resumes: {txt_count}")
    logger.info(f"  JSON data: {json_count} files")
    logger.info(f"  CSV data: {csv_count} files")
    logger.info(f"  Total size: {total_size:.2f} GB")

    # Generate score
    score = 0

    # Volume score (max 40 points)
    if txt_count >= 2000:
        score += 40
        logger.info("\n✅ Excellent volume (2000+ resumes)")
    elif txt_count >= 1000:
        score += 30
        logger.info("\n✅ Good volume (1000+ resumes)")
    elif txt_count >= 500:
        score += 20
        logger.info("\n⚠️  Moderate volume (500+ resumes)")
    elif txt_count >= 100:
        score += 10
        logger.info("\n⚠️  Limited volume (100+ resumes)")
    else:
        logger.info("\n❌ Very limited volume (<100 resumes)")

    # Structure score (max 30 points)
    if json_count > 0 or csv_count > 0:
        score += 30
        logger.info("✅ Has structured data (JSON/CSV)")
    elif txt_count > 0:
        score += 15
        logger.info("⚠️  Only plain text (less structured)")
    else:
        logger.info("❌ No structured data")

    # Size score (max 30 points)
    if total_size >= 2:
        score += 30
        logger.info("✅ Large dataset (2+ GB)")
    elif total_size >= 1:
        score += 20
        logger.info("✅ Good dataset size (1+ GB)")
    elif total_size >= 0.5:
        score += 10
        logger.info("⚠️  Moderate size (0.5+ GB)")
    else:
        logger.info("⚠️  Small dataset (<0.5 GB)")

    # Final recommendation
    logger.info("\n" + "-" * 60)
    logger.info(f"OVERALL SCORE: {score}/100")
    logger.info("-" * 60)

    if score >= 80:
        recommendation = "EXCELLENT"
        logger.info(f"\n🎯 Recommendation: {recommendation}")
        logger.info("\n✅ Dataset is well-suited for ML training!")
        logger.info("\nSuggested approach:")
        logger.info("  1. FastText Embeddings (4-6 hours)")
        logger.info("     - Better keyword similarity detection")
        logger.info("     - Handles semantic relationships")
        logger.info("  2. Job Role Classifier (8-12 hours)")
        logger.info("     - Auto-detect target job role")
        logger.info("     - Context-aware keyword scoring")
        logger.info("  Timeline: 1-2 weeks for full implementation")

    elif score >= 60:
        recommendation = "GOOD"
        logger.info(f"\n🎯 Recommendation: {recommendation}")
        logger.info("\n✅ Dataset has potential with processing")
        logger.info("\nSuggested approach:")
        logger.info("  1. FastText Embeddings only (4-6 hours)")
        logger.info("     - Improves keyword similarity")
        logger.info("  2. Skip job role classifier")
        logger.info("     - Not enough labeled data")
        logger.info("  Timeline: 4-6 days")

    elif score >= 40:
        recommendation = "MODERATE"
        logger.info(f"\n🎯 Recommendation: {recommendation}")
        logger.info("\n⚠️  Dataset needs significant processing")
        logger.info("\nSuggested approach:")
        logger.info("  - Explore further before committing")
        logger.info("  - Consider effort vs. benefit")
        logger.info("  - May not be worth implementing ML")
        logger.info("  Alternative: Manual keyword expansion")

    else:
        recommendation = "SKIP"
        logger.info(f"\n🎯 Recommendation: {recommendation}")
        logger.info("\n❌ Dataset not suitable for ML training")
        logger.info("\nSuggested approach:")
        logger.info("  - Continue with keyword database")
        logger.info("  - Use manual curation")
        logger.info("  - Avoid expensive ML training")

    return {
        'score': score,
        'recommendation': recommendation,
        'stats': stats
    }


def save_results(results, dataset_path):
    """Save analysis results to file"""
    report_path = Path(dataset_path).parent / "DATASET_ANALYSIS.json"

    try:
        with open(report_path, 'w') as f:
            json.dump({
                'analysis_date': datetime.now().isoformat(),
                'dataset_path': dataset_path,
                'score': results['score'],
                'recommendation': results['recommendation'],
                'stats': results['stats']
            }, f, indent=2)

        logger.info(f"\n✅ Results saved to: {report_path}")
    except Exception as e:
        logger.error(f"⚠️  Could not save results: {str(e)}")


def main():
    """Main exploration workflow"""
    logger.info("🚀 KAGGLE RESUME DATASET EXPLORATION")
    logger.info("=" * 60)

    # Step 1: Check dependencies
    if not check_dependencies():
        logger.error("\n❌ Please install missing packages and try again")
        sys.exit(1)

    # Step 2: Check Kaggle credentials
    if not check_kaggle_credentials():
        logger.error("\n❌ Please set up Kaggle credentials and try again")
        sys.exit(1)

    # Step 3: Download dataset
    dataset_path = download_dataset()
    if not dataset_path:
        logger.error("\n❌ Failed to download dataset")
        sys.exit(1)

    # Step 4: Analyze dataset
    stats = analyze_dataset(dataset_path)

    # Step 5: Generate recommendation
    results = generate_recommendation(stats)

    # Step 6: Save results
    save_results(results, dataset_path)

    # Final message
    logger.info("\n" + "=" * 60)
    logger.info("✅ EXPLORATION COMPLETE!")
    logger.info("=" * 60)
    logger.info("\n📋 Next Steps:")
    logger.info(f"1. Review the analysis above (Score: {results['score']}/100)")
    logger.info(f"2. Recommendation: {results['recommendation']}")
    logger.info("3. Share the results with me")
    logger.info("4. We'll decide on implementation approach together")
    logger.info("\n" + "=" * 60)


if __name__ == '__main__':
    main()
