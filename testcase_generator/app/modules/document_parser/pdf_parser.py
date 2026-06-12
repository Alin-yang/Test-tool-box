"""
PDF文档解析器
"""
import PyPDF2
from typing import List, Dict


class PDFParser:
    """解析PDF文档"""

    @staticmethod
    def parse(file_path: str) -> Dict:
        result = {'text': [], 'pages': [], 'metadata': {}}
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            result['metadata'] = {
                'pages': len(reader.pages),
                'title': reader.metadata.get('/Title', ''),
                'author': reader.metadata.get('/Author', '')
            }
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    result['pages'].append({'page_num': page_num + 1, 'text': text})
                    result['text'].append(text)
        return result

    @staticmethod
    def extract_requirements(text_list: List[str]) -> List[Dict]:
        requirements = []
        keywords = ['需求', '功能', '模块', '应该', '需要', '要求', '支持', '提供']
        for text in text_list:
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                for keyword in keywords:
                    if keyword in line:
                        requirements.append({'type': 'functional', 'description': line, 'keyword': keyword})
                        break
        return requirements

    @staticmethod
    def extract_api_info(text_list: List[str]) -> List[Dict]:
        apis = []
        api_keywords = ['接口', 'API', '请求', '响应', 'URL', 'POST', 'GET', 'PUT', 'DELETE']
        for text in text_list:
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                for keyword in api_keywords:
                    if keyword in line.upper() if keyword == 'API' else keyword in line:
                        apis.append({'description': line, 'detected_keyword': keyword})
                        break
        return apis
