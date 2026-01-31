"""
Vietnamese Sentiment Words Database
Comprehensive vocabulary for sentiment analysis
"""

# ==================== POSITIVE WORDS ====================

# High positivity
HIGHLY_POSITIVE = [
    # High quality
    'xuất sắc', 'tuyệt vời', 'tuyệt hảo', 'hoàn hảo', 'tuyệt đỉnh',
    'tuyệt vời quá', 'quá tuyệt', 'quá đỉnh', 'đỉnh cao', 'đỉnh của đỉnh',
    'amazing', 'excellent', 'perfect', 'outstanding', 'superb',
    'fantastic', 'wonderful', 'awesome', 'incredible', 'brilliant',
    
    # High satisfaction
    'rất hài lòng', 'cực kỳ hài lòng', 'hài lòng tuyệt đối',
    'thích lắm', 'thích cực', 'thích vô cùng', 'yêu quá',
    'love', 'adore', 'absolutely love',
    
    # Product quality
    'chất lượng tuyệt vời', 'chất lượng cao', 'siêu phẩm',
    'sản phẩm tốt nhất', 'đáng tiền', 'xứng đáng',
    'bền', 'rất bền', 'cực kỳ bền', 'siêu bền', 'bền bỉ',
    'durable', 'long-lasting', 'sturdy',
    
    # Service
    'phục vụ tận tình', 'phục vụ chu đáo', 'dịch vụ tốt nhất',
    'chăm sóc khách hàng tốt', 'nhân viên nhiệt tình',
]

# Moderate positivity
MODERATELY_POSITIVE = [
    # Good
    'tốt', 'tốt lắm', 'khá tốt', 'rất tốt', 'tốt quá', 'tốt đấy',
    'good', 'very good', 'great', 'nice', 'fine',
    
    # Okay/Fine
    'ổn', 'ổn áp', 'khá ổn', 'rất ổn', 'ổn thỏa',
    'ok', 'okay', 'not bad', 'decent',
    
    # Satisfied
    'hài lòng', 'khá hài lòng', 'vừa lòng', 'thỏa mãn',
    'satisfied', 'pleased', 'happy',
    
    # Quality
    'chất lượng', 'chất lượng tốt', 'chất lượng ổn',
    'đẹp', 'đẹp lắm', 'đẹp quá', 'xinh', 'đẹp mắt',
    'beautiful', 'pretty', 'attractive',
    
    # Price
    'giá tốt', 'giá hợp lý', 'giá phải chăng', 'rẻ',
    'affordable', 'reasonable price', 'cheap',
    
    # Convenience
    'tiện', 'tiện lợi', 'thuận tiện', 'dễ dùng',
    'convenient', 'easy', 'user-friendly',
    
    # Fast
    'nhanh', 'nhanh chóng', 'giao nhanh', 'ship nhanh',
    'fast', 'quick', 'speedy',
]

# Slight positivity
SLIGHTLY_POSITIVE = [
    # Acceptable
    'được', 'được đấy', 'cũng được', 'tạm được',
    'acceptable', 'alright',
    
    # Pleased/Approve
    'ưng', 'ưng ý', 'vừa ý', 'như ý',
    
    # Quite/Pretty good
    'khá', 'khá lắm', 'khá ổn', 'khá tốt',
    'quite good', 'fairly good',
    
    # Delicious
    'ngon', 'ngon lắm', 'ngon quá', 'ngon miệng',
    'delicious', 'tasty', 'yummy',
    
    # Worth it
    'đáng mua', 'đáng tin', 'đáng dùng', 'đáng giá',
    'worth it', 'worthwhile',
]

# ==================== NEGATIVE WORDS (NON-TOXIC) ====================

# High negativity (but not toxic)
HIGHLY_NEGATIVE = [
    # Poor quality
    'tệ', 'tệ hại', 'tồi', 'tồi tệ', 'tồi quá', 'tệ quá',
    'kém', 'kém chất lượng', 'kém cỏi', 'quá kém',
    'terrible', 'awful', 'horrible', 'bad', 'poor quality',
    
    # Disappointed
    'thất vọng', 'rất thất vọng', 'thất vọng quá', 'thất vọng về',
    'disappointed', 'very disappointed', 'let down',
    
    # Unsatisfied
    'không hài lòng', 'chưa hài lòng', 'không vừa lòng',
    'unsatisfied', 'not satisfied', 'unhappy',
    
    # Error / Broken
    'lỗi', 'lỗi nhiều', 'hay lỗi', 'hỏng', 'hỏng luôn', 'bị hỏng',
    'broken', 'defective', 'faulty', 'error', 'buggy',
    
    # Fake / Counterfeit
    'giả', 'hàng giả', 'hàng nhái', 'hàng fake', 'fake',
    'counterfeit', 'knock-off', 'imitation',
    
    # Scams / Dishonest
    'lừa đảo', 'scam', 'lừa gạt', 'gian lận',
    'không uy tín', 'mất uy tín', 'uy tín kém',
    'fraud', 'cheat', 'dishonest',
]

# Moderate negativity
MODERATELY_NEGATIVE = [
    # Not good
    'không tốt', 'không được', 'không hay', 'chưa tốt',
    'not good', 'not great', 'mediocre',
    
    # Subpar/Inferior
    'dở', 'dở quá', 'dở ẹc', 'dở tệ',
    'poor', 'subpar', 'inferior',
    
    # Slow
    'chậm', 'chậm quá', 'ship chậm', 'giao chậm', 'lâu',
    'slow', 'delayed', 'late',
    
    # Expensive
    'đắt', 'đắt quá', 'quá đắt', 'giá cao',
    'expensive', 'overpriced', 'costly',
    
    # Difficult
    'khó', 'khó dùng', 'khó sử dụng', 'phức tạp',
    'difficult', 'hard', 'complicated',
    
    # Small / Lacking
    'nhỏ', 'quá nhỏ', 'nhỏ bé', 'thiếu', 'thiếu sót',
    'small', 'tiny', 'lacking', 'missing',
]

# Slight negativity
SLIGHTLY_NEGATIVE = [
    # Average/So-so
    'tạm', 'tạm ổn', 'tạm được', 'tạm chấp nhận',
    'so-so', 'meh', 'average',
    
    # Ordinary/Nothing special
    'bình thường', 'bình thường thôi', 'không có gì đặc biệt',
    'ordinary', 'nothing special', 'normal',
    
    # Not as expected
    'không như mong đợi', 'không như quảng cáo',
    'không giống mô tả', 'không đúng',
    'not as expected', 'not as advertised',
    
    # Slightly/A bit bad
    'hơi tệ', 'hơi kém', 'hơi đắt', 'hơi nhỏ',
    'a bit', 'slightly bad',
]

# ==================== NEUTRAL WORDS ====================

NEUTRAL_WORDS = [
    # Objective descriptions
    'nhận được', 'đã nhận', 'đã mua', 'mua rồi',
    'như hình', 'đúng hình', 'giống hình', 'đúng mô tả',
    'shipped', 'received', 'got it', 'as described',
    
    # Objective evaluation
    'bình thường', 'như thường', 'như mọi khi',
    'normal', 'standard', 'typical',
    
    # Uncertain/Unknown
    'không rõ', 'chưa biết', 'chưa dùng', 'mới mua',
    'not sure', 'uncertain', 'just bought',
]

# ==================== SPECIAL PHRASES (CONTEXT-AWARE) ====================

# Positive phrases
POSITIVE_PHRASES = [
    'rất tốt', 'quá tốt', 'tốt lắm', 'khá tốt', 'tốt quá',
    'rất đẹp', 'đẹp lắm', 'đẹp quá', 'quá đẹp',
    'rất hài lòng', 'hài lòng lắm', 'quá hài lòng',
    'sẽ mua lại', 'mua lại', 'đáng mua', 'nên mua',
    'recommend', 'highly recommend', 'worth buying',
    'chất lượng tốt', 'chất lượng cao', 'chất lượng ổn',
    'giao hàng nhanh', 'ship nhanh', 'đóng gói cẩn thận',
    'giá tốt', 'giá hợp lý', 'giá phải chăng', 'phải chăng',
    'đáng tiền', 'đáng đồng tiền', 'đáng giá',
    'phục vụ tốt', 'thái độ tốt', 'nhiệt tình',
    '5 sao', '5 stars', '👍', '❤️', '😊', '🥰',
]

# Negative phrases (non-toxic)
NEGATIVE_PHRASES = [
    'không tốt', 'không được', 'chưa tốt', 'chẳng tốt',
    'thất vọng', 'rất thất vọng', 'thất vọng quá',
    'không hài lòng', 'chưa hài lòng', 'không vừa lòng',
    'không đáng', 'không nên mua', 'không recommend',
    'chất lượng kém', 'chất lượng tệ', 'chất lượng không tốt',
    'giao hàng chậm', 'ship chậm', 'lâu quá',
    'giá đắt', 'quá đắt', 'đắt quá', 'giá cao',
    'thái độ không tốt', 'phục vụ kém', 'không nhiệt tình',
    'lỗi', 'hỏng', 'bị lỗi', 'không dùng được',
    '1 sao', '1 star', '👎', '😞', '😡',
]

# ==================== EMOJI & EMOTICONS ====================

POSITIVE_EMOJIS = [
    '😊', '😃', '😄', '😁', '🥰', '😍', '🤩', '❤️', '💕', '💖',
    '👍', '👌', '✨', '⭐', '🌟', '💯', '🎉', '🔥',
    ':)', ':]', ':D', '^_^', '^^', '<3',
]

NEGATIVE_EMOJIS = [
    '😞', '😢', '😭', '😡', '😠', '🤬', '💔', '👎', '❌', '⚠️',
    ':(', ':[', 'T_T', 'T.T', '>_<', '-_-',
]

NEUTRAL_EMOJIS = [
    '😐', '😶', '🙂', '😑', '🤔', '😕', '🤷',
    ':|', '._.',
]

# ==================== SCORING SYSTEM ====================

SENTIMENT_SCORES = {
    'HIGHLY_POSITIVE': 10,
    'MODERATELY_POSITIVE': 7,
    'SLIGHTLY_POSITIVE': 4,
    'NEUTRAL': 0,
    'SLIGHTLY_NEGATIVE': -4,
    'MODERATELY_NEGATIVE': -7,
    'HIGHLY_NEGATIVE': -10,
}

# Scores for emojis
EMOJI_SCORE = {
    'POSITIVE': 5,
    'NEGATIVE': -5,
    'NEUTRAL': 0,
}

# Scores for phrases
PHRASE_SCORE = {
    'POSITIVE': 8,
    'NEGATIVE': -8,
}

# Sentiment thresholds
POSITIVE_THRESHOLD = 5      # >= 5 là positive
NEGATIVE_THRESHOLD = -5     # <= -5 là negative
# Neutral range is [-5, 5]

# ==================== INTENSIFIERS (Emphasis words) ====================

INTENSIFIERS = {
    'rất': 1.5,
    'quá': 1.7,
    'cực': 1.8,
    'cực kỳ': 2.0,
    'siêu': 1.8,
    'vô cùng': 2.0,
    'hết sức': 1.6,
    'thật': 1.3,
    'thật sự': 1.4,
    'thực sự': 1.4,
    'lắm': 1.3,
    'nhiều': 1.2,
    'too': 1.5,
    'very': 1.4,
    'so': 1.5,
    'extremely': 2.0,
    'super': 1.8,
}

# Negation words
NEGATIONS = [
    'không', 'chẳng', 'chả', 'đâu', 'không có',
    'chưa', 'chưa bao giờ', 'không bao giờ',
    'not', 'no', 'never', "don't", "doesn't", "didn't",
]

# ==================== HELPER FUNCTIONS ====================

def get_all_positive_words():
    """Get all positive words"""
    return HIGHLY_POSITIVE + MODERATELY_POSITIVE + SLIGHTLY_POSITIVE

def get_all_negative_words():
    """Get all negative words (non-toxic)"""
    return HIGHLY_NEGATIVE + MODERATELY_NEGATIVE + SLIGHTLY_NEGATIVE

def get_all_sentiment_words():
    """Get all sentiment words"""
    return get_all_positive_words() + get_all_negative_words() + NEUTRAL_WORDS

def is_positive_emoji(char):
    """Check if emoji is positive"""
    return char in POSITIVE_EMOJIS

def is_negative_emoji(char):
    """Check if emoji is negative"""
    return char in NEGATIVE_EMOJIS

def is_neutral_emoji(char):
    """Check if emoji is neutral"""
    return char in NEUTRAL_EMOJIS

