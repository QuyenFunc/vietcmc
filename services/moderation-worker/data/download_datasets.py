"""
Dataset Download Helper for Vietnamese Moderation Datasets

This script provides instructions and helper functions for downloading
the Vietnamese datasets used in this project.

Datasets:
1. ViHSD - Vietnamese Hate Speech Detection (~33k)
2. ViHOS - Vietnamese Hate and Offensive Spans (~11k) 
3. UIT-ViCTSD - Vietnamese Constructive/Toxic Speech (~10k)
4. UIT-VSMEC - Vietnamese Emotion Corpus (~6k)
5. UIT-VSFC - Vietnamese Sentiment Corpus (~16k)
"""

import os
import sys
import requests
import zipfile
import logging
from pathlib import Path
from typing import Optional
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatasetDownloader:
    """Helper for downloading Vietnamese moderation datasets"""
    
    def __init__(self, data_dir: str = "./datasets"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def download_vihsd(self):
        """
        Download ViHSD dataset
        
        Source: https://github.com/ongocthanhvan/ViHSD
        Paper: https://arxiv.org/abs/2210.15634
        License: MIT
        """
        logger.info("="*80)
        logger.info("DOWNLOADING ViHSD - Vietnamese Hate Speech Detection")
        logger.info("="*80)
        
        dataset_dir = self.data_dir / "ViHSD"
        
        if dataset_dir.exists():
            logger.info(f"ViHSD already exists at {dataset_dir}")
            return
        
        logger.info("\nVi HSD Dataset Information:")
        logger.info("  - ~33,000 comments")
        logger.info("  - Labels: CLEAN, OFFENSIVE, HATE")
        logger.info("  - Source: Facebook comments")
        logger.info("  - License: MIT")
        
        logger.info("\nTo download ViHSD:")
        logger.info("1. Visit: https://github.com/ongocthanhvan/ViHSD")
        logger.info("2. Clone or download the repository")
        logger.info("3. Copy the data files to: " + str(dataset_dir))
        
        try:
            logger.info("\nAttempting to clone from GitHub...")
            subprocess.run(
                ["git", "clone", "https://github.com/ongocthanhvan/ViHSD.git", str(dataset_dir)],
                check=True
            )
            logger.info("✅ ViHSD downloaded successfully!")
        except Exception as e:
            logger.warning(f"Auto-download failed: {e}")
            logger.info("Please download manually from the GitHub link above")
    
    def download_vihos(self):
        """
        Download ViHOS dataset
        
        Source: https://github.com/tarudesu/ViHOS
        Paper: https://aclanthology.org/2023.findings-emnlp.210/
        License: CC BY-NC-SA 4.0
        """
        logger.info("="*80)
        logger.info("DOWNLOADING ViHOS - Vietnamese Hate and Offensive Spans")
        logger.info("="*80)
        
        dataset_dir = self.data_dir / "ViHOS"
        
        if dataset_dir.exists():
            logger.info(f"ViHOS already exists at {dataset_dir}")
            return
        
        logger.info("\nViHOS Dataset Information:")
        logger.info("  - ~11,000 comments")
        logger.info("  - Token-level span annotations")
        logger.info("  - For highlighting specific hate/offensive words")
        logger.info("  - License: CC BY-NC-SA 4.0")
        
        logger.info("\nTo download ViHOS:")
        logger.info("1. Visit: https://github.com/tarudesu/ViHOS")
        logger.info("2. Clone or download the repository")
        logger.info("3. Copy the data files to: " + str(dataset_dir))
        
        try:
            logger.info("\nAttempting to clone from GitHub...")
            subprocess.run(
                ["git", "clone", "https://github.com/tarudesu/ViHOS.git", str(dataset_dir)],
                check=True
            )
            logger.info("✅ ViHOS downloaded successfully!")
        except Exception as e:
            logger.warning(f"Auto-download failed: {e}")
            logger.info("Please download manually from the GitHub link above")
    
    def download_uit_victsd(self):
        """
        Download UIT-ViCTSD dataset
        
        Source: https://github.com/sonlam1102/viet-text-normalize
        Paper: https://arxiv.org/abs/2103.10069
        License: Research use
        """
        logger.info("="*80)
        logger.info("DOWNLOADING UIT-ViCTSD - Vietnamese Constructive/Toxic Speech")
        logger.info("="*80)
        
        dataset_dir = self.data_dir / "UIT-ViCTSD"
        
        if dataset_dir.exists():
            logger.info(f"UIT-ViCTSD already exists at {dataset_dir}")
            return
        
        logger.info("\nUIT-ViCTSD Dataset Information:")
        logger.info("  - ~10,000 comments")
        logger.info("  - Labels: CONSTRUCTIVE, TOXIC")
        logger.info("  - Source: YouTube comments")
        logger.info("  - License: Research use only")
        
        logger.info("\nTo download UIT-ViCTSD:")
        logger.info("1. Visit: https://github.com/sonlam1102/viet-text-normalize")
        logger.info("2. Or contact: UIT NLP Lab (nlp@uit.edu.vn)")
        logger.info("3. Download the dataset")
        logger.info("4. Copy the data files to: " + str(dataset_dir))
        
        logger.info("\n⚠️  This dataset may require permission from authors")
    
    def download_uit_vsmec(self):
        """
        Download UIT-VSMEC dataset
        
        Source: https://github.com/uitnlp/vietnamese-student-feedback
        Paper: https://arxiv.org/abs/2104.08569
        License: MIT
        """
        logger.info("="*80)
        logger.info("DOWNLOADING UIT-VSMEC - Vietnamese Emotion Corpus")
        logger.info("="*80)
        
        dataset_dir = self.data_dir / "UIT-VSMEC"
        
        if dataset_dir.exists():
            logger.info(f"UIT-VSMEC already exists at {dataset_dir}")
            return
        
        logger.info("\nUIT-VSMEC Dataset Information:")
        logger.info("  - ~6,000 sentences")
        logger.info("  - Labels: joy, sadness, anger, fear, surprise, love, other")
        logger.info("  - Auxiliary task for emotion understanding")
        logger.info("  - License: MIT")
        
        logger.info("\nTo download UIT-VSMEC:")
        logger.info("1. Visit: https://github.com/uitnlp/vietnamese-student-feedback")
        logger.info("2. Clone or download the repository")
        logger.info("3. Copy the data files to: " + str(dataset_dir))
        
        try:
            logger.info("\nAttempting to clone from GitHub...")
            subprocess.run(
                ["git", "clone", "https://github.com/uitnlp/vietnamese-student-feedback.git", str(dataset_dir)],
                check=True
            )
            logger.info("✅ UIT-VSMEC downloaded successfully!")
        except Exception as e:
            logger.warning(f"Auto-download failed: {e}")
            logger.info("Please download manually from the GitHub link above")
    
    def download_uit_vsfc(self):
        """
        Download UIT-VSFC dataset
        
        Source: https://github.com/uitnlp/vietnamese-sentiment
        Paper: https://arxiv.org/abs/2104.05138
        License: MIT
        """
        logger.info("="*80)
        logger.info("DOWNLOADING UIT-VSFC - Vietnamese Sentiment Corpus")
        logger.info("="*80)
        
        dataset_dir = self.data_dir / "UIT-VSFC"
        
        if dataset_dir.exists():
            logger.info(f"UIT-VSFC already exists at {dataset_dir}")
            return
        
        logger.info("\nUIT-VSFC Dataset Information:")
        logger.info("  - ~16,000 sentences")
        logger.info("  - Labels: negative, neutral, positive")
        logger.info("  - Auxiliary task for sentiment classification")
        logger.info("  - License: MIT")
        
        logger.info("\nTo download UIT-VSFC:")
        logger.info("1. Visit: https://github.com/uitnlp/vietnamese-sentiment")
        logger.info("2. Clone or download the repository")
        logger.info("3. Copy the data files to: " + str(dataset_dir))
        
        try:
            logger.info("\nAttempting to clone from GitHub...")
            subprocess.run(
                ["git", "clone", "https://github.com/uitnlp/vietnamese-sentiment.git", str(dataset_dir)],
                check=True
            )
            logger.info("✅ UIT-VSFC downloaded successfully!")
        except Exception as e:
            logger.warning(f"Auto-download failed: {e}")
            logger.info("Please download manually from the GitHub link above")
    
    def download_all(self):
        """Download all datasets"""
        logger.info("\n\n")
        logger.info("╔" + "="*78 + "╗")
        logger.info("║" + " "*20 + "VIETNAMESE MODERATION DATASETS" + " "*28 + "║")
        logger.info("╚" + "="*78 + "╝")
        logger.info("\n")
        
        datasets = [
            ("ViHSD", self.download_vihsd),
            ("ViHOS", self.download_vihos),
            ("UIT-ViCTSD", self.download_uit_victsd),
            ("UIT-VSMEC", self.download_uit_vsmec),
            ("UIT-VSFC", self.download_uit_vsfc),
        ]
        
        for name, download_func in datasets:
            try:
                download_func()
                logger.info("")
            except Exception as e:
                logger.error(f"Error downloading {name}: {e}")
                logger.info("")
        
        logger.info("\n" + "="*80)
        logger.info("DOWNLOAD SUMMARY")
        logger.info("="*80)
        
        # Check what exists
        for name in ["ViHSD", "ViHOS", "UIT-ViCTSD", "UIT-VSMEC", "UIT-VSFC"]:
            dataset_dir = self.data_dir / name
            if dataset_dir.exists():
                logger.info(f"✅ {name}: Downloaded")
            else:
                logger.info(f"❌ {name}: Not found - please download manually")
        
        logger.info("\n" + "="*80)
        logger.info("NEXT STEPS")
        logger.info("="*80)
        logger.info("1. Ensure all datasets are in: " + str(self.data_dir))
        logger.info("2. Run dataset_loader.py to combine and preprocess")
        logger.info("3. Start training with trainer.py")
        logger.info("")


def print_citation_info():
    """Print citation information for all datasets"""
    logger.info("\n" + "="*80)
    logger.info("CITATION INFORMATION")
    logger.info("="*80)
    
    citations = {
        "ViHSD": """
@article{van2022vihsd,
  title={ViHSD: Vietnamese Hate Speech Detection Dataset},
  author={Van, Ong Ngoc Thanh and others},
  journal={arXiv preprint arXiv:2210.15634},
  year={2022}
}
        """,
        "ViHOS": """
@inproceedings{luu2023vihos,
  title={ViHOS: Hate Speech Detection in Vietnamese Social Media Text},
  author={Luu, Son T and others},
  booktitle={Findings of EMNLP},
  year={2023}
}
        """,
        "UIT-ViCTSD": """
@article{nguyen2021uit,
  title={UIT-ViCTSD: A Dataset for Vietnamese Constructive and Toxic Speech Detection},
  author={Nguyen, Son Lam and others},
  journal={arXiv preprint arXiv:2103.10069},
  year={2021}
}
        """,
        "UIT-VSMEC": """
@article{ho2021uit,
  title={UIT-VSMEC: A Vietnamese Students' Feedback Emotion Corpus},
  author={Ho, Van-Thuy and others},
  journal={arXiv preprint arXiv:2104.08569},
  year={2021}
}
        """,
        "UIT-VSFC": """
@article{van2021uit,
  title={UIT-VSFC: A Vietnamese Students' Feedback Corpus},
  author={Van, Kiet and others},
  journal={arXiv preprint arXiv:2104.05138},
  year={2021}
}
        """
    }
    
    for dataset_name, citation in citations.items():
        logger.info(f"\n{dataset_name}:")
        logger.info(citation.strip())


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Download Vietnamese moderation datasets"
    )
    parser.add_argument(
        '--data-dir',
        type=str,
        default='./datasets',
        help='Directory to download datasets to'
    )
    parser.add_argument(
        '--dataset',
        type=str,
        choices=['all', 'vihsd', 'vihos', 'victsd', 'vsmec', 'vsfc'],
        default='all',
        help='Which dataset to download'
    )
    parser.add_argument(
        '--citations',
        action='store_true',
        help='Print citation information'
    )
    
    args = parser.parse_args()
    
    if args.citations:
        print_citation_info()
        sys.exit(0)
    
    downloader = DatasetDownloader(args.data_dir)
    
    if args.dataset == 'all':
        downloader.download_all()
    elif args.dataset == 'vihsd':
        downloader.download_vihsd()
    elif args.dataset == 'vihos':
        downloader.download_vihos()
    elif args.dataset == 'victsd':
        downloader.download_uit_victsd()
    elif args.dataset == 'vsmec':
        downloader.download_uit_vsmec()
    elif args.dataset == 'vsfc':
        downloader.download_uit_vsfc()
    
    logger.info("\n✅ Done!")

