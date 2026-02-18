# -*- coding: utf-8 -*-
"""
词典API工具 - 获取单词的含义和音标
使用免费的词典API获取单词信息
"""

import urllib.request
import urllib.error
import json
import ssl
from typing import Dict, Optional, List


class DictionaryAPI:
    """词典API处理器"""
    
    def __init__(self):
        """初始化词典API"""
        # 创建SSL上下文，忽略证书验证（某些网络环境下需要）
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        
        # 请求超时时间（秒）
        self.timeout = 10
    
    def lookup_word(self, word: str) -> Optional[Dict]:
        """
        查询单词信息
        
        参数:
            word: 要查询的单词
        
        返回:
            Dict: 单词信息，包含meaning, phonetic, part_of_speech, example等
                  如果查询失败返回None
        """
        word = word.strip().lower()
        if not word:
            return None
        
        # 尝试使用Free Dictionary API
        result = self._lookup_free_dictionary_api(word)
        if result:
            return result
        
        # 如果第一个API失败，可以尝试其他API
        # result = self._lookup_other_api(word)
        
        return None
    
    def _lookup_free_dictionary_api(self, word: str) -> Optional[Dict]:
        """
        使用Free Dictionary API查询单词
        API文档: https://dictionaryapi.dev/
        
        参数:
            word: 要查询的单词
        
        返回:
            Dict: 单词信息或None
        """
        api_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        
        try:
            # 创建请求
            request = urllib.request.Request(
                api_url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/json'
                }
            )
            
            # 发送请求
            with urllib.request.urlopen(request, timeout=self.timeout, context=self.ssl_context) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            if not data or not isinstance(data, list):
                return None
            
            # 解析返回的数据
            entry = data[0]
            
            result = {
                'word': word,
                'meaning': '',
                'phonetic': '',
                'part_of_speech': '',
                'example': '',
                'definitions': []
            }
            
            # 获取音标
            result['phonetic'] = entry.get('phonetic', '')
            if not result['phonetic']:
                # 尝试从phonetics数组中获取
                phonetics = entry.get('phonetics', [])
                for p in phonetics:
                    if p.get('text'):
                        result['phonetic'] = p['text']
                        break
            
            # 获取释义
            meanings = entry.get('meanings', [])
            all_definitions = []
            
            for meaning in meanings:
                pos = meaning.get('partOfSpeech', '')
                definitions = meaning.get('definitions', [])
                
                for def_item in definitions:
                    definition = def_item.get('definition', '')
                    example = def_item.get('example', '')
                    
                    if definition:
                        def_text = f"[{pos}] {definition}"
                        all_definitions.append({
                            'part_of_speech': pos,
                            'definition': definition,
                            'example': example
                        })
                        
                        # 如果还没有例句，保存这个
                        if example and not result['example']:
                            result['example'] = example
            
            # 合并所有释义
            if all_definitions:
                # 取前3个释义
                result['definitions'] = all_definitions[:3]
                result['meaning'] = '; '.join([
                    f"[{d['part_of_speech']}] {d['definition']}" 
                    for d in all_definitions[:3]
                ])
                result['part_of_speech'] = all_definitions[0]['part_of_speech']
            
            return result
            
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"单词 '{word}' 未找到")
            else:
                print(f"HTTP错误: {e.code}")
            return None
        except urllib.error.URLError as e:
            print(f"网络错误: {e.reason}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            return None
        except Exception as e:
            print(f"查询错误: {e}")
            return None
    
    def lookup_multiple_words(self, words: List[str]) -> Dict[str, Dict]:
        """
        批量查询单词
        
        参数:
            words: 单词列表
        
        返回:
            Dict: {word: word_info} 字典
        """
        results = {}
        for word in words:
            result = self.lookup_word(word)
            if result:
                results[word] = result
        return results
    
    def get_simple_meaning(self, word: str) -> str:
        """
        获取单词的简单中文释义
        注意: Free Dictionary API返回的是英文释义
        如果需要中文释义，需要使用其他API或本地词典
        
        参数:
            word: 要查询的单词
        
        返回:
            str: 释义字符串
        """
        result = self.lookup_word(word)
        if result and result.get('meaning'):
            return result['meaning']
        return ""


class LocalDictionary:
    """
    本地词典类 - 存储常用单词的中文释义
    用于离线查询或作为在线API的补充
    """
    
    # 常用单词的中文释义（示例）
    COMMON_WORDS = {
        "the": "det. 这；那",
        "be": "v. 是；存在",
        "to": "prep. 到；向",
        "of": "prep. ...的",
        "and": "conj. 和；与",
        "a": "art. 一个",
        "in": "prep. 在...里面",
        "that": "pron. 那个",
        "have": "v. 有",
        "i": "pron. 我",
        "it": "pron. 它",
        "for": "prep. 为了",
        "not": "adv. 不",
        "on": "prep. 在...上",
        "with": "prep. 和...一起",
        "he": "pron. 他",
        "as": "conj. 如同",
        "you": "pron. 你",
        "do": "v. 做",
        "at": "prep. 在",
        "this": "pron. 这个",
        "but": "conj. 但是",
        "his": "pron. 他的",
        "by": "prep. 由",
        "from": "prep. 从",
        "they": "pron. 他们",
        "we": "pron. 我们",
        "say": "v. 说",
        "her": "pron. 她的",
        "she": "pron. 她",
        "or": "conj. 或者",
        "an": "art. 一个",
        "will": "v. 将；意志",
        "my": "pron. 我的",
        "one": "num. 一",
        "all": "adj. 所有的",
        "would": "v. 将要",
        "there": "adv. 那里",
        "their": "pron. 他们的",
        "what": "pron. 什么",
        "so": "adv. 如此",
        "up": "adv. 向上",
        "out": "adv. 出去",
        "if": "conj. 如果",
        "about": "prep. 关于",
        "who": "pron. 谁",
        "get": "v. 得到",
        "which": "pron. 哪一个",
        "go": "v. 去",
        "me": "pron. 我",
        "when": "adv. 什么时候",
        "make": "v. 制作",
        "can": "v. 能",
        "like": "v. 喜欢",
        "time": "n. 时间",
        "no": "adv. 不",
        "just": "adv. 只是",
        "him": "pron. 他",
        "know": "v. 知道",
        "take": "v. 拿",
        "people": "n. 人们",
        "into": "prep. 进入",
        "year": "n. 年",
        "your": "pron. 你的",
        "good": "adj. 好的",
        "some": "adj. 一些",
        "could": "v. 能",
        "them": "pron. 他们",
        "see": "v. 看见",
        "other": "adj. 其他的",
        "than": "conj. 比",
        "then": "adv. 然后",
        "now": "adv. 现在",
        "look": "v. 看",
        "only": "adv. 只有",
        "come": "v. 来",
        "its": "pron. 它的",
        "over": "prep. 超过",
        "think": "v. 思考",
        "also": "adv. 也",
        "back": "adv. 返回",
        "after": "prep. 在...之后",
        "use": "v. 使用",
        "two": "num. 二",
        "how": "adv. 如何",
        "our": "pron. 我们的",
        "work": "n./v. 工作",
        "first": "adj. 第一的",
        "well": "adv. 很好",
        "way": "n. 方式",
        "even": "adv. 甚至",
        "new": "adj. 新的",
        "want": "v. 想要",
        "because": "conj. 因为",
        "any": "adj. 任何",
        "these": "pron. 这些",
        "give": "v. 给",
        "day": "n. 天",
        "most": "adj. 最多的",
        "us": "pron. 我们",
    }
    
    @classmethod
    def lookup(cls, word: str) -> Optional[str]:
        """
        查询本地词典
        
        参数:
            word: 要查询的单词
        
        返回:
            str: 释义或None
        """
        return cls.COMMON_WORDS.get(word.lower())


def get_word_info(word: str) -> Dict:
    """
    获取单词信息的便捷函数
    优先使用本地词典，然后尝试在线API
    
    参数:
        word: 要查询的单词
    
    返回:
        Dict: 单词信息
    """
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
        result['source'] = 'api'
        return result
    
    return {
        'word': word,
        'meaning': '',
        'phonetic': '',
        'part_of_speech': '',
        'example': '',
        'source': 'none'
    }


# 创建全局词典API实例
dictionary_api = DictionaryAPI()
