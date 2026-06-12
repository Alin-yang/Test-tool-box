"""
Apifox格式导出器 - 优化版
支持从接口文档提取URL并配置到Apifox环境中
"""
from typing import List, Dict
import json
import uuid
from urllib.parse import urlparse


class ApifoxExporter:
    """导出API测试用例为Apifox可导入格式"""

    @staticmethod
    def export(api_test_cases: List[Dict], output_path: str, servers: List[Dict] = None):
        """
        导出为Apifox格式（OpenAPI扩展格式）
        :param api_test_cases: API测试用例列表
        :param output_path: 输出路径
        :param servers: 服务器配置列表（可选）
        """
        # 从用例中提取服务器配置
        extracted_servers = ApifoxExporter._extract_servers_from_cases(api_test_cases)
        
        # 使用提取的服务器配置或用户提供的配置
        final_servers = servers if servers else extracted_servers
        
        if not final_servers:
            final_servers = [
                {'url': 'http://localhost:8080', 'description': '开发环境'}
            ]

        apifox_data = {
            'openapi': '3.0.0',
            'info': {
                'title': '自动生成的API测试用例',
                'version': '1.0.0',
                'description': '由测试用例自动生成工具生成'
            },
            'servers': final_servers,
            'paths': {},
            'components': {
                'schemas': {},
                'securitySchemes': {
                    'bearerAuth': {
                        'type': 'http',
                        'scheme': 'bearer',
                        'bearerFormat': 'JWT'
                    }
                }
            }
        }

        # 按URL和方法分组
        url_method_groups = {}
        for tc in api_test_cases:
            key = (tc.get('url', '/api/unknown'), tc.get('method', 'POST'))
            if key not in url_method_groups:
                url_method_groups[key] = []
            url_method_groups[key].append(tc)

        # 构建paths - 使用相对路径
        for (url, method), cases in url_method_groups.items():
            main_case = cases[0]
            method_lower = method.lower()
            
            # 提取相对路径（移除基础URL）
            relative_path = ApifoxExporter._extract_relative_path(url, final_servers)
            api_name = main_case.get('api_name', '未知接口')
            
            operation = {
                'summary': f'【{api_name}】{method}接口',
                'description': main_case.get('description', ''),
                'operationId': f'{method_lower}_{api_name.lower().replace(" ", "_")}',
                'tags': [api_name],
                'parameters': ApifoxExporter._build_parameters(main_case),
                'requestBody': ApifoxExporter._build_request_body(main_case),
                'responses': {},
                'security': [] if not main_case.get('headers', {}).get('Authorization') else [{'bearerAuth': []}]
            }
            
            status_codes = set()
            for tc in cases:
                status_codes.add(str(tc.get('expected_status', 200)))
            
            for status in status_codes:
                operation['responses'][status] = {
                    'description': ApifoxExporter._get_status_description(int(status)),
                    'content': {
                        'application/json': {
                            'schema': {'type': 'object'},
                            'example': {}
                        }
                    }
                }
            
            if relative_path not in apifox_data['paths']:
                apifox_data['paths'][relative_path] = {}
            apifox_data['paths'][relative_path][method_lower] = operation

        apifox_data['x-apifox-testcases'] = []
        for tc in api_test_cases:
            relative_path = ApifoxExporter._extract_relative_path(tc.get('url', ''), final_servers)
            testcase = {
                'id': tc.get('id', ''),
                'name': tc.get('name', ''),
                'request': {
                    'method': tc.get('method', 'POST'),
                    'url': relative_path,
                    'headers': tc.get('headers', {}),
                    'params': tc.get('params', {}),
                    'body': tc.get('body', {})
                },
                'expected': {
                    'status': tc.get('expected_status', 200),
                    'response': tc.get('expected_response', {})
                },
                'priority': tc.get('priority', 'P2'),
                'tags': tc.get('tags', [])
            }
            apifox_data['x-apifox-testcases'].append(testcase)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(apifox_data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _extract_servers_from_cases(test_cases: List[Dict]) -> List[Dict]:
        """从测试用例中提取服务器配置"""
        servers = {}
        
        for tc in test_cases:
            url = tc.get('url', '')
            if url.startswith('http'):
                parsed = urlparse(url)
                base_url = f"{parsed.scheme}://{parsed.netloc}"
                
                if base_url not in servers:
                    # 尝试从URL推断环境名称
                    env_name = ApifoxExporter._guess_env_name(base_url)
                    servers[base_url] = {
                        'url': base_url,
                        'description': env_name
                    }
        
        return list(servers.values())

    @staticmethod
    def _guess_env_name(url: str) -> str:
        """从URL推断环境名称"""
        url_lower = url.lower()
        if 'dev' in url_lower or 'develop' in url_lower:
            return '开发环境'
        if 'test' in url_lower:
            return '测试环境'
        if 'prod' in url_lower or 'production' in url_lower:
            return '生产环境'
        if 'staging' in url_lower:
            return '预发布环境'
        if 'localhost' in url_lower or '127.0.0.1' in url_lower:
            return '本地环境'
        return '默认环境'

    @staticmethod
    def _extract_relative_path(full_url: str, servers: List[Dict]) -> str:
        """从完整URL中提取相对路径"""
        if not full_url.startswith('http'):
            return full_url
        
        parsed = urlparse(full_url)
        path = parsed.path
        if parsed.query:
            path += f'?{parsed.query}'
        
        return path

    @staticmethod
    def _build_parameters(tc: Dict) -> List[Dict]:
        """构建参数列表"""
        params = []
        for key, value in tc.get('params', {}).items():
            params.append({
                'name': key,
                'in': 'query',
                'required': True,
                'schema': {'type': 'string'},
                'example': value
            })
        return params

    @staticmethod
    def _build_request_body(tc: Dict) -> Dict:
        """构建请求体"""
        body = tc.get('body', {})
        if not body:
            return None
        
        return {
            'required': True,
            'content': {
                'application/json': {
                    'schema': {'type': 'object'},
                    'example': body
                }
            }
        }

    @staticmethod
    def export_apifox_json(api_test_cases: List[Dict], output_path: str, servers: List[Dict] = None):
        """
        导出为Apifox原生JSON格式（可直接导入）
        重点：每个测试用例作为独立接口导出，确保导入后所有用例都可见
        通过在path中添加唯一标识确保Apifox不会合并测试用例
        """
        # 从用例中提取服务器配置
        extracted_servers = ApifoxExporter._extract_servers_from_cases(api_test_cases)
        final_servers = servers if servers else extracted_servers
        
        if not final_servers:
            final_servers = [{'url': 'http://localhost:8080', 'description': '开发环境'}]

        interfaces = []
        interface_index = 1

        for tc in api_test_cases:
            # 提取相对路径
            full_url = tc.get('url', '')
            relative_path = ApifoxExporter._extract_relative_path(full_url, final_servers)
            
            api_name = tc.get('api_name', '未知接口')
            scenario = tc.get('scenario', 'unknown')
            case_id = tc.get('id', f'case_{interface_index}')
            
            # 为每个测试用例生成唯一的path，防止Apifox合并
            # 在原path基础上添加用例ID作为查询参数，确保唯一性
            unique_path = f"{relative_path}?__testcase={case_id}"
            
            # 每个测试用例作为独立接口导出
            interface = {
                'name': f'【{api_name}】{tc.get("name", "")}',
                'method': tc.get('method', 'POST'),
                'path': unique_path,
                'description': tc.get('description', ''),
                'tags': [api_name, scenario, case_id],
                'requestBody': {
                    'type': 'application/json',
                    'json': tc.get('body', {})
                },
                'parameters': [
                    {'name': k, 'value': v, 'type': 'string', 'in': 'query'} 
                    for k, v in tc.get('params', {}).items()
                ],
                'headers': [{'name': k, 'value': v} for k, v in tc.get('headers', {}).items()],
                'responses': [{
                    'code': tc.get('expected_status', 200),
                    'name': ApifoxExporter._get_status_description(tc.get('expected_status', 200)),
                    'json': tc.get('expected_response', {})
                }],
                'testCases': [{
                    'name': tc.get('name', ''),
                    'request': {
                        'body': tc.get('body', {}),
                        'params': tc.get('params', {})
                    },
                    'expected': {
                        'status': tc.get('expected_status', 200),
                        'body': tc.get('expected_response', {})
                    },
                    'priority': tc.get('priority', 'P2'),
                    'tags': tc.get('tags', [])
                }],
                'api_name': api_name,
                '_index': interface_index
            }
            interfaces.append(interface)
            interface_index += 1
        
        # 构建环境配置（Apifox格式）
        server_config = {}
        env_names = set()
        for server in final_servers:
            env_name = server.get('description', '')
            # 确保环境名称唯一
            counter = 1
            original_name = env_name
            while env_name in env_names:
                env_name = f'{original_name}{counter}'
                counter += 1
            env_names.add(env_name)
            server_config[env_name] = server.get('url', '')
        
        # 添加模块级别的前置URL配置
        module_config = {
            'name': '自动生成的API测试用例',
            'baseUrl': final_servers[0].get('url', '') if final_servers else ''
        }

        apifox_import_data = {
            'version': '1.0',
            'type': 'interface',
            'data': interfaces,
            'serverConfig': server_config if server_config else None,
            'moduleConfig': module_config
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(apifox_import_data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def export_openapi(api_test_cases: List[Dict], output_path: str, servers: List[Dict] = None):
        """导出为标准OpenAPI 3.0格式 - 测试用例通过examples字段导入"""
        extracted_servers = ApifoxExporter._extract_servers_from_cases(api_test_cases)
        final_servers = servers if servers else extracted_servers
        
        if not final_servers:
            final_servers = [{'url': 'http://localhost:8080', 'description': '开发环境'}]

        openapi_data = {
            'openapi': '3.0.0',
            'info': {
                'title': '自动生成的API文档',
                'version': '1.0.0',
                'description': '由测试用例自动生成工具生成'
            },
            'servers': final_servers,
            'paths': {},
            'components': {
                'schemas': {},
                'examples': {},
                'securitySchemes': {
                    'bearerAuth': {
                        'type': 'http',
                        'scheme': 'bearer'
                    }
                }
            }
        }

        # 按接口分组（相同路径+方法为同一接口）
        interface_groups = {}
        for tc in api_test_cases:
            full_url = tc.get('url', '/api/unknown')
            method = tc.get('method', 'POST')
            relative_path = ApifoxExporter._extract_relative_path(full_url, final_servers)
            key = (relative_path, method)
            
            if key not in interface_groups:
                interface_groups[key] = []
            interface_groups[key].append(tc)

        for (relative_path, method), test_cases in interface_groups.items():
            method_lower = method.lower()
            api_name = test_cases[0].get('api_name', '未知接口')
            
            if relative_path not in openapi_data['paths']:
                openapi_data['paths'][relative_path] = {}

            # 收集所有测试用例作为请求体示例
            request_examples = {}
            response_examples = {}
            
            for tc in test_cases:
                case_name = tc.get('name', f'用例{len(request_examples) + 1}')
                body = tc.get('body', {})
                if body:
                    request_examples[case_name] = {
                        'value': body,
                        'summary': case_name
                    }
                
                status_code = str(tc.get('expected_status', 200))
                if status_code not in response_examples:
                    response_examples[status_code] = {}
                
                response_body = tc.get('expected_response', {})
                if response_body:
                    response_examples[status_code][case_name] = {
                        'value': response_body,
                        'summary': case_name
                    }

            operation = {
                'summary': f'【{api_name}】{method}接口',
                'description': test_cases[0].get('description', ''),
                'operationId': f'{method_lower}_{api_name.lower().replace(" ", "_")}',
                'tags': [api_name],
                'responses': {}
            }

            # 添加请求体（包含多个示例）
            if request_examples:
                operation['requestBody'] = {
                    'required': True,
                    'content': {
                        'application/json': {
                            'examples': request_examples
                        }
                    }
                }
            
            # 添加参数
            params = test_cases[0].get('params', {})
            if params:
                operation['parameters'] = [
                    {'name': k, 'in': 'query', 'required': True, 'schema': {'type': 'string'}, 'example': v}
                    for k, v in params.items()
                ]
            
            # 添加请求头
            headers = test_cases[0].get('headers', {})
            if headers:
                if 'parameters' not in operation:
                    operation['parameters'] = []
                operation['parameters'].extend([
                    {'name': k, 'in': 'header', 'required': True, 'schema': {'type': 'string'}, 'example': v}
                    for k, v in headers.items()
                ])

            # 添加响应（包含多个示例）
            for status_code, examples in response_examples.items():
                operation['responses'][status_code] = {
                    'description': ApifoxExporter._get_status_description(int(status_code)),
                    'content': {
                        'application/json': {
                            'examples': examples
                        }
                    }
                }
            
            # 如果没有响应示例，添加默认响应
            if not operation['responses']:
                operation['responses']['200'] = {
                    'description': '成功'
                }

            openapi_data['paths'][relative_path][method_lower] = operation

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(openapi_data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def export_postman_collection(api_test_cases: List[Dict], output_path: str, servers: List[Dict] = None):
        """导出为Postman Collection v2.1格式（Apifox完美支持）"""
        extracted_servers = ApifoxExporter._extract_servers_from_cases(api_test_cases)
        final_servers = servers if servers else extracted_servers
        
        if not final_servers:
            final_servers = [{'url': 'http://localhost:8080', 'description': '开发环境'}]

        # 按接口分组
        interface_groups = {}
        for tc in api_test_cases:
            full_url = tc.get('url', '/api/unknown')
            method = tc.get('method', 'POST')
            relative_path = ApifoxExporter._extract_relative_path(full_url, final_servers)
            api_name = tc.get('api_name', '未知接口')
            
            if api_name not in interface_groups:
                interface_groups[api_name] = []
            interface_groups[api_name].append(tc)

        collection = {
            'info': {
                '_postman_id': str(uuid.uuid4()),
                'name': '自动生成的API测试用例',
                'description': '由测试用例自动生成工具生成',
                'schema': 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json'
            },
            'item': []
        }

        # 添加环境变量
        collection['variable'] = []
        for server in final_servers:
            collection['variable'].append({
                'key': 'baseUrl',
                'value': server.get('url', 'http://localhost:8080'),
                'type': 'string'
            })
            break  # 只添加第一个服务器作为默认环境

        # 创建文件夹和请求
        for api_name, test_cases in interface_groups.items():
            folder = {
                'name': api_name,
                'item': []
            }

            for tc in test_cases:
                full_url = tc.get('url', '/api/unknown')
                method = tc.get('method', 'POST')
                relative_path = ApifoxExporter._extract_relative_path(full_url, final_servers)
                
                request = {
                    'name': tc.get('name', '未命名用例'),
                    'request': {
                        'method': method,
                        'header': [],
                        'url': {
                            'raw': f'{{{{baseUrl}}}}{relative_path}',
                            'host': ['{{baseUrl}}'],
                            'path': relative_path.lstrip('/').split('/')
                        }
                    },
                    'response': []
                }

                # 添加请求头
                headers = tc.get('headers', {})
                for key, value in headers.items():
                    request['request']['header'].append({
                        'key': key,
                        'value': value,
                        'type': 'text'
                    })

                # 添加查询参数
                params = tc.get('params', {})
                if params:
                    request['request']['url']['query'] = []
                    for key, value in params.items():
                        request['request']['url']['query'].append({
                            'key': key,
                            'value': str(value),
                            'type': 'text'
                        })

                # 添加请求体
                body = tc.get('body', {})
                if body:
                    request['request']['body'] = {
                        'mode': 'raw',
                        'raw': json.dumps(body, ensure_ascii=False),
                        'options': {
                            'raw': {
                                'language': 'json'
                            }
                        }
                    }

                # 添加响应示例
                expected_status = tc.get('expected_status', 200)
                expected_response = tc.get('expected_response', {})
                request['response'].append({
                    'name': tc.get('name', '预期响应'),
                    'originalRequest': request['request'],
                    'status': str(expected_status),
                    'code': expected_status,
                    '_postman_previewlanguage': 'json',
                    'header': [{'key': 'Content-Type', 'value': 'application/json'}],
                    'body': json.dumps(expected_response, ensure_ascii=False)
                })

                folder['item'].append(request)

            collection['item'].append(folder)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(collection, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _get_status_description(status_code: int) -> str:
        """获取状态码描述"""
        descriptions = {
            200: '成功',
            201: '创建成功',
            204: '无内容',
            400: '请求参数错误',
            401: '未授权',
            403: '禁止访问',
            404: '资源不存在',
            405: '方法不允许',
            500: '服务器内部错误'
        }
        return descriptions.get(status_code, '未知状态')