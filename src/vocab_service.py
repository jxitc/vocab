"""
Vocab in News - Vocabulary Service (Iteration 1)
Provides word difficulty classification and Chinese definitions
for intermediate+ English words (CET4/TOEFL level, above middle school 1500-word base).
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
    ("ied", "y", 4),       # duplicated below intentionally
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
            # Don't over-stem very short words
            if len(stemmed) >= 3:
                return stemmed
    return word


def _lookup(word_lower: str) -> Optional[Tuple[str, str]]:
    """Look up a word (lowercase) in the vocab, trying stemmed forms."""
    # Direct match
    if word_lower in VOCAB_DIFFICULTY:
        return VOCAB_DIFFICULTY[word_lower]
    # Try stemmed form
    stemmed = _stem(word_lower)
    if stemmed != word_lower and stemmed in VOCAB_DIFFICULTY:
        return VOCAB_DIFFICULTY[stemmed]
    return None


# ── Word Difficulty Database ──────────────────────────────────────────────
# ~200 common intermediate+ English words with Chinese definitions.
# These are words that exceed the ~1500-word vocabulary of a Chinese
# middle school student (CET4/TOEFL level and above).
#
# Format: { "word": ("中文释义", "词性") }

VOCAB_DIFFICULTY: Dict[str, Tuple[str, str]] = {
    # ── Academic & Study (学习与学术) ──
    "ability": ("能力", "n."),
    "abroad": ("国外", "adv."),
    "access": ("进入；使用权", "n./v."),
    "achieve": ("实现；达到", "v."),
    "acquire": ("获得；习得", "v."),
    "adapt": ("适应", "v."),
    "adequate": ("足够的", "adj."),
    "adjust": ("调整", "v."),
    "advantage": ("优势", "n."),
    "analyze": ("分析", "v."),
    "approach": ("方法；接近", "n./v."),
    "appropriate": ("适当的", "adj."),
    "aspect": ("方面", "n."),
    "assume": ("假设", "v."),
    "attempt": ("尝试", "n./v."),
    "attitude": ("态度", "n."),
    "available": ("可用的", "adj."),
    "aware": ("意识到的", "adj."),
    "benefit": ("好处；受益", "n./v."),
    "brief": ("简短的", "adj."),
    "capable": ("有能力的", "adj."),
    "challenge": ("挑战", "n./v."),
    "circumstance": ("情况；环境", "n."),
    "claim": ("声称", "v."),
    "comment": ("评论", "n./v."),
    "communicate": ("交流", "v."),
    "community": ("社区；群体", "n."),
    "compare": ("比较", "v."),
    "complex": ("复杂的", "adj."),
    "concentrate": ("集中；专注", "v."),
    "concept": ("概念", "n."),
    "concern": ("关心；担忧", "n./v."),
    "conclude": ("得出结论", "v."),
    "condition": ("条件；状况", "n."),
    "conduct": ("进行；实施", "v."),
    "confidence": ("信心", "n."),
    "confirm": ("确认；证实", "v."),
    "conflict": ("冲突", "n."),
    "consequence": ("后果", "n."),
    "consider": ("考虑", "v."),
    "consistent": ("一致的", "adj."),
    "constant": ("持续的；不断的", "adj."),
    "construct": ("建造", "v."),
    "context": ("上下文；背景", "n."),
    "contribute": ("贡献", "v."),
    "convince": ("说服", "v."),
    "create": ("创造", "v."),
    "critical": ("关键的；批评的", "adj."),
    "crucial": ("至关重要的", "adj."),
    "culture": ("文化", "n."),
    "curious": ("好奇的", "adj."),
    "current": ("当前的；现行的", "adj."),

    # ── Debate & Discussion (讨论与辩论) ──
    "debate": ("辩论", "n./v."),
    "declare": ("宣布；声明", "v."),
    "define": ("定义", "v."),
    "demonstrate": ("展示；证明", "v."),
    "deny": ("否认", "v."),
    "describe": ("描述", "v."),
    "deserve": ("值得", "v."),
    "despite": ("尽管", "prep."),
    "detail": ("细节", "n."),
    "determine": ("决定；确定", "v."),
    "develop": ("发展；开发", "v."),
    "device": ("设备；装置", "n."),
    "discover": ("发现", "v."),
    "discovery": ("发现", "n."),
    "discuss": ("讨论", "v."),
    "display": ("展示；显示", "n./v."),
    "distinguish": ("区分；辨别", "v."),
    "dramatic": ("戏剧性的；巨大的", "adj."),
    "effective": ("有效的", "adj."),
    "efficient": ("高效的", "adj."),
    "effort": ("努力", "n."),
    "element": ("元素；要素", "n."),
    "eliminate": ("消除", "v."),
    "emerge": ("出现", "v."),
    "emphasis": ("强调", "n."),
    "employ": ("雇用；使用", "v."),
    "enable": ("使能够", "v."),
    "encounter": ("遇到；遭遇", "v."),
    "encourage": ("鼓励", "v."),
    "energy": ("能量；精力", "n."),
    "engage": ("参与；吸引", "v."),
    "enormous": ("巨大的", "adj."),
    "ensure": ("确保", "v."),
    "entire": ("整个的；全部的", "adj."),
    "environment": ("环境", "n."),
    "equipment": ("设备；装备", "n."),
    "essential": ("必要的；本质的", "adj."),
    "establish": ("建立", "v."),
    "evaluate": ("评估", "v."),
    "eventually": ("最终", "adv."),
    "evidence": ("证据", "n."),
    "examine": ("检查；审查", "v."),
    "exist": ("存在", "v."),
    "expand": ("扩展；扩大", "v."),
    "experiment": ("实验", "n./v."),
    "expert": ("专家", "n."),
    "explore": ("探索；探究", "v."),
    "expose": ("暴露；揭露", "v."),
    "external": ("外部的", "adj."),
    "extraordinary": ("非凡的；特别的", "adj."),
    "extreme": ("极端的", "adj."),

    # ── Features & Qualities (特征与品质) ──
    "facility": ("设施；设备", "n."),
    "factor": ("因素", "n."),
    "feature": ("特征；特点", "n."),
    "flexible": ("灵活的", "adj."),
    "focus": ("焦点；集中", "n./v."),
    "former": ("前者的；以前的", "adj."),
    "frequent": ("频繁的", "adj."),
    "function": ("功能；作用", "n./v."),
    "fundamental": ("基本的；根本的", "adj."),
    "generate": ("产生；生成", "v."),
    "global": ("全球的", "adj."),
    "identify": ("识别；确认", "v."),
    "illustrate": ("说明；阐明", "v."),
    "impact": ("影响；冲击", "n./v."),
    "imply": ("暗示", "v."),
    "indicate": ("表明；指出", "v."),
    "individual": ("个人的；个体", "adj./n."),
    "influence": ("影响", "n./v."),
    "inform": ("通知；告知", "v."),
    "initial": ("最初的", "adj."),
    "instance": ("例子；实例", "n."),
    "instrument": ("仪器；工具", "n."),
    "intense": ("强烈的；激烈的", "adj."),
    "interpret": ("解释；解读", "v."),
    "investigate": ("调查", "v."),
    "involve": ("涉及；包含", "v."),
    "issue": ("问题；议题", "n."),
    "item": ("物品；项目", "n."),

    # ── Logic & Measurement (逻辑与测量) ──
    "justify": ("证明...有理", "v."),
    "likely": ("可能的", "adj."),
    "locate": ("找到；位于", "v."),
    "logical": ("合乎逻辑的", "adj."),
    "maintain": ("维持；保养", "v."),
    "major": ("主要的", "adj."),
    "measure": ("测量；措施", "v./n."),
    "mental": ("精神的；心理的", "adj."),
    "method": ("方法", "n."),
    "minor": ("较小的；次要的", "adj."),
    "modify": ("修改", "v."),
    "monitor": ("监控；监视器", "v./n."),
    "negative": ("消极的；负面的", "adj."),
    "normal": ("正常的", "adj."),
    "obtain": ("获得", "v."),
    "obvious": ("明显的", "adj."),
    "occur": ("发生", "v."),
    "option": ("选择", "n."),
    "original": ("原始的；原创的", "adj."),
    "overall": ("总体的", "adj./adv."),
    "participate": ("参加", "v."),
    "perform": ("表现；执行", "v."),
    "phenomenon": ("现象", "n."),
    "physical": ("身体的；物理的", "adj."),
    "policy": ("政策", "n."),
    "positive": ("积极的；正面的", "adj."),
    "potential": ("潜力；潜在的", "n./adj."),
    "predict": ("预测", "v."),
    "preserve": ("保护；保存", "v."),
    "previous": ("以前的", "adj."),
    "principle": ("原则；原理", "n."),
    "process": ("过程；处理", "n./v."),
    "propose": ("提议；建议", "v."),
    "prove": ("证明", "v."),
    "publish": ("出版；发表", "v."),
    "purpose": ("目的", "n."),
    "pursue": ("追求", "v."),

    # ── Quality & Resources (质量与资源) ──
    "quality": ("质量；品质", "n."),
    "range": ("范围", "n."),
    "rapid": ("快速的", "adj."),
    "react": ("反应", "v."),
    "recognize": ("认出；承认", "v."),
    "recommend": ("推荐", "v."),
    "reduce": ("减少", "v."),
    "reflect": ("反映；反思", "v."),
    "region": ("地区；区域", "n."),
    "regulate": ("调节；管理", "v."),
    "reject": ("拒绝", "v."),
    "relevant": ("相关的", "adj."),
    "reliable": ("可靠的", "adj."),
    "represent": ("代表", "v."),
    "require": ("需要；要求", "v."),
    "research": ("研究", "n./v."),
    "resource": ("资源", "n."),
    "respond": ("回应", "v."),
    "reveal": ("揭示；透露", "v."),
    "role": ("角色；作用", "n."),
    "section": ("部分；章节", "n."),
    "seek": ("寻求", "v."),
    "select": ("选择", "v."),
    "significant": ("重要的；显著的", "adj."),
    "similar": ("相似的", "adj."),
    "source": ("来源", "n."),
    "specific": ("具体的；特定的", "adj."),
    "stable": ("稳定的", "adj."),
    "strategy": ("策略", "n."),
    "stress": ("压力；强调", "n./v."),
    "structure": ("结构", "n."),
    "struggle": ("挣扎；斗争", "v./n."),
    "sufficient": ("足够的", "adj."),
    "suggest": ("建议；表明", "v."),
    "summarize": ("总结", "v."),
    "surface": ("表面", "n."),
    "survey": ("调查", "n./v."),
    "survive": ("生存", "v."),

    # ── Technology & Science (科技) ──
    "atmosphere": ("大气层；氛围", "n."),
    "chemical": ("化学的；化学品", "adj./n."),
    "climate": ("气候", "n."),
    "component": ("组成部分", "n."),
    "consume": ("消费；消耗", "v."),
    "core": ("核心", "n."),
    "cycle": ("周期；循环", "n."),
    "digital": ("数字的", "adj."),
    "evolve": ("进化；发展", "v."),
    "explore": ("探索", "v."),
    "formula": ("公式", "n."),
    "gravity": ("重力", "n."),
    "laboratory": ("实验室", "n."),
    "launch": ("发射；启动", "v./n."),
    "molecule": ("分子", "n."),
    "observe": ("观察", "v."),
    "orbit": ("轨道；绕行", "n./v."),
    "planet": ("行星", "n."),
    "satellite": ("卫星", "n."),
    "solar": ("太阳的", "adj."),
    "species": ("物种", "n."),
    "telescope": ("望远镜", "n."),
    "temperature": ("温度", "n."),
    "tissue": ("组织（生物）", "n."),
    "universe": ("宇宙", "n."),
    "volume": ("体积；音量", "n."),

    # ── Social & Media (社会与媒体) ──
    "advertise": ("做广告", "v."),
    "announce": ("宣布", "v."),
    "audience": ("观众；听众", "n."),
    "campaign": ("运动；活动", "n."),
    "celebrity": ("名人", "n."),
    "commercial": ("商业的；广告", "adj./n."),
    "committee": ("委员会", "n."),
    "confirm": ("确认", "v."),
    "corporation": ("公司；企业", "n."),
    "democracy": ("民主", "n."),
    "document": ("文件；记录", "n./v."),
    "economy": ("经济", "n."),
    "editor": ("编辑", "n."),
    "establish": ("建立", "v."),
    "estimate": ("估计", "v./n."),
    "exchange": ("交换；交流", "n./v."),
    "executive": ("高管的；行政的", "adj./n."),
    "fund": ("基金；资助", "n./v."),
    "image": ("形象；图像", "n."),
    "immigrant": ("移民", "n."),
    "independent": ("独立的", "adj."),
    "journal": ("期刊；日志", "n."),
    "legal": ("法律的；合法的", "adj."),
    "media": ("媒体", "n."),
    "military": ("军事的", "adj."),
    "network": ("网络", "n."),
    "official": ("官方的；官员", "adj./n."),
    "opponent": ("对手", "n."),
    "poll": ("民意调查", "n."),
    "press": ("媒体；按压", "n./v."),
    "professional": ("专业的；专业人士", "adj./n."),
    "profit": ("利润", "n."),
    "promote": ("推广；晋升", "v."),
    "protest": ("抗议", "n./v."),
    "publish": ("出版；发表", "v."),
    "register": ("注册；登记", "v."),
    "release": ("释放；发布", "v./n."),
    "report": ("报告；报道", "n./v."),
    "revolution": ("革命", "n."),
    "security": ("安全", "n."),
    "senator": ("参议员", "n."),
    "stock": ("股票；库存", "n."),
    "tradition": ("传统", "n."),
    "victim": ("受害者", "n."),
}

# ── Public API ────────────────────────────────────────────────────────────

def is_difficult(word: str) -> bool:
    """Return True if the word is in the difficult vocabulary list.

    Matching is case-insensitive, with basic stemming.
    """
    return _lookup(word.lower().strip()) is not None


def get_definition(word: str) -> Optional[Tuple[str, str]]:
    """Return (chinese_definition, part_of_speech) or None if not found.

    Matching is case-insensitive, with basic stemming.
    """
    return _lookup(word.lower().strip())


def tokenize(text: str) -> List[Dict]:
    """Split text into token objects for template rendering.

    Each token is a dict:
        {"text": str, "is_word": bool, "word": str | None,
         "is_difficult": bool, "definition": str | None, "pos": str | None}

    Non-word tokens (spaces, punctuation) are preserved and marked
    with is_word=False.
    """
    tokens = []
    # Match: word characters OR single non-word/non-space chars OR whitespace runs
    pattern = re.compile(r"([a-zA-Z]+(?:'[a-zA-Z]+)?)|([^\w\s])|(\s+)")
    for match in pattern.finditer(text):
        raw = match.group(0)
        word_part = match.group(1)
        if word_part:
            entry = _lookup(word_part.lower())
            tokens.append({
                "text": word_part,
                "is_word": True,
                "word": word_part,
                "is_difficult": entry is not None,
                "definition": entry[0] if entry else None,
                "pos": entry[1] if entry else None,
            })
        else:
            tokens.append({
                "text": raw,
                "is_word": False,
                "word": None,
                "is_difficult": False,
                "definition": None,
                "pos": None,
            })
    return tokens


def find_difficult_words(text: str) -> List[Dict]:
    """Return list of difficult words found in the text.

    Each item: {"word": str, "definition": str, "pos": str, "lower": str}
    Case-insensitive; each word appears only once in the result.
    """
    found: Dict[str, Dict] = {}
    for match in re.finditer(r"[a-zA-Z]+(?:'[a-zA-Z]+)?", text):
        w = match.group(0)
        key = w.lower()
        entry = _lookup(key)
        if entry is not None and key not in found:
            defn, pos = entry
            found[key] = {"word": w, "lower": key, "definition": defn, "pos": pos}
    return list(found.values())


def find_difficult_words_sorted(text: str) -> List[Dict]:
    """Like find_difficult_words but sorted by first appearance in text."""
    result = find_difficult_words(text)
    # Sort by position in text (case-insensitive find)
    lower_text = text.lower()
    result.sort(key=lambda item: lower_text.index(item["lower"]))
    return result
