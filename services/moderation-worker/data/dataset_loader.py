"""
Dataset loader for Vietnamese moderation datasets
Supports: UIT-ViCTSD, ViHSD, ViHOS, UIT-VSMEC, UIT-VSFC
"""

import os
import json
import pandas as pd
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import logging

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nlp.taxonomy import ModerationLabel, SeverityLevel, DATASET_SOURCES

logger = logging.getLogger(__name__)


class DatasetLoader:
    """Load and process Vietnamese moderation datasets"""
    
    def __init__(self, data_dir: str = "./datasets"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def load_vihsd(self) -> pd.DataFrame:
        """
        Load ViHSD dataset (Vietnamese Hate Speech Detection)
        
        Expected format: CSV with columns [text, label]
        Labels: CLEAN, OFFENSIVE, HATE
        
        Returns:
            DataFrame with columns [text, toxicity, hate, severity]
        """
        vihsd_path = self.data_dir / "ViHSD"
        
        if not vihsd_path.exists():
            logger.warning(f"ViHSD dataset not found at {vihsd_path}")
            logger.info("Download from: https://github.com/ongocthanhvan/ViHSD")
            return pd.DataFrame()
        
        # Load train/dev/test files
        dfs = []
        for split in ['train', 'dev', 'test']:
            file_path = vihsd_path / f"{split}.csv"
            if file_path.exists():
                df = pd.read_csv(file_path)
                df['split'] = split
                dfs.append(df)
        
        if not dfs:
            logger.error("No ViHSD files found")
            return pd.DataFrame()
        
        # Combine all splits
        data = pd.concat(dfs, ignore_index=True)
        
        # Map labels to taxonomy
        data['toxicity'] = (data['label'].isin(['OFFENSIVE', 'HATE'])).astype(int)
        data['hate'] = (data['label'] == 'HATE').astype(int)
        data['harassment'] = 0  # Not annotated in ViHSD
        data['threat'] = 0
        data['sexual'] = 0
        data['spam'] = 0
        data['pii'] = 0
        
        # Map severity
        severity_map = {
            'CLEAN': SeverityLevel.CLEAN,
            'OFFENSIVE': SeverityLevel.MODERATE,
            'HATE': SeverityLevel.SEVERE
        }
        data['severity'] = data['label'].map(severity_map).astype(int)
        
        logger.info(f"Loaded ViHSD: {len(data)} samples")
        logger.info(f"  CLEAN: {(data['label'] == 'CLEAN').sum()}")
        logger.info(f"  OFFENSIVE: {(data['label'] == 'OFFENSIVE').sum()}")
        logger.info(f"  HATE: {(data['label'] == 'HATE').sum()}")
        
        return data
    
    def load_vihos(self) -> pd.DataFrame:
        """
        Load ViHOS dataset (Vietnamese Hate and Offensive Spans)
        
        Token-level annotations for span detection
        
        Expected format: JSON with span annotations
        
        Returns:
            DataFrame with columns [text, hate, toxicity, severity, spans]
        """
        vihos_path = self.data_dir / "ViHOS"
        
        if not vihos_path.exists():
            logger.warning(f"ViHOS dataset not found at {vihos_path}")
            logger.info("Download from: https://github.com/tarudesu/ViHOS")
            return pd.DataFrame()
        
        # Load JSON files
        data_list = []
        for split in ['train', 'dev', 'test']:
            file_path = vihos_path / f"{split}.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    split_data = json.load(f)
                    for item in split_data:
                        item['split'] = split
                        data_list.append(item)
        
        if not data_list:
            logger.error("No ViHOS files found")
            return pd.DataFrame()
        
        data = pd.DataFrame(data_list)
        
        # ViHOS has span-level annotations
        # Extract text and labels
        data['hate'] = 1  # All ViHOS samples contain hate/offensive content
        data['toxicity'] = 1
        data['harassment'] = 0
        data['threat'] = 0
        data['sexual'] = 0
        data['spam'] = 0
        data['pii'] = 0
        data['severity'] = SeverityLevel.SEVERE  # Hate speech is severe
        
        logger.info(f"Loaded ViHOS: {len(data)} samples (all contain hate/offensive content)")
        
        return data
    
    def load_uit_victsd(self) -> pd.DataFrame:
        """
        Load UIT-ViCTSD dataset (Vietnamese Constructive and Toxic Speech Detection)
        
        Expected format: CSV with columns [text, label]
        Labels: CONSTRUCTIVE, TOXIC
        
        Returns:
            DataFrame with columns [text, toxicity, severity]
        """
        victsd_path = self.data_dir / "UIT-ViCTSD"
        
        if not victsd_path.exists():
            logger.warning(f"UIT-ViCTSD dataset not found at {victsd_path}")
            logger.info("Contact authors or check: https://github.com/sonlam1102/viet-text-normalize")
            return pd.DataFrame()
        
        # Load files
        dfs = []
        for file in victsd_path.glob("*.csv"):  
            df = pd.read_csv(file)
            dfs.append(df)
        
        if not dfs:
            logger.error("No UIT-ViCTSD files found")
            return pd.DataFrame()
        
        data = pd.concat(dfs, ignore_index=True)
        
        # Map labels
        data['toxicity'] = (data['label'] == 'TOXIC').astype(int)
        data['hate'] = 0  # Not specifically annotated
        data['harassment'] = 0
        data['threat'] = 0
        data['sexual'] = 0
        data['spam'] = 0
        data['pii'] = 0
        
        # Map severity
        data['severity'] = data['toxicity'].apply(
            lambda x: SeverityLevel.MODERATE if x else SeverityLevel.CLEAN
        ).astype(int)
        
        logger.info(f"Loaded UIT-ViCTSD: {len(data)} samples")
        logger.info(f"  CONSTRUCTIVE: {(data['label'] == 'CONSTRUCTIVE').sum()}")
        logger.info(f"  TOXIC: {(data['label'] == 'TOXIC').sum()}")
        
        return data
    
    def load_uit_vsmec(self) -> pd.DataFrame:
        """
        Load UIT-VSMEC dataset (Vietnamese Students' Feedback Emotion Corpus)
        
        Auxiliary task for emotion understanding
        
        Labels: joy, sadness, anger, fear, surprise, love, other
        
        Returns:
            DataFrame with columns [text, emotion]
        """
        vsmec_path = self.data_dir / "UIT-VSMEC"
        
        if not vsmec_path.exists():
            logger.warning(f"UIT-VSMEC dataset not found at {vsmec_path}")
            logger.info("Download from: https://github.com/uitnlp/vietnamese-student-feedback")
            return pd.DataFrame()
        
        dfs = []
        for split in ['train', 'dev', 'test']:
            file_path = vsmec_path / f"{split}.csv"
            if file_path.exists():
                df = pd.read_csv(file_path)
                df['split'] = split
                dfs.append(df)
        
        if not dfs:
            return pd.DataFrame()
        
        data = pd.concat(dfs, ignore_index=True)
        
        # Map emotions to moderation hints
        # anger -> potential toxicity
        data['toxicity'] = (data['emotion'] == 'anger').astype(int)
        data['hate'] = 0
        data['harassment'] = 0
        data['threat'] = 0
        data['sexual'] = 0
        data['spam'] = 0
        data['pii'] = 0
        data['severity'] = SeverityLevel.CLEAN  # Emotion data is not toxic by default
        
        logger.info(f"Loaded UIT-VSMEC: {len(data)} samples (emotion corpus)")
        
        return data
    
    def load_uit_vsfc(self) -> pd.DataFrame:
        """
        Load UIT-VSFC dataset (Vietnamese Students' Feedback Corpus)
        
        Auxiliary task for sentiment classification
        
        Labels: negative, neutral, positive
        
        Returns:
            DataFrame with columns [text, sentiment]
        """
        vsfc_path = self.data_dir / "UIT-VSFC"
        
        if not vsfc_path.exists():
            logger.warning(f"UIT-VSFC dataset not found at {vsfc_path}")
            logger.info("Download from: https://github.com/uitnlp/vietnamese-sentiment")
            return pd.DataFrame()
        
        dfs = []
        for split in ['train', 'dev', 'test']:
            file_path = vsfc_path / f"{split}.csv"
            if file_path.exists():
                df = pd.read_csv(file_path)
                df['split'] = split
                dfs.append(df)
        
        if not dfs:
            return pd.DataFrame()
        
        data = pd.concat(dfs, ignore_index=True)
        
        # Sentiment data - not directly moderation labels
        # But negative sentiment with high confidence might indicate toxicity
        data['toxicity'] = 0
        data['hate'] = 0
        data['harassment'] = 0
        data['threat'] = 0
        data['sexual'] = 0
        data['spam'] = 0
        data['pii'] = 0
        data['severity'] = SeverityLevel.CLEAN
        
        logger.info(f"Loaded UIT-VSFC: {len(data)} samples (sentiment corpus)")
        
        return data
    
    def combine_datasets(
        self,
        include_emotion: bool = False,
        include_sentiment: bool = False
    ) -> pd.DataFrame:
        """
        Combine all datasets into unified format
        
        Args:
            include_emotion: Include emotion corpus (UIT-VSMEC)
            include_sentiment: Include sentiment corpus (UIT-VSFC)
            
        Returns:
            Combined DataFrame with standardized columns
        """
        datasets = []
        
        # Core moderation datasets
        vihsd = self.load_vihsd()
        if not vihsd.empty:
            vihsd['source'] = 'ViHSD'
            datasets.append(vihsd)
        
        vihos = self.load_vihos()
        if not vihos.empty:
            vihos['source'] = 'ViHOS'
            datasets.append(vihos)
        
        victsd = self.load_uit_victsd()
        if not victsd.empty:
            victsd['source'] = 'UIT-ViCTSD'
            datasets.append(victsd)
        
        # Auxiliary datasets
        if include_emotion:
            vsmec = self.load_uit_vsmec()
            if not vsmec.empty:
                vsmec['source'] = 'UIT-VSMEC'
                datasets.append(vsmec)
        
        if include_sentiment:
            vsfc = self.load_uit_vsfc()
            if not vsfc.empty:
                vsfc['source'] = 'UIT-VSFC'
                datasets.append(vsfc)
        
        if not datasets:
            logger.error("No datasets loaded!")
            return pd.DataFrame()
        
        # Combine
        combined = pd.concat(datasets, ignore_index=True)
        
        # Ensure required columns exist
        required_cols = ['text', 'toxicity', 'hate', 'harassment', 'threat', 
                        'sexual', 'spam', 'pii', 'severity', 'source']
        
        for col in required_cols:
            if col not in combined.columns:
                combined[col] = 0
        
        # Remove duplicates
        combined = combined.drop_duplicates(subset=['text'], keep='first')
        
        logger.info(f"\n{'='*60}")
        logger.info(f"COMBINED DATASET STATISTICS")
        logger.info(f"{'='*60}")
        logger.info(f"Total samples: {len(combined)}")
        logger.info(f"\nBy source:")
        for source in combined['source'].unique():
            count = (combined['source'] == source).sum()
            logger.info(f"  {source}: {count}")
        
        logger.info(f"\nLabel distribution:")
        logger.info(f"  Toxicity: {combined['toxicity'].sum()}")
        logger.info(f"  Hate: {combined['hate'].sum()}")
        logger.info(f"  Harassment: {combined['harassment'].sum()}")
        logger.info(f"  Threat: {combined['threat'].sum()}")
        logger.info(f"  Sexual: {combined['sexual'].sum()}")
        logger.info(f"  Spam: {combined['spam'].sum()}")
        logger.info(f"  PII: {combined['pii'].sum()}")
        
        logger.info(f"\nSeverity distribution:")
        for sev in [0, 1, 2]:
            count = (combined['severity'] == sev).sum()
            logger.info(f"  Level {sev}: {count}")
        
        return combined
    
    def save_unified_dataset(self, output_path: str, **kwargs):
        """
        Save combined dataset to file
        
        Args:
            output_path: Path to save CSV
            **kwargs: Arguments for combine_datasets
        """
        combined = self.combine_datasets(**kwargs)
        
        if combined.empty:
            logger.error("No data to save")
            return
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        combined.to_csv(output_path, index=False, encoding='utf-8')
        logger.info(f"Saved combined dataset to {output_path}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    loader = DatasetLoader("./datasets")
    
    # Load and combine datasets
    combined = loader.combine_datasets(
        include_emotion=True,
        include_sentiment=True
    )
    
    # Save
    if not combined.empty:
        loader.save_unified_dataset(
            "./datasets/combined_moderation_dataset.csv",
            include_emotion=True,
            include_sentiment=True
        )

