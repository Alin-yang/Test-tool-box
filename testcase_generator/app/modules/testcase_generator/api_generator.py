"""
API测试用例生成器 - 优化版
支持更智能的用例标题生成和环境配置
"""
from typing import List, Dict
import re


class APIGenerator:
    """生成API接口测试用例 - 优化版"""

    HTTP_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
    CONTENT_TYPES = ['application/json', 'application/x-www-form-urlencoded', 'multipart/form-data', 'text/plain']
    COMMON_STATUS_CODES = {
        200: '成功',
        201: '创建成功',
        204: '无内容',
        400: '请求参数错误',
        401: '未授权',
        403: '禁止访问',
        404: '资源不存在',
        405: '方法不允许',
        408: '请求超时',
        409: '资源冲突',
        415: '不支持的内容类型',
        422: '参数验证失败',
        500: '服务器内部错误',
        502: '网关错误',
        503: '服务不可用',
        504: '网关超时'
    }

    # 常见API参数类型及其测试规则
    PARAM_TYPES = {
        'id': {
            'valid': ['1', '100', '999999'],
            'invalid': ['0', '-1', 'abc', '', 'null', '999999999999999']
        },
        'name': {
            'valid': ['测试名称', 'TestName', '中文English'],
            'invalid': ['', '  ', '!@#$%', '超长名称超长名称超长名称超长名称超长名称超长名称']
        },
        'email': {
            'valid': ['test@example.com', 'user@domain.cn'],
            'invalid': ['', 'test', 'test@', '@example.com', 'test@example']
        },
        'phone': {
            'valid': ['13812345678', '18600001111'],
            'invalid': ['', '12345', '12345678901234', 'abc12345678']
        },
        'amount': {
            'valid': ['100', '99.99', '0.01'],
            'invalid': ['', '-100', '0', 'abc', '100.999']
        },
        'page': {
            'valid': ['1', '10', '100'],
            'invalid': ['0', '-1', '', 'abc', '999999999']
        },
        'size': {
            'valid': ['10', '20', '50'],
            'invalid': ['0', '-1', '', 'abc', '1000']
        },
        'status': {
            'valid': ['0', '1', '2'],
            'invalid': ['', '-1', 'abc', '999']
        },
        'date': {
            'valid': ['2024-01-01', '2024-12-31'],
            'invalid': ['', '20240101', '2024-13-01', '2024-01-32']
        }
    }

    # 测试场景类型描述映射
    SCENARIO_TYPES = {
        'normal': {'name': '正常请求', 'desc': '验证接口正常响应', 'priority': 'P0'},
        'invalid_method': {'name': '方法不允许', 'desc': '验证HTTP方法限制', 'priority': 'P2'},
        'unauthorized': {'name': '未授权', 'desc': '验证未登录访问控制', 'priority': 'P0'},
        'param_valid': {'name': '参数有效', 'desc': '验证有效参数', 'priority': 'P1'},
        'param_invalid': {'name': '参数无效', 'desc': '验证无效参数', 'priority': 'P2'},
        'security': {'name': '安全测试', 'desc': '验证安全防护', 'priority': 'P0'},
        'performance': {'name': '性能测试', 'desc': '验证性能指标', 'priority': 'P2'},
    }

    @staticmethod
    def generate(api_info: List[Dict], base_url: str = '') -> List[Dict]:
        """
        根据接口信息生成全面的API测试用例
        :param api_info: 接口信息列表（包含解析器提取的params、body、headers）
        :param base_url: 基础URL（测试环境地址）
        """
        all_test_cases = []
        global_index = 1

        for api in api_info:
            desc = api.get('description', '')
            
            # 分析接口信息 - 使用解析器提取的参数
            analysis = APIGenerator._analyze_api(desc, base_url)
            
            # 合并解析器提取的参数
            if api.get('params'):
                # 解析器返回的是 Dict，需要转换为 List[Dict]
                parser_params = api.get('params', {})
                for key, value in parser_params.items():
                    exists = False
                    for p in analysis['params']:
                        if p.get('name') == key:
                            exists = True
                            break
                    if not exists:
                        analysis['params'].append({
                            'name': key,
                            'type': 'string',
                            'required': True,
                            'description': f'{key}参数',
                            'example': value
                        })
            if api.get('body'):
                analysis['body'] = api['body']
            if api.get('headers'):
                analysis['headers'] = api['headers']
            
            # 生成基础API测试用例
            base_cases = APIGenerator._generate_base_api_cases(analysis, global_index)
            all_test_cases.extend(base_cases)
            global_index += len(base_cases)
            
            # 生成参数测试用例
            param_cases = APIGenerator._generate_param_cases(analysis, global_index)
            all_test_cases.extend(param_cases)
            global_index += len(param_cases)
            
            # 生成安全测试用例
            security_cases = APIGenerator._generate_security_cases(analysis, global_index)
            all_test_cases.extend(security_cases)
            global_index += len(security_cases)
            
            # 生成性能测试用例
            perf_cases = APIGenerator._generate_performance_cases(analysis, global_index)
            all_test_cases.extend(perf_cases)
            global_index += len(perf_cases)

        return APIGenerator._sort_by_priority(all_test_cases)

    @staticmethod
    def _analyze_api(description: str, base_url: str = '') -> Dict:
        """分析接口描述，提取关键信息"""
        url = APIGenerator._extract_url(description)
        # 如果提供了基础URL，拼接完整URL
        if base_url and not url.startswith('http'):
            url = base_url.rstrip('/') + url
        
        analysis = {
            'method': APIGenerator._detect_method(description),
            'url': url,
            'base_url': base_url,
            'path': APIGenerator._extract_path(url),
            'params': APIGenerator._extract_params(description),
            'body': {},
            'headers': {},
            'description': description,
            'requires_auth': APIGenerator._requires_auth(description),
            'content_type': APIGenerator._detect_content_type(description),
            'api_name': APIGenerator._extract_api_name(description, url)
        }
        return analysis

    @staticmethod
    def _detect_method(text: str) -> str:
        """检测HTTP方法"""
        text_upper = text.upper()
        for method in APIGenerator.HTTP_METHODS:
            if method in text_upper:
                return method
        if any(kw in text for kw in ['查询', '获取', '列表', '详情', 'search', 'get', 'list']):
            return 'GET'
        if any(kw in text for kw in ['添加', '创建', '新增', 'add', 'create', 'insert']):
            return 'POST'
        if any(kw in text for kw in ['修改', '更新', '编辑', 'update', 'edit', 'modify']):
            return 'PUT'
        if any(kw in text for kw in ['删除', '移除', 'delete', 'remove']):
            return 'DELETE'
        return 'POST'

    @staticmethod
    def _extract_url(text: str) -> str:
        """提取URL路径"""
        url_patterns = [
            r'https?://[^\s<>"\']+',
            r'/api/[a-zA-Z0-9/_-]+',
            r'/[a-zA-Z0-9/_-]+',
        ]
        for pattern in url_patterns:
            urls = re.findall(pattern, text)
            if urls:
                return urls[0]
        return '/api/unknown'

    @staticmethod
    def _extract_path(url: str) -> str:
        """从URL中提取路径部分"""
        if url.startswith('http'):
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.path
        return url

    @staticmethod
    def _extract_api_name(description: str, url: str) -> str:
        """提取API名称"""
        # 从URL提取
        path = APIGenerator._extract_path(url)
        path_parts = [p for p in path.split('/') if p]
        if path_parts:
            api_name = path_parts[-1].replace('-', '').replace('_', '')
            # 尝试转换为中文
            name_map = {
                'list': '列表', 'query': '查询', 'get': '详情', 'create': '创建', 
                'update': '更新', 'delete': '删除', 'add': '添加', 'edit': '编辑',
                'search': '搜索', 'login': '登录', 'register': '注册', 'upload': '上传',
                'export': '导出', 'import': '导入', 'save': '保存', 'submit': '提交'
            }
            if api_name.lower() in name_map:
                return name_map[api_name.lower()]
            return api_name
        return '未知接口'

    @staticmethod
    def _extract_params(text: str) -> List[Dict]:
        """提取参数信息"""
        params = []
        param_keywords = {
            'id': ['id', 'ID', '编号', '标识'],
            'name': ['name', '名称', '标题', 'title'],
            'email': ['email', '邮箱', '邮件'],
            'phone': ['phone', 'mobile', '手机', '电话'],
            'amount': ['amount', 'price', '金额', '价格', '费用'],
            'page': ['page', '页码', '页数'],
            'size': ['size', 'limit', '数量', '条数'],
            'status': ['status', '状态', 'type', '类型'],
            'date': ['date', 'time', '日期', '时间']
        }

        for param_type, keywords in param_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    params.append({
                        'name': keyword.lower(),
                        'type': param_type,
                        'required': True,
                        'description': f'{keyword}参数'
                    })
                    break
        return params

    @staticmethod
    def _requires_auth(text: str) -> bool:
        auth_keywords = ['登录', '认证', 'token', 'auth', '授权', '权限', '登录后', '需要登录']
        return any(kw.lower() in text.lower() for kw in auth_keywords)

    @staticmethod
    def _detect_content_type(text: str) -> str:
        if 'json' in text.lower():
            return 'application/json'
        if 'form' in text.lower() or '表单' in text:
            return 'application/x-www-form-urlencoded'
        if 'file' in text.lower() or '文件' in text or '上传' in text:
            return 'multipart/form-data'
        return 'application/json'

    @staticmethod
    def _generate_base_api_cases(analysis: Dict, start_index: int) -> List[Dict]:
        """生成基础API测试用例"""
        test_cases = []
        method = analysis['method']
        url = analysis['url']
        desc = analysis['description']
        api_name = analysis['api_name']
        
        # 使用解析器提取的请求头和请求体
        headers = analysis.get('headers', {})
        if 'Content-Type' not in headers:
            headers['Content-Type'] = analysis['content_type']
        
        body = analysis.get('body', {})
        params = {}
        # GET请求使用query参数，POST/PUT使用body
        if method == 'GET':
            params = analysis.get('params', {})
        
        # 正向测试 - 成功场景
        test_cases.append({
            'id': f'API-{start_index:04d}',
            'name': f'【{api_name}】正常请求',
            'method': method,
            'url': url,
            'headers': headers,
            'params': params,
            'body': body if method != 'GET' else {},
            'expected_status': 200 if method in ['GET', 'PUT', 'PATCH'] else (201 if method == 'POST' else 204),
            'expected_response': {'success': True, 'data': '返回预期数据'},
            'description': f'验证{desc}的正常请求流程',
            'priority': 'P0',
            'tags': ['正向测试', '功能测试'],
            'api_name': api_name,
            'scenario': 'normal'
        })

        # 未授权测试（使用原接口方法）
        if analysis['requires_auth']:
            test_cases.append({
                'id': f'API-{start_index + len(test_cases):04d}',
                'name': f'【{api_name}】未授权访问',
                'method': method,
                'url': url,
                'headers': {},
                'params': {},
                'body': {},
                'expected_status': 401,
                'expected_response': {'error': 'Unauthorized'},
                'description': '验证未登录时访问需认证接口',
                'priority': 'P0',
                'tags': ['安全测试', '认证测试'],
                'api_name': api_name,
                'scenario': 'unauthorized'
            })

        return test_cases

    @staticmethod
    def _generate_param_cases(analysis: Dict, start_index: int) -> List[Dict]:
        """生成参数测试用例 - 增强版：包含多参数组合、少参、边界值等"""
        test_cases = []
        method = analysis['method']
        url = analysis['url']
        params = analysis['params']
        api_name = analysis['api_name']
        body = analysis.get('body', {})
        headers = analysis.get('headers', {})
        
        if 'Content-Type' not in headers:
            headers['Content-Type'] = analysis['content_type']

        index = start_index
        
        # 1. 空参数测试（无任何参数）
        test_cases.append({
            'id': f'API-{index:04d}',
            'name': f'【{api_name}】无参数请求',
            'method': method,
            'url': url,
            'headers': headers.copy(),
            'params': {},
            'body': {},
            'expected_status': 400,
            'expected_response': {'error': '参数缺失'},
            'description': '验证不传入任何参数时的处理',
            'priority': 'P1',
            'tags': ['参数测试', '逆向测试'],
            'api_name': api_name,
            'scenario': 'param_missing'
        })
        index += 1
        
        if not params:
            return test_cases

        # 2. 缺少单个必填参数（每个参数都测试一次）
        for param in params:
            param_name = param['name']
            # 构建缺少当前参数的请求体
            test_body = {k: v for k, v in body.items() if k != param_name}
            test_params = {k: v for k, v in (analysis.get('query_params', {})).items() if k != param_name}
            
            test_cases.append({
                'id': f'API-{index:04d}',
                'name': f'【{api_name}】缺少{param_name}参数',
                'method': method,
                'url': url,
                'headers': headers.copy(),
                'params': test_params,
                'body': test_body,
                'expected_status': 400,
                'expected_response': {'error': f'缺少必填参数{param_name}'},
                'description': f'验证缺少{param_name}参数时的处理',
                'priority': 'P1',
                'tags': ['参数测试', '逆向测试'],
                'api_name': api_name,
                'scenario': 'param_missing'
            })
            index += 1

        # 3. 单个参数测试（有效值和无效值）
        for param in params:
            param_name = param['name']
            param_type = param['type']
            param_example = param.get('example', '')
            
            # 使用解析器提取的示例值作为有效值
            if param_example:
                # GET使用params，POST/PUT使用body
                test_params = {param_name: param_example} if method == 'GET' else {}
                test_body = {} if method == 'GET' else {param_name: param_example}
                
                test_cases.append({
                    'id': f'API-{index:04d}',
                    'name': f'【{api_name}】{param_name}参数正常值',
                    'method': method,
                    'url': url,
                    'headers': headers.copy(),
                    'params': test_params,
                    'body': test_body,
                    'expected_status': 200,
                    'expected_response': {'success': True},
                    'description': f'验证{param_name}参数传入正常值"{param_example}"',
                    'priority': 'P1',
                    'tags': ['参数测试', '正向测试'],
                    'api_name': api_name,
                    'scenario': 'param_valid'
                })
                index += 1
            
            # 无效值测试
            if param_type in APIGenerator.PARAM_TYPES:
                rules = APIGenerator.PARAM_TYPES[param_type]
                for invalid_value in rules['invalid'][:2]:
                    test_params = {param_name: invalid_value} if method == 'GET' else {}
                    test_body = {} if method == 'GET' else {param_name: invalid_value}
                    
                    test_cases.append({
                        'id': f'API-{index:04d}',
                        'name': f'【{api_name}】{param_name}参数无效值',
                        'method': method,
                        'url': url,
                        'headers': headers.copy(),
                        'params': test_params,
                        'body': test_body,
                        'expected_status': 400,
                        'expected_response': {'error': f'{param_name}参数格式错误'},
                        'description': f'验证{param_name}参数传入无效值"{invalid_value}"',
                        'priority': 'P2',
                        'tags': ['参数测试', '逆向测试'],
                        'api_name': api_name,
                        'scenario': 'param_invalid'
                    })
                    index += 1

        # 4. 多参数组合测试（使用解析器提取的所有参数）
        if params and body:
            test_cases.append({
                'id': f'API-{index:04d}',
                'name': f'【{api_name}】完整参数组合',
                'method': method,
                'url': url,
                'headers': headers.copy(),
                'params': analysis.get('query_params', {}),
                'body': body,
                'expected_status': 200,
                'expected_response': {'success': True, 'data': '返回预期数据'},
                'description': '验证所有参数正确组合时的请求',
                'priority': 'P0',
                'tags': ['参数测试', '正向测试', '组合测试'],
                'api_name': api_name,
                'scenario': 'param_combination'
            })
            index += 1

        # 5. 部分参数组合（一半参数）
        if len(params) >= 2:
            half_count = (len(params) + 1) // 2
            partial_body = {}
            for i, param in enumerate(params[:half_count]):
                key = param['name']
                if key in body:
                    partial_body[key] = body[key]
                elif param.get('example'):
                    partial_body[key] = param['example']
            
            if partial_body:
                test_cases.append({
                    'id': f'API-{index:04d}',
                    'name': f'【{api_name}】部分参数组合',
                    'method': method,
                    'url': url,
                    'headers': headers.copy(),
                    'params': {},
                    'body': partial_body,
                    'expected_status': 400,
                    'expected_response': {'error': '参数缺失'},
                    'description': f'验证只传入{half_count}个参数时的处理',
                    'priority': 'P2',
                    'tags': ['参数测试', '逆向测试', '组合测试'],
                    'api_name': api_name,
                    'scenario': 'param_partial'
                })
                index += 1

        # 6. 参数值边界测试
        for param in params:
            param_name = param['name']
            # 测试超长值
            test_params = {param_name: 'A' * 500} if method == 'GET' else {}
            test_body = {} if method == 'GET' else {param_name: 'A' * 500}
            
            test_cases.append({
                'id': f'API-{index:04d}',
                'name': f'【{api_name}】{param_name}参数超长值',
                'method': method,
                'url': url,
                'headers': headers.copy(),
                'params': test_params,
                'body': test_body,
                'expected_status': 400,
                'expected_response': {'error': f'{param_name}参数过长'},
                'description': f'验证{param_name}参数传入超长值(500字符)',
                'priority': 'P2',
                'tags': ['参数测试', '边界测试'],
                'api_name': api_name,
                'scenario': 'param_boundary'
            })
            index += 1
            
            # 测试特殊字符
            test_params = {param_name: '<script>alert(1)</script>'} if method == 'GET' else {}
            test_body = {} if method == 'GET' else {param_name: '<script>alert(1)</script>'}
            
            test_cases.append({
                'id': f'API-{index:04d}',
                'name': f'【{api_name}】{param_name}参数特殊字符',
                'method': method,
                'url': url,
                'headers': headers.copy(),
                'params': test_params,
                'body': test_body,
                'expected_status': 400,
                'expected_response': {'error': f'{param_name}参数包含非法字符'},
                'description': f'验证{param_name}参数传入特殊字符',
                'priority': 'P2',
                'tags': ['参数测试', '安全测试'],
                'api_name': api_name,
                'scenario': 'param_special'
            })
            index += 1

        return test_cases

    @staticmethod
    def _generate_security_cases(analysis: Dict, start_index: int) -> List[Dict]:
        """生成安全测试用例"""
        test_cases = []
        method = analysis['method']
        url = analysis['url']
        api_name = analysis['api_name']
        index = start_index

        security_tests = [
            {'name': 'SQL注入', 'payload': "' OR '1'='1", 'expected_status': 400},
            {'name': 'XSS攻击', 'payload': '<script>alert(1)</script>', 'expected_status': 400},
            {'name': '路径遍历', 'payload': '../../etc/passwd', 'expected_status': 400},
            {'name': '超长输入', 'payload': 'A' * 10000, 'expected_status': 400},
            {'name': '特殊字符', 'payload': '!@#$%^&*(){}[]|\\;:,.<>?', 'expected_status': 400}
        ]

        for test in security_tests:
            test_cases.append({
                'id': f'API-{index:04d}',
                'name': f'【{api_name}】{test["name"]}防护',
                'method': method,
                'url': url,
                'headers': {'Content-Type': 'application/json'},
                'params': {'input': test['payload']},
                'body': {'input': test['payload']},
                'expected_status': test['expected_status'],
                'expected_response': {'error': '非法输入'},
                'description': f'验证{api_name}接口对{test["name"]}攻击的防护',
                'priority': 'P0',
                'tags': ['安全测试', test['name']],
                'api_name': api_name,
                'scenario': 'security'
            })
            index += 1

        return test_cases

    @staticmethod
    def _generate_performance_cases(analysis: Dict, start_index: int) -> List[Dict]:
        """生成性能测试用例"""
        test_cases = []
        method = analysis['method']
        url = analysis['url']
        api_name = analysis['api_name']

        performance_tests = [
            {'name': '响应时间', 'desc': '响应时间<500ms', 'expected_time': 500},
            {'name': '并发请求', 'desc': '支持100并发', 'concurrent': 100},
            {'name': '大数据量', 'desc': '处理大数据量', 'data_size': 'large'}
        ]

        for i, test in enumerate(performance_tests):
            test_cases.append({
                'id': f'API-{start_index + i:04d}',
                'name': f'【{api_name}】{test["name"]}测试',
                'method': method,
                'url': url,
                'headers': {'Content-Type': 'application/json'},
                'params': {},
                'body': {},
                'expected_status': 200,
                'expected_response': {'success': True},
                'description': f'验证{api_name}接口{test["desc"]}',
                'priority': 'P2',
                'tags': ['性能测试', test['name']],
                'api_name': api_name,
                'scenario': 'performance',
                'performance': test
            })

        return test_cases

    @staticmethod
    def _sort_by_priority(test_cases: List[Dict]) -> List[Dict]:
        """按优先级排序"""
        priority_order = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}
        return sorted(test_cases, key=lambda x: priority_order.get(x.get('priority', 'P2'), 2))