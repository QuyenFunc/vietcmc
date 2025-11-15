"""
Vietnamese Content Moderation Taxonomy
Multi-label classification with severity levels (0-2)
"""

from typing import List, Dict
from enum import Enum


class ModerationLabel(str, Enum):
    """Multi-label taxonomy for content moderation"""
    
    # Core toxicity categories
    TOXICITY = "toxicity"  # Thô tục, xúc phạm chung
    HATE = "hate"  # Ghét, nhắm tới nhóm/thuộc tính (sắc tộc, tôn giáo, giới tính...)
    HARASSMENT = "harassment"  # Quấy rối cá nhân cụ thể, bắt nạt
    THREAT = "threat"  # Đe dọa bạo lực, tự hại
    SEXUAL = "sexual"  # Khiêu dâm, 18+, NSFW
    
    # Spam & fraud
    SPAM = "spam"  # Quảng cáo, lừa đảo, scam
    
    # Privacy & data
    PII = "pii"  # Personal Identifiable Information (SĐT, email, địa chỉ)
    
    # Domain-specific (optional)
    BRAND_POLICY = "brand_policy"  # Vi phạm chính sách thương hiệu
    MISINFORMATION = "misinformation"  # Thông tin sai lệch (optional - nên pipeline riêng)


class SeverityLevel(int, Enum):
    """Severity levels for moderation actions"""
    CLEAN = 0  # Sạch, cho qua
    MODERATE = 1  # Trung bình - ẩn hoặc chờ duyệt
    SEVERE = 2  # Nghiêm trọng - chặn ngay


# Mapping from severity to actions
SEVERITY_ACTIONS = {
    SeverityLevel.CLEAN: "allowed",
    SeverityLevel.MODERATE: "review",
    SeverityLevel.SEVERE: "reject"
}


# Label descriptions for training data annotation
LABEL_DESCRIPTIONS = {
    ModerationLabel.TOXICITY: {
        "vi": "Ngôn từ thô tục, xúc phạm, chửi thề không nhắm vào nhóm cụ thể",
        "en": "Profanity, offensive language, general insults",
        "examples": ["đồ ngu", "mẹ kiếp", "đ*o", "vl", "đ.m"],
        "severity": {
            0: "Không có từ thô tục",
            1: "Từ thô tục nhẹ (đ.m, vl...)",
            2: "Từ thô tục nặng, lặp lại nhiều lần"
        }
    },
    ModerationLabel.HATE: {
        "vi": "Ghét bỏ, kỳ thị nhóm người dựa trên sắc tộc, tôn giáo, giới tính, khuynh hướng tình dục",
        "en": "Hate speech targeting groups based on race, religion, gender, sexual orientation",
        "examples": ["khỉ đen", "đồ đạo chó", "đồ đồng tính biến thái"],
        "severity": {
            0: "Không có hate speech",
            1: "Định kiến nhẹ, đánh giá tiêu cực nhóm",
            2: "Hate speech rõ ràng, kêu gọi bạo lực"
        }
    },
    ModerationLabel.HARASSMENT: {
        "vi": "Quấy rối, bắt nạt cá nhân cụ thể",
        "en": "Harassment, bullying targeting specific individuals",
        "examples": ["mày xấu vãi", "@user này ngu vl", "lũ bạn mày toàn rác"],
        "severity": {
            0: "Không quấy rối",
            1: "Chế giễu, châm chọc",
            2: "Quấy rối nghiêm trọng, đe dọa"
        }
    },
    ModerationLabel.THREAT: {
        "vi": "Đe dọa bạo lực, tự hại, gây nguy hiểm",
        "en": "Threats of violence, self-harm, danger",
        "examples": ["tao sẽ giết mày", "đập chết", "tự tử đi"],
        "severity": {
            0: "Không có đe dọa",
            1: "Đe dọa mơ hồ",
            2: "Đe dọa rõ ràng, nguy hiểm"
        }
    },
    ModerationLabel.SEXUAL: {
        "vi": "Nội dung khiêu dâm, tình dục, 18+",
        "en": "Sexual content, pornography, NSFW",
        "examples": ["địt", "chịch", "lồn", "cặc", "link sex"],
        "severity": {
            0: "Không có nội dung tình dục",
            1: "Gợi dục nhẹ, ám chỉ",
            2: "Khiêu dâm rõ ràng"
        }
    },
    ModerationLabel.SPAM: {
        "vi": "Quảng cáo, spam, lừa đảo, scam",
        "en": "Spam, ads, scams, fraud",
        "examples": ["inbox mua hàng", "kiếm tiền online", "cần người làm part-time"],
        "severity": {
            0: "Không spam",
            1: "Quảng cáo nhẹ, tự promote",
            2: "Spam rõ ràng, lừa đảo"
        }
    },
    ModerationLabel.PII: {
        "vi": "Thông tin cá nhân (SĐT, email, địa chỉ, CMND...)",
        "en": "Personal Identifiable Information (phone, email, address, ID)",
        "examples": ["0123456789", "user@gmail.com", "123 Lê Lợi Q1"],
        "severity": {
            0: "Không có PII",
            1: "PII không nhạy cảm (email công khai)",
            2: "PII nhạy cảm (SĐT, CMND, địa chỉ)"
        }
    },
    ModerationLabel.BRAND_POLICY: {
        "vi": "Vi phạm chính sách thương hiệu (từ khóa đối thủ, nội dung cấm...)",
        "en": "Brand policy violations (competitor keywords, banned content)",
        "examples": ["shopee rẻ hơn", "lazada tốt hơn"],
        "severity": {
            0: "Không vi phạm",
            1: "Nhắc đến đối thủ",
            2: "Quảng cáo đối thủ rõ ràng"
        }
    },
    ModerationLabel.MISINFORMATION: {
        "vi": "Thông tin sai lệch, tin giả (KHUYẾN NGHỊ: pipeline riêng)",
        "en": "Misinformation, fake news (RECOMMENDED: separate pipeline)",
        "examples": ["covid không tồn tại", "vắc xin gây tự kỷ"],
        "severity": {
            0: "Thông tin chính xác",
            1: "Thông tin chưa kiểm chứng",
            2: "Thông tin sai lệch rõ ràng"
        },
        "note": "Rất khó, nên tách pipeline riêng với fact-checking"
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
            "reasoning": "Nội dung sạch, không vi phạm"
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
    reasoning = f"Phát hiện vi phạm: {label_names} (mức {max_severity})"
    
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

