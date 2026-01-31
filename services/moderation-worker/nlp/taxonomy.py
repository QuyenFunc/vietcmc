"""
Vietnamese Content Moderation Taxonomy
Multi-label classification with severity levels (0-2)
"""

from typing import List, Dict
from enum import Enum


class ModerationLabel(str, Enum):
    """Multi-label taxonomy for content moderation"""
    
    # Core toxicity categories
    TOXICITY = "toxicity"  # Profanity, general insults
    HATE = "hate"  # Hate speech targeting groups (race, religion, gender, etc.)
    HARASSMENT = "harassment"  # Personal harassment, bullying
    THREAT = "threat"  # Violent threats, self-harm
    SEXUAL = "sexual"  # Pornography, 18+, NSFW
    
    # Spam & fraud
    SPAM = "spam"  # Ads, fraud, scam
    
    # Privacy & data
    PII = "pii"  # Personal Identifiable Information (Phone, email, address)
    
    # Domain-specific (optional)
    BRAND_POLICY = "brand_policy"  # Brand policy violations
    MISINFORMATION = "misinformation"  # Misinformation (optional - best handled in separate pipeline)


class SeverityLevel(int, Enum):
    """Severity levels for moderation actions"""
    CLEAN = 0  # Clean, allow
    MODERATE = 1  # Moderate - hide or queue for review
    SEVERE = 2  # Severe - reject immediately


# Mapping from severity to actions
SEVERITY_ACTIONS = {
    SeverityLevel.CLEAN: "allowed",
    SeverityLevel.MODERATE: "review",
    SeverityLevel.SEVERE: "reject"
}


# Label descriptions for training data annotation
LABEL_DESCRIPTIONS = {
    ModerationLabel.TOXICITY: {
        "vi": "Profanity, offensive language, general insults",
        "en": "Profanity, offensive language, general insults",
        "examples": ["đồ ngu", "mẹ kiếp", "đ*o", "vl", "đ.m"],
        "severity": {
            0: "No profanity",
            1: "Mild profanity (đ.m, vl...)",
            2: "Severe profanity, repeated"
        }
    },
    ModerationLabel.HATE: {
        "vi": "Hate speech targeting groups based on race, religion, gender, sexual orientation",
        "en": "Hate speech targeting groups based on race, religion, gender, sexual orientation",
        "examples": ["khỉ đen", "đồ đạo chó", "đồ đồng tính biến thái"],
        "severity": {
            0: "No hate speech",
            1: "Mild bias, negative group evaluation",
            2: "Clear hate speech, inciting violence"
        }
    },
    ModerationLabel.HARASSMENT: {
        "vi": "Harassment, bullying targeting specific individuals",
        "en": "Harassment, bullying targeting specific individuals",
        "examples": ["mày xấu vãi", "@user này ngu vl", "lũ bạn mày toàn rác"],
        "severity": {
            0: "No harassment",
            1: "Mocking, teasing",
            2: "Severe harassment, threats"
        }
    },
    ModerationLabel.THREAT: {
        "vi": "Threats of violence, self-harm, danger",
        "en": "Threats of violence, self-harm, danger",
        "examples": ["tao sẽ giết mày", "đập chết", "tự tử đi"],
        "severity": {
            0: "No threats",
            1: "Vague threats",
            2: "Clear, dangerous threats"
        }
    },
    ModerationLabel.SEXUAL: {
        "vi": "Sexual content, pornography, NSFW",
        "en": "Sexual content, pornography, NSFW",
        "examples": ["địt", "chịch", "lồn", "cặc", "link sex"],
        "severity": {
            0: "No sexual content",
            1: "Mildly suggestive",
            2: "Explicit pornography"
        }
    },
    ModerationLabel.SPAM: {
        "vi": "Spam, ads, scams, fraud",
        "en": "Spam, ads, scams, fraud",
        "examples": ["inbox mua hàng", "kiếm tiền online", "cần người làm part-time"],
        "severity": {
            0: "No spam",
            1: "Mild advertising, self-promotion",
            2: "Clear spam, fraud"
        }
    },
    ModerationLabel.PII: {
        "vi": "Personal Identifiable Information (phone, email, address, ID)",
        "en": "Personal Identifiable Information (phone, email, address, ID)",
        "examples": ["0123456789", "user@gmail.com", "123 Lê Lợi Q1"],
        "severity": {
            0: "No PII",
            1: "Non-sensitive PII (public email)",
            2: "Sensitive PII (Phone, ID, address)"
        }
    },
    ModerationLabel.BRAND_POLICY: {
        "vi": "Brand policy violations (competitor keywords, banned content)",
        "en": "Brand policy violations (competitor keywords, banned content)",
        "examples": ["shopee rẻ hơn", "lazada tốt hơn"],
        "severity": {
            0: "No violation",
            1: "Mentioning competitors",
            2: "Explicit competitor advertising"
        }
    },
    ModerationLabel.MISINFORMATION: {
        "vi": "Misinformation, fake news (RECOMMENDED: separate pipeline)",
        "en": "Misinformation, fake news (RECOMMENDED: separate pipeline)",
        "examples": ["covid không tồn tại", "vắc xin gây tự kỷ"],
        "severity": {
            0: "Accurate information",
            1: "Unverified information",
            2: "Clear misinformation"
        },
        "note": "Very difficult, recommend separate fact-checking pipeline"
    }
}


# Default labels to use (excluding optional ones)
DEFAULT_LABELS = [
    ModerationLabel.TOXICITY,
    ModerationLabel.HATE,
    ModerationLabel.HARASSMENT,
    ModerationLabel.THREAT,
    ModerationLabel.SEXUAL,
    ModerationLabel.SPAM,
    ModerationLabel.PII
]


# Extended labels (include all)
ALL_LABELS = list(ModerationLabel)


def get_label_list(include_optional: bool = False) -> List[str]:
    """Get list of label names"""
    if include_optional:
        return [label.value for label in ALL_LABELS]
    return [label.value for label in DEFAULT_LABELS]


def get_num_labels(include_optional: bool = False) -> int:
    """Get number of labels"""
    return len(get_label_list(include_optional))


def severity_to_action(severity: int) -> str:
    """Map severity level to moderation action"""
    if severity == 0:
        return "allowed"
    elif severity == 1:
        return "review"
    else:
        return "reject"


def combine_predictions(labels: List[str], severities: List[int]) -> Dict:
    """
    Combine multi-label predictions with severities to final decision
    
    Args:
        labels: List of detected labels
        severities: List of severity scores (0-2) for each label
        
    Returns:
        Dict with final action and reasoning
    """
    if not labels:
        return {
            "action": "allowed",
            "severity": 0,
            "triggered_labels": [],
            "reasoning": "Clean content, no violation"
        }
    
    # Get max severity
    max_severity = max(severities)
    
    # Get labels with max severity
    critical_labels = [
        labels[i] for i, s in enumerate(severities) if s == max_severity
    ]
    
    # Map to action
    action = severity_to_action(max_severity)
    
    # Generate reasoning
    label_names = ", ".join(critical_labels)
    reasoning = f"Violation detected: {label_names} (level {max_severity})"
    
    return {
        "action": action,
        "severity": max_severity,
        "triggered_labels": critical_labels,
        "all_labels": dict(zip(labels, severities)),
        "reasoning": reasoning
    }


# Dataset source mapping
DATASET_SOURCES = {
    "UIT-ViCTSD": {
        "url": "https://github.com/sonlam1102/viet-text-normalize",
        "paper": "https://arxiv.org/abs/2103.10069",
        "labels": ["CONSTRUCTIVE", "TOXIC"],
        "size": "~10k comments",
        "mapping": {
            "TOXIC": [ModerationLabel.TOXICITY]
        }
    },
    "ViHSD": {
        "url": "https://github.com/ongocthanhvan/ViHSD",
        "paper": "https://arxiv.org/abs/2210.15634",
        "labels": ["CLEAN", "OFFENSIVE", "HATE"],
        "size": "~33k comments",
        "mapping": {
            "OFFENSIVE": [ModerationLabel.TOXICITY],
            "HATE": [ModerationLabel.HATE]
        }
    },
    "ViHOS": {
        "url": "https://github.com/tarudesu/ViHOS",
        "paper": "https://aclanthology.org/2023.findings-emnlp.210/",
        "labels": ["span-level hate speech"],
        "size": "~11k comments",
        "mapping": {
            "HATE_SPAN": [ModerationLabel.HATE, ModerationLabel.TOXICITY]
        },
        "note": "Token-level annotations for span detection"
    },
    "UIT-VSMEC": {
        "url": "https://github.com/uitnlp/vietnamese-student-feedback",
        "paper": "https://arxiv.org/abs/2104.08569",
        "labels": ["emotion: joy, sadness, anger, fear, surprise, love, other"],
        "size": "~6k sentences",
        "usage": "Auxiliary task for sentiment understanding"
    },
    "UIT-VSFC": {
        "url": "https://github.com/uitnlp/vietnamese-sentiment",
        "paper": "https://arxiv.org/abs/2104.05138",
        "labels": ["negative, neutral, positive"],
        "size": "~16k sentences",
        "usage": "Auxiliary task for sentiment classification"
    }
}


if __name__ == "__main__":
    # Print taxonomy info
    print("=" * 80)
    print("VIETNAMESE CONTENT MODERATION TAXONOMY")
    print("=" * 80)
    print(f"\nTotal labels: {get_num_labels(include_optional=True)}")
    print(f"Core labels: {get_num_labels(include_optional=False)}")
    print(f"\nLabels (multi-label, not mutually exclusive):\n")
    
    for label in ALL_LABELS:
        info = LABEL_DESCRIPTIONS[label]
        print(f"{label.value.upper()}")
        print(f"  VI: {info['vi']}")
        print(f"  Examples: {', '.join(info['examples'][:3])}")
        print(f"  Severity levels:")
        for sev, desc in info['severity'].items():
            print(f"    {sev}: {desc}")
        if 'note' in info:
            print(f"  Note: {info['note']}")
        print()

