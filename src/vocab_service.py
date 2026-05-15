"""
Vocab in News - Vocabulary Service (Iteration 5)
Provides word difficulty classification with multiple levels and Chinese definitions
for English words (CET4/TOEFL/GRE level, above middle school 1500-word base).

Levels: 1=小学, 2=初中, 3=高中, 4=大学
"""

import re
from typing import Dict, List, Optional, Tuple


# ── Simple English Stemmer ───────────────────────────────────────────────────
# Strips common inflectional suffixes so that "confirmed" matches "confirm",
# "discoveries" matches "discovery", etc.

_SUFFIX_RULES = [
    # (suffix, replacement, min_stem_length)
    ("ies", "y", 4),       # carries → carry
    ("ied", "y", 4),       # carried → carry
    ("ier", "y", 4),       # happier → happy
    ("iest", "y", 4),      # happiest → happy
    ("iness", "y", 5),     # happiness → happy
    ("ement", "", 5),      # achievement → achieve
    ("fulness", "ful", 7), # carefulness → careful
    ("ation", "ate", 5),   # exploration → explore? No, this is for -ation words
    ("tion", "t", 5),      # action → act (approximate)
    ("sion", "de", 5),     # decision → decide (approximate)
    ("ment", "", 4),       # achievement → achieve
    ("ness", "", 4),       # happiness → happy
    ("ing", "", 4),        # running → run (handles most -ing)
    ("ied", "y", 4),
    ("ed", "", 3),         # walked → walk
    ("es", "", 3),         # boxes → box
    ("s", "", 3),          # cats → cat
    ("ly", "", 3),         # quickly → quick
    ("er", "", 3),         # bigger → big
    ("est", "", 3),        # biggest → big
    ("ity", "", 4),        # ability → able (approximate)
    ("al", "", 4),         # arrival → arrive (approximate)
    ("ive", "e", 4),       # creative → create
]


def _stem(word: str) -> str:
    """Return a simple stem of the given lowercase word."""
    if len(word) < 3:
        return word
    for suffix, replacement, min_len in _SUFFIX_RULES:
        if word.endswith(suffix) and len(word) - len(suffix) + len(replacement) >= min_len:
            stemmed = word[: -len(suffix)] + replacement
            if len(stemmed) >= 3:
                return stemmed
    return word


def _lookup(word_lower: str) -> Optional[Tuple[str, str, int]]:
    """Look up a word (lowercase) in the vocab, trying stemmed forms.
    Returns (definition, pos, level) or None.
    """
    # Direct match
    if word_lower in VOCAB_DIFFICULTY:
        return VOCAB_DIFFICULTY[word_lower]
    # Try stemmed form
    stemmed = _stem(word_lower)
    if stemmed != word_lower and stemmed in VOCAB_DIFFICULTY:
        return VOCAB_DIFFICULTY[stemmed]
    return None


def _lookup_entry(word_lower: str) -> Optional[Tuple[str, str]]:
    """Backward-compat: return (definition, pos) without level."""
    result = _lookup(word_lower)
    if result is None:
        return None
    return (result[0], result[1])


# ── Word Difficulty Database ──────────────────────────────────────────────
# ~210 English words with Chinese definitions and difficulty levels.
#
# Format: { "word": ("中文释义", "词性", level) }
# level: 1=小学, 2=初中, 3=高中, 4=大学

VOCAB_DIFFICULTY: Dict[str, Tuple[str, str, int]] = {
    # ════════════════════════════════════════════════════════════════
    # Level 1 — 小学 (~40 words): very common words slightly above elementary
    # ════════════════════════════════════════════════════════════════
    "ability": ("能力", "n.", 1),
    "achieve": ("实现；达到", "v.", 1),
    "advantage": ("优势", "n.", 1),
    "available": ("可用的", "adj.", 1),
    "aware": ("意识到的", "adj.", 1),
    "benefit": ("好处；受益", "n./v.", 1),
    "challenge": ("挑战", "n./v.", 1),
    "community": ("社区；群体", "n.", 1),
    "compare": ("比较", "v.", 1),
    "create": ("创造", "v.", 1),
    "culture": ("文化", "n.", 1),
    "curious": ("好奇的", "adj.", 1),
    "describe": ("描述", "v.", 1),
    "detail": ("细节", "n.", 1),
    "develop": ("发展；开发", "v.", 1),
    "discover": ("发现", "v.", 1),
    "discovery": ("发现", "n.", 1),
    "discuss": ("讨论", "v.", 1),
    "effort": ("努力", "n.", 1),
    "encourage": ("鼓励", "v.", 1),
    "energy": ("能量；精力", "n.", 1),
    "environment": ("环境", "n.", 1),
    "experiment": ("实验", "n./v.", 1),
    "explore": ("探索；探究", "v.", 1),
    "global": ("全球的", "adj.", 1),
    "identify": ("识别；确认", "v.", 1),
    "impact": ("影响；冲击", "n./v.", 1),
    "influence": ("影响", "n./v.", 1),
    "method": ("方法", "n.", 1),
    "normal": ("正常的", "adj.", 1),
    "option": ("选择", "n.", 1),
    "planet": ("行星", "n.", 1),
    "positive": ("积极的；正面的", "adj.", 1),
    "quality": ("质量；品质", "n.", 1),
    "range": ("范围", "n.", 1),
    "recognize": ("认出；承认", "v.", 1),
    "research": ("研究", "n./v.", 1),
    "resource": ("资源", "n.", 1),
    "role": ("角色；作用", "n.", 1),
    "similar": ("相似的", "adj.", 1),
    "source": ("来源", "n.", 1),
    "suggest": ("建议；表明", "v.", 1),
    "surface": ("表面", "n.", 1),
    "survive": ("生存", "v.", 1),
    "temperature": ("温度", "n.", 1),

    # ════════════════════════════════════════════════════════════════
    # Level 2 — 初中 (~80 words): intermediate vocabulary (CET4 level)
    # ════════════════════════════════════════════════════════════════
    "access": ("进入；使用权", "n./v.", 2),
    "acquire": ("获得；习得", "v.", 2),
    "adapt": ("适应", "v.", 2),
    "adequate": ("足够的", "adj.", 2),
    "adjust": ("调整", "v.", 2),
    "analyze": ("分析", "v.", 2),
    "announce": ("宣布", "v.", 2),
    "approach": ("方法；接近", "n./v.", 2),
    "appropriate": ("适当的", "adj.", 2),
    "aspect": ("方面", "n.", 2),
    "assume": ("假设", "v.", 2),
    "atmosphere": ("大气层；氛围", "n.", 2),
    "attempt": ("尝试", "n./v.", 2),
    "attitude": ("态度", "n.", 2),
    "brief": ("简短的", "adj.", 2),
    "campaign": ("运动；活动", "n.", 2),
    "capable": ("有能力的", "adj.", 2),
    "chemical": ("化学的；化学品", "adj./n.", 2),
    "claim": ("声称", "v.", 2),
    "climate": ("气候", "n.", 2),
    "comment": ("评论", "n./v.", 2),
    "communicate": ("交流", "v.", 2),
    "concentrate": ("集中；专注", "v.", 2),
    "concept": ("概念", "n.", 2),
    "concern": ("关心；担忧", "n./v.", 2),
    "conclude": ("得出结论", "v.", 2),
    "condition": ("条件；状况", "n.", 2),
    "conduct": ("进行；实施", "v.", 2),
    "confidence": ("信心", "n.", 2),
    "confirm": ("确认；证实", "v.", 2),
    "conflict": ("冲突", "n.", 2),
    "consider": ("考虑", "v.", 2),
    "constant": ("持续的；不断的", "adj.", 2),
    "construct": ("建造", "v.", 2),
    "consume": ("消费；消耗", "v.", 2),
    "context": ("上下文；背景", "n.", 2),
    "contribute": ("贡献", "v.", 2),
    "convince": ("说服", "v.", 2),
    "critical": ("关键的；批评的", "adj.", 2),
    "current": ("当前的；现行的", "adj.", 2),
    "debate": ("辩论", "n./v.", 2),
    "declare": ("宣布；声明", "v.", 2),
    "define": ("定义", "v.", 2),
    "demonstrate": ("展示；证明", "v.", 2),
    "deny": ("否认", "v.", 2),
    "deserve": ("值得", "v.", 2),
    "despite": ("尽管", "prep.", 2),
    "determine": ("决定；确定", "v.", 2),
    "device": ("设备；装置", "n.", 2),
    "digital": ("数字的", "adj.", 2),
    "display": ("展示；显示", "n./v.", 2),
    "dramatic": ("戏剧性的；巨大的", "adj.", 2),
    "economy": ("经济", "n.", 2),
    "effective": ("有效的", "adj.", 2),
    "efficient": ("高效的", "adj.", 2),
    "element": ("元素；要素", "n.", 2),
    "employ": ("雇用；使用", "v.", 2),
    "enable": ("使能够", "v.", 2),
    "entire": ("整个的；全部的", "adj.", 2),
    "equipment": ("设备；装备", "n.", 2),
    "essential": ("必要的；本质的", "adj.", 2),
    "estimate": ("估计", "v./n.", 2),
    "eventually": ("最终", "adv.", 2),
    "evidence": ("证据", "n.", 2),
    "exist": ("存在", "v.", 2),
    "expand": ("扩展；扩大", "v.", 2),
    "expert": ("专家", "n.", 2),
    "extreme": ("极端的", "adj.", 2),
    "factor": ("因素", "n.", 2),
    "feature": ("特征；特点", "n.", 2),
    "focus": ("焦点；集中", "n./v.", 2),
    "former": ("前者的；以前的", "adj.", 2),
    "generate": ("产生；生成", "v.", 2),
    "image": ("形象；图像", "n.", 2),
    "independent": ("独立的", "adj.", 2),
    "inform": ("通知；告知", "v.", 2),
    "involve": ("涉及；包含", "v.", 2),
    "issue": ("问题；议题", "n.", 2),
    "launch": ("发射；启动", "v./n.", 2),
    "likely": ("可能的", "adj.", 2),
    "locate": ("找到；位于", "v.", 2),
    "major": ("主要的", "adj.", 2),
    "media": ("媒体", "n.", 2),
    "minor": ("较小的；次要的", "adj.", 2),
    "negative": ("消极的；负面的", "adj.", 2),
    "observe": ("观察", "v.", 2),
    "obtain": ("获得", "v.", 2),
    "obvious": ("明显的", "adj.", 2),
    "occur": ("发生", "v.", 2),
    "overall": ("总体的", "adj./adv.", 2),
    "participate": ("参加", "v.", 2),
    "perform": ("表现；执行", "v.", 2),
    "previous": ("以前的", "adj.", 2),
    "process": ("过程；处理", "n./v.", 2),
    "profit": ("利润", "n.", 2),
    "propose": ("提议；建议", "v.", 2),
    "prove": ("证明", "v.", 2),
    "publish": ("出版；发表", "v.", 2),
    "purpose": ("目的", "n.", 2),
    "rapid": ("快速的", "adj.", 2),
    "react": ("反应", "v.", 2),
    "recommend": ("推荐", "v.", 2),
    "reduce": ("减少", "v.", 2),
    "reflect": ("反映；反思", "v.", 2),
    "region": ("地区；区域", "n.", 2),
    "reject": ("拒绝", "v.", 2),
    "represent": ("代表", "v.", 2),
    "require": ("需要；要求", "v.", 2),
    "respond": ("回应", "v.", 2),
    "security": ("安全", "n.", 2),
    "seek": ("寻求", "v.", 2),
    "select": ("选择", "v.", 2),
    "specific": ("具体的；特定的", "adj.", 2),
    "stable": ("稳定的", "adj.", 2),
    "stock": ("股票；库存", "n.", 2),
    "stress": ("压力；强调", "n./v.", 2),
    "structure": ("结构", "n.", 2),
    "survey": ("调查", "n./v.", 2),
    "tradition": ("传统", "n.", 2),
    "volume": ("体积；音量", "n.", 2),

    # ════════════════════════════════════════════════════════════════
    # Level 3 — 高中 (~60 words): advanced vocabulary (CET6/TOEFL)
    # ════════════════════════════════════════════════════════════════
    "circumstance": ("情况；环境", "n.", 3),
    "commercial": ("商业的；广告", "adj./n.", 3),
    "committee": ("委员会", "n.", 3),
    "component": ("组成部分", "n.", 3),
    "consequence": ("后果", "n.", 3),
    "consistent": ("一致的", "adj.", 3),
    "core": ("核心", "n.", 3),
    "corporation": ("公司；企业", "n.", 3),
    "crucial": ("至关重要的", "adj.", 3),
    "cycle": ("周期；循环", "n.", 3),
    "democracy": ("民主", "n.", 3),
    "distinguish": ("区分；辨别", "v.", 3),
    "document": ("文件；记录", "n./v.", 3),
    "editor": ("编辑", "n.", 3),
    "eliminate": ("消除", "v.", 3),
    "emerge": ("出现", "v.", 3),
    "emphasis": ("强调", "n.", 3),
    "encounter": ("遇到；遭遇", "v.", 3),
    "engage": ("参与；吸引", "v.", 3),
    "enormous": ("巨大的", "adj.", 3),
    "ensure": ("确保", "v.", 3),
    "establish": ("建立", "v.", 3),
    "evaluate": ("评估", "v.", 3),
    "evolve": ("进化；发展", "v.", 3),
    "examine": ("检查；审查", "v.", 3),
    "executive": ("高管的；行政的", "adj./n.", 3),
    "expose": ("暴露；揭露", "v.", 3),
    "external": ("外部的", "adj.", 3),
    "extraordinary": ("非凡的；特别的", "adj.", 3),
    "facility": ("设施；设备", "n.", 3),
    "flexible": ("灵活的", "adj.", 3),
    "formula": ("公式", "n.", 3),
    "frequent": ("频繁的", "adj.", 3),
    "function": ("功能；作用", "n./v.", 3),
    "fund": ("基金；资助", "n./v.", 3),
    "fundamental": ("基本的；根本的", "adj.", 3),
    "gravity": ("重力", "n.", 3),
    "illustrate": ("说明；阐明", "v.", 3),
    "imply": ("暗示", "v.", 3),
    "indicate": ("表明；指出", "v.", 3),
    "individual": ("个人的；个体", "adj./n.", 3),
    "initial": ("最初的", "adj.", 3),
    "instance": ("例子；实例", "n.", 3),
    "instrument": ("仪器；工具", "n.", 3),
    "intense": ("强烈的；激烈的", "adj.", 3),
    "interpret": ("解释；解读", "v.", 3),
    "investigate": ("调查", "v.", 3),
    "journal": ("期刊；日志", "n.", 3),
    "justify": ("证明...有理", "v.", 3),
    "laboratory": ("实验室", "n.", 3),
    "legal": ("法律的；合法的", "adj.", 3),
    "logical": ("合乎逻辑的", "adj.", 3),
    "maintain": ("维持；保养", "v.", 3),
    "mental": ("精神的；心理的", "adj.", 3),
    "military": ("军事的", "adj.", 3),
    "modify": ("修改", "v.", 3),
    "molecule": ("分子", "n.", 3),
    "monitor": ("监控；监视器", "v./n.", 3),
    "network": ("网络", "n.", 3),
    "official": ("官方的；官员", "adj./n.", 3),
    "opponent": ("对手", "n.", 3),
    "orbit": ("轨道；绕行", "n./v.", 3),
    "phenomenon": ("现象", "n.", 3),
    "policy": ("政策", "n.", 3),
    "poll": ("民意调查", "n.", 3),
    "potential": ("潜力；潜在的", "n./adj.", 3),
    "predict": ("预测", "v.", 3),
    "preserve": ("保护；保存", "v.", 3),
    "press": ("媒体；按压", "n./v.", 3),
    "principle": ("原则；原理", "n.", 3),
    "professional": ("专业的；专业人士", "adj./n.", 3),
    "promote": ("推广；晋升", "v.", 3),
    "protest": ("抗议", "n./v.", 3),
    "pursue": ("追求", "v.", 3),
    "regulate": ("调节；管理", "v.", 3),
    "relevant": ("相关的", "adj.", 3),
    "reliable": ("可靠的", "adj.", 3),
    "reveal": ("揭示；透露", "v.", 3),
    "revolution": ("革命", "n.", 3),
    "satellite": ("卫星", "n.", 3),
    "section": ("部分；章节", "n.", 3),
    "senator": ("参议员", "n.", 3),
    "significant": ("重要的；显著的", "adj.", 3),
    "solar": ("太阳的；太阳系的", "adj.", 3),
    "species": ("物种", "n.", 3),
    "strategy": ("策略", "n.", 3),
    "struggle": ("挣扎；斗争", "v./n.", 3),
    "sufficient": ("足够的", "adj.", 3),
    "summarize": ("总结", "v.", 3),
    "telescope": ("望远镜", "n.", 3),
    "tissue": ("组织（生物）", "n.", 3),
    "universe": ("宇宙", "n.", 3),
    "victim": ("受害者", "n.", 3),

    # ════════════════════════════════════════════════════════════════
    # Level 4 — 大学 (~30 words): academic / GRE-level vocabulary
    # ════════════════════════════════════════════════════════════════
    "abstract": ("抽象的；摘要", "adj./n.", 4),
    "ambiguous": ("模糊的；有歧义的", "adj.", 4),
    "comprehensive": ("全面的；综合的", "adj.", 4),
    "controversial": ("有争议的", "adj.", 4),
    "correlate": ("关联；相关", "v.", 4),
    "criteria": ("标准", "n.", 4),
    "dilemma": ("困境；两难", "n.", 4),
    "diminish": ("减少；削弱", "v.", 4),
    "empirical": ("经验的；实证的", "adj.", 4),
    "fluctuate": ("波动；起伏", "v.", 4),
    "hypothesis": ("假说；假设", "n.", 4),
    "ideology": ("意识形态", "n.", 4),
    "inevitable": ("不可避免的", "adj.", 4),
    "infrastructure": ("基础设施", "n.", 4),
    "innovation": ("创新", "n.", 4),
    "integrate": ("整合；融合", "v.", 4),
    "mechanism": ("机制；原理", "n.", 4),
    "negotiate": ("谈判；协商", "v.", 4),
    "notion": ("概念；观念", "n.", 4),
    "paradigm": ("范式；模式", "n.", 4),
    "predominantly": ("主要地", "adv.", 4),
    "preliminary": ("初步的", "adj.", 4),
    "rational": ("理性的；合理的", "adj.", 4),
    "skeptical": ("怀疑的", "adj.", 4),
    "subordinate": ("从属的；下级", "adj./n.", 4),
    "supplement": ("补充；增补", "v./n.", 4),
    "sustainable": ("可持续的", "adj.", 4),
    "theoretical": ("理论的", "adj.", 4),
    "undermine": ("削弱；破坏", "v.", 4),
    "valid": ("有效的；合理的", "adj.", 4),
    "vulnerable": ("脆弱的；易受伤害的", "adj.", 4),
    "widespread": ("广泛的；普遍的", "adj.", 4),
}


# ════════════════════════════════════════════════════════════════════
# Level Configuration
# ════════════════════════════════════════════════════════════════════

LEVEL_NAMES = {
    1: "小学",
    2: "初中",
    3: "高中",
    4: "大学",
}

# Cumulative: which levels to highlight for each user level
# 小学 user: highlight level 1 words
# 初中 user: highlight level 1+2 words
# 高中 user: highlight level 1+2+3 words
# 大学 user: highlight all words
LEVEL_HIGHLIGHT_RANGES = {
    1: {1},               # 小学: only level 1
    2: {1, 2},            # 初中: levels 1+2
    3: {1, 2, 3},         # 高中: levels 1+2+3
    4: {1, 2, 3, 4},      # 大学: all levels
}

# Max highlights per level
MAX_HIGHLIGHTS = {
    1: 3,   # 小学
    2: 6,   # 初中
    3: 8,   # 高中
    4: 10,  # 大学
}


def get_levels_for_user(user_level: int) -> set:
    """Return the set of vocab levels that should be highlighted for a user level."""
    return LEVEL_HIGHLIGHT_RANGES.get(user_level, {1, 2})


def get_max_highlights(user_level: int) -> int:
    """Return the max number of highlighted words for a user level."""
    return MAX_HIGHLIGHTS.get(user_level, 6)


def is_difficult_for_level(word: str, user_level: int) -> bool:
    """Return True if the word is in the vocabulary AND at or below the user's level."""
    entry = _lookup(word.lower().strip())
    if entry is None:
        return False
    word_level = entry[2]
    return word_level in get_levels_for_user(user_level)


# ════════════════════════════════════════════════════════════════════
# Public API (updated for levels; backward-compatible defaults)
# ════════════════════════════════════════════════════════════════════

def is_difficult(word: str) -> bool:
    """Return True if the word is in the difficult vocabulary list.
    Matching is case-insensitive, with basic stemming.
    """
    return _lookup(word.lower().strip()) is not None


def get_definition(word: str) -> Optional[Tuple[str, str]]:
    """Return (chinese_definition, part_of_speech) or None if not found.
    Matching is case-insensitive, with basic stemming.
    """
    return _lookup_entry(word.lower().strip())


def get_full_entry(word: str) -> Optional[Tuple[str, str, int]]:
    """Return (chinese_definition, part_of_speech, level) or None if not found."""
    return _lookup(word.lower().strip())


def filter_vocab_by_level(user_level: int) -> dict:
    """Return a subset of VOCAB_DIFFICULTY filtered to the user's level range."""
    allowed = get_levels_for_user(user_level)
    return {w: e for w, e in VOCAB_DIFFICULTY.items() if e[2] in allowed}


def tokenize(text: str, user_level: int = 2) -> List[Dict]:
    """Split text into token objects for template rendering.

    Each token is a dict:
        {"text": str, "is_word": bool, "word": str | None,
         "is_difficult": bool, "definition": str | None, "pos": str | None,
         "level": int | None}

    user_level determines which word levels are considered "difficult".
    Non-word tokens (spaces, punctuation) are preserved and marked
    with is_word=False.
    """
    allowed_levels = get_levels_for_user(user_level)
    tokens = []
    pattern = re.compile(
        r"([a-zA-Z]+(?:'[a-zA-Z]+)?(?:-[a-zA-Z]+)*)"
        r"|(\d[\d,]*(?:-[a-zA-Z]+)*)"
        r"|([^\w\s])"
        r"|(\s+)"
    )
    for match in pattern.finditer(text):
        raw = match.group(0)
        word_part = match.group(1) or match.group(2)
        if word_part:
            entry = _lookup(word_part.lower()) if match.group(1) else None
            if entry and entry[2] in allowed_levels:
                tokens.append({
                    "text": word_part,
                    "is_word": True,
                    "word": word_part,
                    "is_difficult": True,
                    "definition": entry[0],
                    "pos": entry[1],
                    "level": entry[2],
                })
            else:
                tokens.append({
                    "text": word_part,
                    "is_word": True,
                    "word": word_part,
                    "is_difficult": False,
                    "definition": None,
                    "pos": None,
                    "level": None,
                })
        else:
            tokens.append({
                "text": raw,
                "is_word": False,
                "word": None,
                "is_difficult": False,
                "definition": None,
                "pos": None,
                "level": None,
            })
    return tokens


def find_difficult_words(text: str, user_level: int = 4) -> List[Dict]:
    """Return list of difficult words found in the text.

    Each item: {"word": str, "definition": str, "pos": str, "lower": str, "level": int}
    Case-insensitive; each word appears only once in the result.
    user_level controls which vocab levels to include (default 4 = all).
    """
    allowed_levels = get_levels_for_user(user_level)
    found: Dict[str, Dict] = {}
    for match in re.finditer(r"[a-zA-Z]+(?:'[a-zA-Z]+)?", text):
        w = match.group(0)
        key = w.lower()
        entry = _lookup(key)
        if entry is not None and key not in found and entry[2] in allowed_levels:
            defn, pos, level = entry
            found[key] = {
                "word": w, "lower": key,
                "definition": defn, "pos": pos, "level": level,
            }
    return list(found.values())


def find_difficult_words_sorted(text: str, user_level: int = 4) -> List[Dict]:
    """Like find_difficult_words but sorted by first appearance in text."""
    result = find_difficult_words(text, user_level)
    lower_text = text.lower()
    result.sort(key=lambda item: lower_text.index(item["lower"]))
    return result


def count_vocab_by_level() -> Dict[int, int]:
    """Return count of words per level."""
    counts = {1: 0, 2: 0, 3: 0, 4: 0}
    for entry in VOCAB_DIFFICULTY.values():
        counts[entry[2]] = counts.get(entry[2], 0) + 1
    return counts
