"""
Markdown文档解析器 - 增强版
支持从接口文档提取请求参数示例
"""
import markdown
from bs4 import BeautifulSoup
from typing import List, Dict
import json
import re


class MarkdownParser:
    """解析Markdown文档 - 增强版"""

    @staticmethod
    def parse(file_path: str) -> Dict:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        html = markdown.markdown(content, extensions=['tables', 'fenced_code'])
        result = {'raw_text': content, 'html': html, 'headings': [], 'paragraphs': [], 'code_blocks': [], 'tables': [], 'json_blocks': []}
        soup = BeautifulSoup(html, 'html.parser')

        for i, tag in enumerate(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])):
            level = int(tag.name[1])
            result['headings'].append({'level': level, 'text': tag.get_text(), 'index': i})

        for tag in soup.find_all('p'):
            text = tag.get_text().strip()
            if text:
                result['paragraphs'].append(text)

        for tag in soup.find_all('pre'):
            code = tag.get_text().strip()
            if code:
                result['code_blocks'].append(code)
                # 尝试解析JSON
                try:
                    json_data = json.loads(code)
                    result['json_blocks'].append({'type': 'json', 'content': json_data})
                except:
                    pass

        for tag in soup.find_all('table'):
            table_data = []
            for row in tag.find_all('tr'):
                row_data = [cell.get_text().strip() for cell in row.find_all(['th', 'td'])]
                table_data.append(row_data)
            result['tables'].append(table_data)
        return result

    @staticmethod
    def extract_requirements(paragraphs: List[str], tables: List[List[List[str]]] = None) -> List[Dict]:
        """智能提取需求文档中的需求点"""
        requirements = []
        
        # 需求类型识别模式
        requirement_patterns = {
            'functional': [
                r'应该.*(能够|可以|实现|支持)',
                r'需要.*(实现|完成|支持)',
                r'必须.*(实现|完成|支持)',
                r'系统.*(应|需|必须)',
                r'功能.*(描述|说明|要求)',
                r'模块.*(功能|需求)',
                r'用户.*(可以|能够|应该)',
                r'提供.*(功能|服务|接口)',
                r'支持.*(格式|类型|方式)',
                r'实现.*(功能|需求|特性)',
            ],
            'performance': [
                r'响应时间.*(小于|不超过|低于)',
                r'性能.*(要求|指标)',
                r'并发.*(用户|请求)',
                r'TPS.*(达到|要求)',
                r'吞吐量.*(要求|指标)',
                r'延迟.*(小于|不超过)',
            ],
            'security': [
                r'安全.*(要求|措施|策略)',
                r'权限.*(控制|管理)',
                r'加密.*(传输|存储)',
                r'认证.*(机制|方式)',
                r'授权.*(管理|控制)',
                r'防止.*(攻击|泄露)',
            ],
            'ui': [
                r'界面.*(设计|布局|显示)',
                r'页面.*(展示|布局|设计)',
                r'样式.*(要求|规范)',
                r'交互.*(设计|方式)',
                r'导航.*(设计|结构)',
            ],
            'data': [
                r'数据.*(存储|格式|类型)',
                r'数据库.*(设计|要求)',
                r'字段.*(定义|要求)',
                r'表.*(设计|结构)',
            ]
        }
        
        # 优先级识别模式
        priority_patterns = {
            'P0': [r'必须.*实现', r'核心.*功能', r'关键.*需求', r'不实现.*无法', r'MUST'],
            'P1': [r'重要.*功能', r'主要.*需求', r'SHOULD', r'建议.*实现'],
            'P2': [r'可选.*功能', r'次要.*需求', r'MAY', r'可以.*后续'],
        }
        
        # 从段落提取需求
        for idx, para in enumerate(paragraphs):
            # 跳过空段落
            if not para or len(para.strip()) < 10:
                continue
            
            # 识别需求类型
            req_type = 'functional'
            for type_name, patterns in requirement_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, para, re.IGNORECASE):
                        req_type = type_name
                        break
                if req_type != 'functional':
                    break
            
            # 识别优先级
            priority = 'P2'
            for p, patterns in priority_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, para, re.IGNORECASE):
                        priority = p
                        break
                if priority != 'P2':
                    break
            
            # 提取需求描述
            # 尝试从段落中提取更精确的需求描述
            description = para
            
            # 清理描述（去除标点和多余空格）
            description = re.sub(r'[。，、；：！？]+$', '', description.strip())
            
            # 添加需求
            requirements.append({
                'id': f'REQ-{idx+1:04d}',
                'type': req_type,
                'description': description,
                'priority': priority,
                'source': 'paragraph'
            })
        
        # 从表格提取需求
        if tables:
            for table in tables:
                # 检查表格是否包含需求相关内容
                header_row = table[0] if table else []
                has_requirement_col = any(
                    any(keyword in str(cell) for keyword in ['需求', '功能', '说明', '描述', '要求'])
                    for cell in header_row
                )
                
                if has_requirement_col:
                    # 解析表格行
                    for row_idx, row in enumerate(table[1:], 1):
                        if len(row) >= 2:
                            # 尝试找到需求描述列
                            req_desc = ''
                            req_priority = 'P2'
                            req_type = 'functional'
                            
                            for cell in row:
                                cell_str = str(cell).strip()
                                if cell_str:
                                    # 检查是否为优先级
                                    if cell_str in ['P0', 'P1', 'P2', '高', '中', '低']:
                                        priority_map = {'高': 'P0', '中': 'P1', '低': 'P2'}
                                        req_priority = priority_map.get(cell_str, cell_str)
                                    # 检查是否为类型
                                    elif cell_str in ['功能', '性能', '安全', 'UI', '数据']:
                                        type_map = {'功能': 'functional', '性能': 'performance', 
                                                    '安全': 'security', 'UI': 'ui', '数据': 'data'}
                                        req_type = type_map.get(cell_str, 'functional')
                                    # 否则作为描述
                                    elif len(cell_str) > 5:
                                        req_desc = cell_str
                            
                            if req_desc:
                                requirements.append({
                                    'id': f'REQ-TBL-{row_idx:03d}',
                                    'type': req_type,
                                    'description': req_desc,
                                    'priority': req_priority,
                                    'source': 'table'
                                })
        
        # 去重
        seen = set()
        unique_reqs = []
        for req in requirements:
            key = req['description'][:200]
            if key not in seen:
                seen.add(key)
                unique_reqs.append(req)
        
        return unique_reqs

    @staticmethod
    def extract_api_info(paragraphs: List[str], code_blocks: List[str]) -> List[Dict]:
        apis = []
        api_keywords = ['接口', 'API', '请求', '响应', 'URL', 'POST', 'GET', 'PUT', 'DELETE']
        
        # 按段落分组提取API信息
        current_api = None
        current_code_block = None
        
        # 遍历所有内容，包括段落和代码块
        for i, content in enumerate(paragraphs + code_blocks):
            # 检测HTTP方法
            method = MarkdownParser._detect_http_method(content)
            
            if method:
                # 保存当前API
                if current_api:
                    # 如果有未匹配的代码块，尝试作为请求体
                    if current_code_block:
                        try:
                            json_data = json.loads(current_code_block)
                            if isinstance(json_data, dict):
                                current_api['body'] = json_data
                        except:
                            pass
                        current_code_block = None
                    apis.append(current_api)
                
                current_api = {
                    'description': content,
                    'method': method,
                    'url': MarkdownParser._extract_url(content),
                    'params': {},
                    'body': {},
                    'headers': {},
                    'detected_keyword': method
                }
            elif current_api:
                # 如果是代码块，尝试作为请求体
                if content.strip().startswith('{') and content.strip().endswith('}'):
                    try:
                        json_data = json.loads(content)
                        if isinstance(json_data, dict):
                            current_api['body'] = json_data
                        elif isinstance(json_data, list):
                            current_api['body'] = json_data
                    except:
                        # 尝试修复JSON格式
                        try:
                            fixed_content = content.replace("'", "\"").replace('\\n', '').strip()
                            json_data = json.loads(fixed_content)
                            if isinstance(json_data, dict):
                                current_api['body'] = json_data
                        except:
                            pass
                
                # 尝试提取参数
                params = MarkdownParser._extract_params(content)
                if params:
                    current_api['params'].update(params)
                
                # 尝试提取headers
                headers = MarkdownParser._extract_headers(content)
                if headers:
                    current_api['headers'].update(headers)
            
            # 检测到新的API描述（非HTTP方法开头）
            elif not method:
                for keyword in api_keywords:
                    if keyword in content:
                        if current_api and current_api.get('url'):
                            apis.append(current_api)
                        current_api = {
                            'description': content,
                            'method': MarkdownParser._detect_http_method(content),
                            'url': MarkdownParser._extract_url(content),
                            'params': {},
                            'body': {},
                            'headers': {},
                            'detected_keyword': keyword
                        }
                        break
        
        # 添加最后一个API
        if current_api:
            apis.append(current_api)
        
        return apis

    @staticmethod
    def _detect_http_method(text: str) -> str:
        """检测HTTP方法"""
        methods = ['POST', 'GET', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
        text_upper = text.upper()
        for method in methods:
            if method in text_upper:
                return method
        return None

    @staticmethod
    def _extract_url(text: str) -> str:
        """提取URL"""
        url_patterns = [
            r'https?://[^\s<>"\']+',
            r'/api/[a-zA-Z0-9/_-]+',
            r'/[a-zA-Z0-9/_-]+',
        ]
        for pattern in url_patterns:
            urls = re.findall(pattern, text)
            if urls:
                return urls[0]
        return ''

    @staticmethod
    def _extract_params(text: str) -> Dict:
        """提取URL参数或查询参数"""
        params = {}
        
        # 从URL提取query参数
        match = re.search(r'\?(.*)', text)
        if match:
            query_str = match.group(1)
            for pair in query_str.split('&'):
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    params[key.strip()] = value.strip()
        
        # 从文本提取参数定义
        param_pattern = r'(参数|params|query|Query)\s*[：:]?\s*\{?([^\}]*)\}?'
        match = re.search(param_pattern, text, re.IGNORECASE)
        if match:
            param_str = match.group(2)
            for param in param_str.split(','):
                param = param.strip()
                if param:
                    if ':' in param:
                        key, value = param.split(':', 1)
                        params[key.strip()] = value.strip()
                    else:
                        params[param] = ''
        
        return params

    @staticmethod
    def _extract_request_body(text: str) -> Dict:
        """提取请求体JSON"""
        # 尝试直接解析JSON
        try:
            return json.loads(text)
        except:
            pass
        
        # 从文本中提取JSON块
        json_pattern = r'\{[\s\S]*\}'
        matches = re.findall(json_pattern, text)
        for match in matches:
            try:
                return json.loads(match)
            except:
                pass
        
        # 尝试解析key-value格式
        body = {}
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if ':' in line and not line.startswith('//') and not line.startswith('#'):
                parts = line.split(':', 1)
                key = parts[0].strip().strip('"').strip("'")
                value = parts[1].strip().strip('"').strip("'").strip(',')
                # 尝试转换类型
                try:
                    value = int(value)
                except:
                    try:
                        value = float(value)
                    except:
                        if value.lower() == 'true':
                            value = True
                        elif value.lower() == 'false':
                            value = False
                        elif value.lower() == 'null':
                            value = None
                body[key] = value
        
        return body if body else {}

    @staticmethod
    def _extract_headers(text: str) -> Dict:
        """提取请求头"""
        headers = {}
        header_patterns = [
            r'(Content-Type|Authorization|Token|token|X-.*?):\s*([^\s]+)',
            r'(headers|Headers)\s*[：:]?\s*\{?([^\}]*)\}?'
        ]
        
        for pattern in header_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                key = match[0].strip()
                value = match[1].strip() if len(match) > 1 else ''
                headers[key] = value
        
        return headers