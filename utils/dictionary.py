# -*- coding: utf-8 -*-
"""
词典API工具 - 获取单词的中文含义和音标
使用有道词典API或免费词典API
"""

import urllib.request
import urllib.parse
import urllib.error
import json
import ssl
from typing import Dict, Optional


class DictionaryAPI:
    """词典API处理器"""
    
    def __init__(self):
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        self.timeout = 10
    
    def lookup_word(self, word: str) -> Optional[Dict]:
        """查询单词信息"""
        word = word.strip().lower()
        if not word:
            return None
        
        # 尝试有道词典API（有中文释义）
        result = self._lookup_youdao(word)
        if result:
            return result
        
        # 备用：Free Dictionary API（英文释义）
        result = self._lookup_free_dictionary_api(word)
        if result:
            return result
        
        return None
    
    def _lookup_youdao(self, word: str) -> Optional[Dict]:
        """
        使用有道词典API查询单词（支持中文释义）
        """
        try:
            # 有道词典API
            url = f"https://dict.youdao.com/suggest?num=1&doctype=json&q={urllib.parse.quote(word)}"
            
            request = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                }
            )
            
            with urllib.request.urlopen(request, timeout=self.timeout, context=self.ssl_context) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            if data and data.get('data') and data['data'].get('entries'):
                entries = data['data']['entries']
                if entries and len(entries) > 0:
                    entry = entries[0]
                    explain = entry.get('explain', '')
                    
                    if explain:
                        # 解析释义，格式通常是 "word [phonetic] meaning"
                        parts = explain.split(' ', 1)
                        meaning = parts[1] if len(parts) > 1 else explain
                        
                        return {
                            'word': word,
                            'meaning': meaning,
                            'phonetic': '',
                            'part_of_speech': '',
                            'example': '',
                            'source': 'youdao'
                        }
            
            return None
            
        except Exception as e:
            print(f"有道词典查询失败: {e}")
            return None
    
    def _lookup_free_dictionary_api(self, word: str) -> Optional[Dict]:
        """使用Free Dictionary API查询"""
        api_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        
        try:
            request = urllib.request.Request(
                api_url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/json'
                }
            )
            
            with urllib.request.urlopen(request, timeout=self.timeout, context=self.ssl_context) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            if not data or not isinstance(data, list):
                return None
            
            entry = data[0]
            
            result = {
                'word': word,
                'meaning': '',
                'phonetic': '',
                'part_of_speech': '',
                'example': '',
            }
            
            # 获取音标
            result['phonetic'] = entry.get('phonetic', '')
            if not result['phonetic']:
                phonetics = entry.get('phonetics', [])
                for p in phonetics:
                    if p.get('text'):
                        result['phonetic'] = p['text']
                        break
            
            # 获取释义（注意：这是英文释义）
            meanings = entry.get('meanings', [])
            all_definitions = []
            
            for meaning in meanings:
                pos = meaning.get('partOfSpeech', '')
                definitions = meaning.get('definitions', [])
                
                for def_item in definitions:
                    definition = def_item.get('definition', '')
                    example = def_item.get('example', '')
                    
                    if definition:
                        all_definitions.append({
                            'part_of_speech': pos,
                            'definition': definition,
                            'example': example
                        })
                        
                        if example and not result['example']:
                            result['example'] = example
            
            if all_definitions:
                result['meaning'] = '; '.join([
                    f"[{d['part_of_speech']}] {d['definition']}" 
                    for d in all_definitions[:2]
                ])
                result['part_of_speech'] = all_definitions[0]['part_of_speech']
            
            result['source'] = 'free_dict'
            return result
            
        except Exception as e:
            print(f"Free Dictionary查询失败: {e}")
            return None


class LocalDictionary:
    """本地常用词词典（带中文释义）"""
    
    COMMON_WORDS = {
        "the": "art. 这；那（定冠词）",
        "be": "v. 是；存在",
        "to": "prep. 到；向",
        "of": "prep. ...的",
        "and": "conj. 和；与",
        "a": "art. 一个",
        "in": "prep. 在...里面",
        "that": "pron. 那个",
        "have": "v. 有；拥有",
        "it": "pron. 它",
        "for": "prep. 为了",
        "not": "adv. 不",
        "on": "prep. 在...上",
        "with": "prep. 和...一起",
        "he": "pron. 他",
        "as": "conj. 如同；作为",
        "you": "pron. 你",
        "do": "v. 做",
        "at": "prep. 在",
        "this": "pron. 这个",
        "but": "conj. 但是",
        "his": "pron. 他的",
        "by": "prep. 由；通过",
        "from": "prep. 来自",
        "they": "pron. 他们",
        "we": "pron. 我们",
        "say": "v. 说",
        "her": "pron. 她的",
        "she": "pron. 她",
        "or": "conj. 或者",
        "an": "art. 一个",
        "will": "v. 将；会",
        "my": "pron. 我的",
        "one": "num. 一；一个",
        "all": "adj. 所有的",
        "would": "v. 将要；愿意",
        "there": "adv. 那里",
        "their": "pron. 他们的",
        "what": "pron. 什么",
        "so": "adv. 如此；所以",
        "up": "adv. 向上",
        "out": "adv. 出去",
        "if": "conj. 如果",
        "about": "prep. 关于",
        "who": "pron. 谁",
        "get": "v. 得到；获得",
        "which": "pron. 哪一个",
        "go": "v. 去",
        "me": "pron. 我（宾格）",
        "when": "adv. 什么时候",
        "make": "v. 制作；使",
        "can": "v. 能；可以",
        "like": "v. 喜欢；prep. 像",
        "time": "n. 时间",
        "no": "adv. 不",
        "just": "adv. 只是；刚刚",
        "him": "pron. 他（宾格）",
        "know": "v. 知道",
        "take": "v. 拿；取",
        "people": "n. 人们",
        "into": "prep. 进入",
        "year": "n. 年",
        "your": "pron. 你的",
        "good": "adj. 好的",
        "some": "adj. 一些",
        "could": "v. 能；可以",
        "them": "pron. 他们（宾格）",
        "see": "v. 看见",
        "other": "adj. 其他的",
        "than": "conj. 比",
        "then": "adv. 然后",
        "now": "adv. 现在",
        "look": "v. 看",
        "only": "adv. 只有；仅仅",
        "come": "v. 来",
        "its": "pron. 它的",
        "over": "prep. 超过；在...上方",
        "think": "v. 思考；认为",
        "also": "adv. 也",
        "back": "adv. 回来",
        "after": "prep. 在...之后",
        "use": "v. 使用",
        "two": "num. 二",
        "how": "adv. 如何",
        "our": "pron. 我们的",
        "work": "n./v. 工作",
        "first": "adj. 第一的",
        "well": "adv. 很好",
        "way": "n. 方式；道路",
        "even": "adv. 甚至",
        "new": "adj. 新的",
        "want": "v. 想要",
        "because": "conj. 因为",
        "any": "adj. 任何",
        "these": "pron. 这些",
        "give": "v. 给",
        "day": "n. 天；白天",
        "most": "adj. 最多的",
        "us": "pron. 我们（宾格）",
        "research": "n./v. 研究",
        "researcher": "n. 研究员",
        "study": "n./v. 学习；研究",
        "university": "n. 大学",
        "technical": "adj. 技术的",
        "develop": "v. 开发；发展",
        "system": "n. 系统",
        "technology": "n. 技术",
        "computer": "n. 计算机",
        "science": "n. 科学",
        "scientist": "n. 科学家",
        "method": "n. 方法",
        "data": "n. 数据",
        "information": "n. 信息",
        "process": "n./v. 过程；处理",
        "model": "n. 模型",
        "algorithm": "n. 算法",
        "learning": "n. 学习",
        "machine": "n. 机器",
        "artificial": "adj. 人工的",
        "intelligence": "n. 智能",
        "network": "n. 网络",
        "language": "n. 语言",
        "natural": "adj. 自然的",
        "application": "n. 应用",
        "program": "n. 程序",
        "software": "n. 软件",
        "digital": "adj. 数字的",
        "electronic": "adj. 电子的",
        "device": "n. 设备",
        "tool": "n. 工具",
        "platform": "n. 平台",
        "service": "n. 服务",
        "internet": "n. 互联网",
        "online": "adj. 在线的",
        "web": "n. 网络",
        "mobile": "adj. 移动的",
        "phone": "n. 电话",
        "smart": "adj. 智能的",
        "function": "n. 功能",
        "feature": "n. 特征；功能",
        "design": "n./v. 设计",
        "create": "v. 创造",
        "build": "v. 构建",
        "test": "n./v. 测试",
        "result": "n. 结果",
        "report": "n./v. 报告",
        "analysis": "n. 分析",
        "project": "n. 项目",
        "team": "n. 团队",
        "company": "n. 公司",
        "business": "n. 商业；业务",
        "market": "n. 市场",
        "industry": "n. 工业；行业",
        "production": "n. 生产",
        "development": "n. 发展；开发",
        "management": "n. 管理",
        "strategy": "n. 策略",
        "solution": "n. 解决方案",
        "problem": "n. 问题",
        "challenge": "n. 挑战",
        "opportunity": "n. 机会",
        "future": "n. 未来",
        "innovation": "n. 创新",
        "change": "n./v. 变化",
        "growth": "n. 增长",
        "success": "n. 成功",
        "quality": "n. 质量",
        "performance": "n. 性能；表现",
        "efficiency": "n. 效率",
        "speed": "n. 速度",
        "power": "n. 力量；权力",
        "energy": "n. 能量",
        "resource": "n. 资源",
        "environment": "n. 环境",
        "sustainable": "adj. 可持续的",
        "global": "adj. 全球的",
        "international": "adj. 国际的",
        "world": "n. 世界",
        "country": "n. 国家",
        "city": "n. 城市",
        "area": "n. 区域",
        "region": "n. 地区",
        "community": "n. 社区",
        "society": "n. 社会",
        "culture": "n. 文化",
        "education": "n. 教育",
        "knowledge": "n. 知识",
        "skill": "n. 技能",
        "experience": "n. 经验",
        "training": "n. 训练",
        "course": "n. 课程",
        "lesson": "n. 课程；教训",
        "class": "n. 班级；阶级",
        "student": "n. 学生",
        "teacher": "n. 教师",
        "professor": "n. 教授",
        "expert": "n. 专家",
        "professional": "n./adj. 专业人员；专业的",
    }
    
    @classmethod
    def lookup(cls, word: str) -> Optional[str]:
        return cls.COMMON_WORDS.get(word.lower())


def get_word_info(word: str) -> Dict:
    """获取单词信息"""
    word = word.strip().lower()
    
    # 先查本地词典
    local_meaning = LocalDictionary.lookup(word)
    if local_meaning:
        return {
            'word': word,
            'meaning': local_meaning,
            'phonetic': '',
            'part_of_speech': '',
            'example': '',
            'source': 'local'
        }
    
    # 查在线API
    api = DictionaryAPI()
    result = api.lookup_word(word)
    if result:
        return result
    
    return {
        'word': word,
        'meaning': '',
        'phonetic': '',
        'part_of_speech': '',
        'example': '',
        'source': 'none'
    }


dictionary_api = DictionaryAPI()
