"""
Mock数据生成器
根据接口文档自动生成Mock数据
"""
import random
import json
from typing import Dict, List, Any


class MockGenerator:
    """Mock数据生成器"""
    
    # 数据类型映射
    TYPE_MAPPING = {
        'string': 'str',
        'int': 'int',
        'integer': 'int',
        'float': 'float',
        'number': 'float',
        'boolean': 'bool',
        'bool': 'bool',
        'array': 'list',
        'list': 'list',
        'object': 'dict',
        'dict': 'dict',
        'date': 'date',
        'datetime': 'datetime',
        'time': 'time',
        'email': 'email',
        'phone': 'phone',
        'url': 'url',
        'id': 'id',
        'name': 'name',
        'password': 'password'
    }
    
    # 常用Mock数据模板
    MOCK_TEMPLATES = {
        'user': {
            'name': 'generate_user',
            'description': '用户信息'
        },
        'login': {
            'name': 'generate_login_response',
            'description': '登录响应'
        },
        'token': {
            'name': 'generate_token',
            'description': 'Token信息'
        },
        'product': {
            'name': 'generate_product',
            'description': '商品信息'
        },
        'order': {
            'name': 'generate_order',
            'description': '订单信息'
        },
        'page': {
            'name': 'generate_page_data',
            'description': '分页数据'
        },
        'address': {
            'name': 'generate_address',
            'description': '地址信息'
        },
        'image': {
            'name': 'generate_image_url',
            'description': '图片URL'
        },
        'pagination': {
            'name': 'generate_pagination',
            'description': '分页参数'
        },
        'error': {
            'name': 'generate_error_response',
            'description': '错误响应'
        },
        'success': {
            'name': 'generate_success_response',
            'description': '成功响应'
        },
        'empty_list': {
            'name': 'generate_empty_list',
            'description': '空列表'
        },
        'id_card': {
            'name': 'generate_id_card',
            'description': '身份证号'
        },
        'bank_card': {
            'name': 'generate_bank_card',
            'description': '银行卡号'
        },
        'uuid': {
            'name': 'generate_uuid',
            'description': 'UUID'
        },
        'enum': {
            'name': 'generate_enum_values',
            'description': '枚举值'
        }
    }
    
    # 常用响应模板
    RESPONSE_TEMPLATES = {
        'success': {
            'code': 200,
            'message': 'success',
            'success': True,
            'data': None
        },
        'success_list': {
            'code': 200,
            'message': 'success',
            'success': True,
            'data': [],
            'total': 0,
            'page': 1,
            'size': 10
        },
        'error': {
            'code': 400,
            'message': 'error',
            'success': False,
            'data': None
        },
        'unauthorized': {
            'code': 401,
            'message': 'Unauthorized',
            'success': False
        },
        'forbidden': {
            'code': 403,
            'message': 'Forbidden',
            'success': False
        },
        'not_found': {
            'code': 404,
            'message': 'Not Found',
            'success': False
        }
    }
    
    @staticmethod
    def _generate_value(data_type: str, schema: Dict = None) -> Any:
        """根据类型生成Mock值"""
        data_type = data_type.lower()
        
        # 检查是否有enum
        if schema and 'enum' in schema:
            return random.choice(schema['enum'])
        
        # 检查是否有format
        if schema and 'format' in schema:
            format_type = schema['format'].lower()
            if format_type == 'email':
                return MockGenerator._generate_email()
            elif format_type == 'phone' or format_type == 'mobile':
                return MockGenerator._generate_phone()
            elif format_type == 'date':
                return MockGenerator._generate_date()
            elif format_type == 'datetime':
                return MockGenerator._generate_datetime()
            elif format_type == 'url':
                return MockGenerator._generate_url()
        
        # 根据类型生成值
        if data_type in ['string', 'str']:
            length = schema.get('maxLength', 20) if schema else 20
            return MockGenerator._generate_string(min(20, max(1, length)))
        elif data_type in ['int', 'integer']:
            if schema:
                minimum = schema.get('minimum', 0)
                maximum = schema.get('maximum', 100)
                return random.randint(minimum, max(minimum, maximum))
            return random.randint(0, 100)
        elif data_type in ['float', 'number']:
            if schema:
                minimum = schema.get('minimum', 0.0)
                maximum = schema.get('maximum', 100.0)
                return round(random.uniform(minimum, max(minimum, maximum)), 2)
            return round(random.uniform(0.0, 100.0), 2)
        elif data_type in ['boolean', 'bool']:
            return random.choice([True, False])
        elif data_type in ['date']:
            return MockGenerator._generate_date()
        elif data_type in ['datetime', 'timestamp']:
            return MockGenerator._generate_datetime()
        elif data_type in ['email']:
            return MockGenerator._generate_email()
        elif data_type in ['phone', 'mobile']:
            return MockGenerator._generate_phone()
        elif data_type in ['url']:
            return MockGenerator._generate_url()
        elif data_type in ['id']:
            return MockGenerator._generate_id()
        elif data_type in ['name']:
            return MockGenerator._generate_name()
        elif data_type in ['password']:
            return MockGenerator._generate_password()
        return ''
    
    @staticmethod
    def _generate_string(length: int = 10) -> str:
        """生成随机字符串"""
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        return ''.join(random.choice(chars) for _ in range(length))
    
    @staticmethod
    def _generate_email() -> str:
        """生成随机邮箱"""
        domains = ['qq.com', '163.com', 'gmail.com', 'hotmail.com', 'test.com']
        return f"{MockGenerator._generate_string(8)}@{random.choice(domains)}"
    
    @staticmethod
    def _generate_phone() -> str:
        """生成随机手机号"""
        prefixes = ['138', '139', '137', '159', '188', '189']
        return f"{random.choice(prefixes)}{''.join(random.choice('0123456789') for _ in range(8))}"
    
    @staticmethod
    def _generate_date() -> str:
        """生成随机日期"""
        year = random.randint(2020, 2025)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        return f"{year}-{month:02d}-{day:02d}"
    
    @staticmethod
    def _generate_datetime() -> str:
        """生成随机日期时间"""
        year = random.randint(2020, 2025)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        return f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"
    
    @staticmethod
    def _generate_url() -> str:
        """生成随机URL"""
        domains = ['example.com', 'test.com', 'api.com']
        paths = ['/user', '/api/data', '/v1/item']
        return f"https://{random.choice(domains)}{random.choice(paths)}"
    
    @staticmethod
    def _generate_id() -> str:
        """生成随机ID"""
        return ''.join(random.choice('0123456789abcdef') for _ in range(16))
    
    @staticmethod
    def _generate_name() -> str:
        """生成随机姓名"""
        first_names = ['张', '李', '王', '刘', '陈', '杨', '赵', '黄']
        last_names = ['伟', '强', '勇', '军', '涛', '明', '辉', '刚']
        return f"{random.choice(first_names)}{random.choice(last_names)}"
    
    @staticmethod
    def _generate_password() -> str:
        """生成随机密码"""
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%'
        return ''.join(random.choice(chars) for _ in range(12))
    
    @staticmethod
    def generate_user() -> Dict:
        """生成用户信息"""
        return {
            'id': MockGenerator._generate_id(),
            'name': MockGenerator._generate_name(),
            'nickname': f"{MockGenerator._generate_string(6)}_user",
            'email': MockGenerator._generate_email(),
            'phone': MockGenerator._generate_phone(),
            'age': random.randint(18, 60),
            'gender': random.choice(['男', '女']),
            'status': random.choice([0, 1]),
            'created_at': MockGenerator._generate_datetime(),
            'updated_at': MockGenerator._generate_datetime()
        }
    
    @staticmethod
    def generate_login_response() -> Dict:
        """生成登录响应"""
        return {
            'code': 200,
            'message': 'success',
            'success': True,
            'data': {
                'token': MockGenerator._generate_id(),
                'refresh_token': MockGenerator._generate_id(),
                'expires_in': 7200,
                'user': MockGenerator.generate_user()
            }
        }
    
    @staticmethod
    def generate_token() -> Dict:
        """生成Token信息"""
        return {
            'access_token': MockGenerator._generate_id(),
            'refresh_token': MockGenerator._generate_id(),
            'token_type': 'Bearer',
            'expires_in': 7200,
            'scope': 'read write'
        }
    
    @staticmethod
    def generate_product() -> Dict:
        """生成商品信息"""
        return {
            'id': MockGenerator._generate_id(),
            'name': f"商品_{MockGenerator._generate_string(8)}",
            'code': f"SKU{random.randint(100000, 999999)}",
            'price': round(random.uniform(10, 9999.99), 2),
            'original_price': round(random.uniform(10, 9999.99), 2),
            'stock': random.randint(0, 1000),
            'sales': random.randint(0, 10000),
            'category': random.choice(['电子产品', '服装', '食品', '日用品']),
            'status': random.choice([0, 1]),
            'created_at': MockGenerator._generate_datetime()
        }
    
    @staticmethod
    def generate_order() -> Dict:
        """生成订单信息"""
        return {
            'id': f"ORD{random.randint(1000000000, 9999999999)}",
            'user_id': MockGenerator._generate_id(),
            'total_amount': round(random.uniform(10, 9999.99), 2),
            'pay_amount': round(random.uniform(10, 9999.99), 2),
            'status': random.choice(['待支付', '已支付', '待发货', '已发货', '已完成', '已取消']),
            'pay_type': random.choice(['微信', '支付宝', '银行卡']),
            'create_time': MockGenerator._generate_datetime(),
            'pay_time': MockGenerator._generate_datetime(),
            'items': [MockGenerator.generate_product() for _ in range(random.randint(1, 3))]
        }
    
    @staticmethod
    def generate_page_data(item_type: str = 'product') -> Dict:
        """生成分页数据"""
        items = []
        item_count = random.randint(1, 10)
        
        for _ in range(item_count):
            if item_type == 'user':
                items.append(MockGenerator.generate_user())
            elif item_type == 'order':
                items.append(MockGenerator.generate_order())
            else:
                items.append(MockGenerator.generate_product())
        
        return {
            'code': 200,
            'message': 'success',
            'success': True,
            'data': items,
            'total': random.randint(100, 1000),
            'page': 1,
            'size': 10
        }
    
    @staticmethod
    def generate_address() -> Dict:
        """生成地址信息"""
        provinces = ['北京市', '上海市', '广东省', '浙江省', '江苏省', '四川省', '湖北省']
        cities = ['北京市', '上海市', '广州市', '深圳市', '杭州市', '南京市', '成都市', '武汉市']
        districts = ['朝阳区', '海淀区', '浦东新区', '天河区', '南山区', '西湖区']
        
        return {
            'id': MockGenerator._generate_id(),
            'name': MockGenerator._generate_name(),
            'phone': MockGenerator._generate_phone(),
            'province': random.choice(provinces),
            'city': random.choice(cities),
            'district': random.choice(districts),
            'detail': f"{random.randint(1, 999)}号{MockGenerator._generate_string(4)}小区{random.randint(1, 20)}栋{random.randint(1, 30)}层{random.randint(1, 99)}室",
            'is_default': random.choice([True, False]),
            'status': 1
        }
    
    @staticmethod
    def generate_image_url(width: int = 200, height: int = 200) -> str:
        """生成图片URL"""
        return f"https://picsum.photos/{width}/{height}?random={random.randint(1, 1000)}"
    
    @staticmethod
    def generate_pagination() -> Dict:
        """生成分页参数"""
        return {
            'page': random.randint(1, 10),
            'size': random.randint(10, 100),
            'total': random.randint(100, 1000),
            'pages': random.randint(1, 10)
        }
    
    @staticmethod
    def generate_error_response(code: int = 400, message: str = 'error') -> Dict:
        """生成错误响应"""
        return {
            'code': code,
            'message': message,
            'success': False,
            'data': None
        }
    
    @staticmethod
    def generate_success_response(data: Any = None) -> Dict:
        """生成成功响应"""
        if data is None:
            data = {'id': MockGenerator._generate_id()}
        return {
            'code': 200,
            'message': 'success',
            'success': True,
            'data': data
        }
    
    @staticmethod
    def generate_empty_list() -> Dict:
        """生成空列表响应"""
        return {
            'code': 200,
            'message': 'success',
            'success': True,
            'data': [],
            'total': 0,
            'page': 1,
            'size': 10
        }
    
    @staticmethod
    def generate_id_card() -> str:
        """生成身份证号"""
        province_codes = ['11', '12', '13', '14', '15', '21', '22', '23', '31', '32', '33', '34', '35', '36', '37', '41', '42', '43', '44', '45', '46', '50', '51', '52', '53', '54', '61', '62', '63', '64', '65']
        year = random.randint(1970, 2005)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        
        return f"{random.choice(province_codes)}{random.randint(10, 99)}{random.randint(0, 99)}{year}{month:02d}{day:02d}{random.randint(100, 999)}{random.choice('0123456789Xx')}"
    
    @staticmethod
    def generate_bank_card() -> str:
        """生成银行卡号"""
        prefixes = ['622202', '622203', '622848', '622155', '622156', '622525', '622526', '622535', '622536', '622516']
        return f"{random.choice(prefixes)}{''.join(random.choice('0123456789') for _ in range(10))}"
    
    @staticmethod
    def generate_uuid() -> str:
        """生成UUID"""
        import uuid
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_enum_values(values: List[str] = None) -> List[str]:
        """生成枚举值"""
        if values is None:
            values = ['value1', 'value2', 'value3', 'value4', 'value5']
        return values[:random.randint(1, len(values))]
    
    @staticmethod
    def generate_by_template(template_key: str) -> Any:
        """根据模板键生成Mock数据"""
        template = MockGenerator.MOCK_TEMPLATES.get(template_key)
        if not template:
            return {'error': f'模板 {template_key} 不存在'}
        
        method_name = template['name']
        method = getattr(MockGenerator, method_name, None)
        if method and callable(method):
            return method()
        return {'error': f'方法 {method_name} 不存在'}
    
    @staticmethod
    def get_templates() -> Dict:
        """获取所有模板列表"""
        return {key: value['description'] for key, value in MockGenerator.MOCK_TEMPLATES.items()}
    
    @staticmethod
    def generate_from_schema(schema: Dict) -> Any:
        """根据JSON Schema生成Mock数据"""
        if not isinstance(schema, dict):
            return schema
        
        # 处理anyOf/oneOf
        if 'anyOf' in schema:
            return MockGenerator.generate_from_schema(random.choice(schema['anyOf']))
        if 'oneOf' in schema:
            return MockGenerator.generate_from_schema(random.choice(schema['oneOf']))
        
        # 获取类型
        data_type = schema.get('type', 'string')
        
        # 处理数组
        if data_type == 'array':
            items_schema = schema.get('items', {})
            count = schema.get('maxItems', 5)
            return [MockGenerator.generate_from_schema(items_schema) for _ in range(min(5, max(1, count)))]
        
        # 处理对象
        if data_type == 'object':
            properties = schema.get('properties', {})
            required = schema.get('required', [])
            result = {}
            for prop_name, prop_schema in properties.items():
                if prop_name in required or random.choice([True, False]):
                    result[prop_name] = MockGenerator.generate_from_schema(prop_schema)
            return result
        
        # 处理基本类型
        return MockGenerator._generate_value(data_type, schema)
    
    @staticmethod
    def generate_response(api_info: Dict, template: str = 'success') -> Dict:
        """生成Mock响应"""
        response = MockGenerator.RESPONSE_TEMPLATES.get(template, MockGenerator.RESPONSE_TEMPLATES['success']).copy()
        
        # 根据API信息生成data
        if response.get('data') is None:
            # 尝试从api_info获取响应结构
            response_schema = api_info.get('response_schema', {})
            if response_schema:
                response['data'] = MockGenerator.generate_from_schema(response_schema)
            else:
                # 根据请求体结构生成响应
                request_body = api_info.get('body', {})
                if request_body:
                    response['data'] = MockGenerator.generate_from_schema({'type': 'object', 'properties': request_body})
                else:
                    response['data'] = {'id': MockGenerator._generate_id()}
        
        elif isinstance(response.get('data'), list):
            # 生成列表数据
            response_schema = api_info.get('response_schema', {}).get('items', {})
            count = random.randint(3, 10)
            response['data'] = [MockGenerator.generate_from_schema(response_schema) for _ in range(count)]
            response['total'] = random.randint(100, 1000)
        
        return response
    
    @staticmethod
    def generate_mock_data(api_info: List[Dict]) -> List[Dict]:
        """为多个API生成Mock数据"""
        mock_results = []
        
        for api in api_info:
            mock_result = {
                'method': api.get('method', 'GET'),
                'url': api.get('url', ''),
                'api_name': api.get('api_name', 'unknown'),
                'description': api.get('description', ''),
                'mock_responses': {
                    'success': MockGenerator.generate_response(api, 'success'),
                    'error': MockGenerator.generate_response(api, 'error')
                }
            }
            
            # 如果是列表接口，添加列表响应
            if any(kw in api.get('description', '').lower() for kw in ['list', '列表', '查询', 'search']):
                mock_result['mock_responses']['success_list'] = MockGenerator.generate_response(api, 'success_list')
            
            # 添加认证相关响应
            if any(kw in api.get('description', '').lower() for kw in ['auth', '登录', 'token', '认证']):
                mock_result['mock_responses']['unauthorized'] = MockGenerator.generate_response(api, 'unauthorized')
            
            mock_results.append(mock_result)
        
        return mock_results
    
    @staticmethod
    def generate_mock_server_config(api_info: List[Dict], base_path: str = '/mock') -> Dict:
        """生成Mock服务器配置"""
        routes = []
        
        for api in api_info:
            route = {
                'path': api.get('url', '').replace('https://', '').replace('http://', '').split('/')[1:] or ['unknown'],
                'method': api.get('method', 'GET').lower(),
                'response': MockGenerator.generate_response(api, 'success'),
                'description': api.get('description', '')
            }
            routes.append(route)
        
        return {
            'name': 'Auto Generated Mock Server',
            'base_path': base_path,
            'routes': routes,
            'generated_at': MockGenerator._generate_datetime()
        }
    
    @staticmethod
    def generate_mock_json_file(api_info: List[Dict], output_path: str) -> None:
        """生成Mock JSON文件"""
        mock_data = MockGenerator.generate_mock_data(api_info)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(mock_data, f, ensure_ascii=False, indent=2)
