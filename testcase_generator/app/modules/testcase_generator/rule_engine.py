"""
测试用例规则引擎 - 集成专业测试设计技术
包含：等价类划分、边界值分析、场景设计、错误猜测等方法
"""
from typing import List, Dict, Tuple, Optional
import re


class EquivalenceClassAnalyzer:
    """
    等价类划分法分析器
    将输入域划分为有效等价类和无效等价类
    """

    # 常见输入类型及其等价类规则
    INPUT_TYPE_RULES = {
        'username': {
            'valid': [
                {'name': '有效长度用户名', 'range': (6, 20), 'example': 'testuser123'},
                {'name': '纯字母用户名', 'pattern': r'^[a-zA-Z]+$', 'example': 'username'},
                {'name': '纯数字用户名', 'pattern': r'^[0-9]+$', 'example': '12345678'},
                {'name': '字母数字混合', 'pattern': r'^[a-zA-Z0-9]+$', 'example': 'user2024'},
            ],
            'invalid': [
                {'name': '长度不足', 'range': (1, 5), 'example': 'abc'},
                {'name': '长度超限', 'range': (21, 100), 'example': 'verylongusername'},
                {'name': '包含特殊字符', 'pattern': r'[!@#$%^&*]', 'example': 'user@test'},
                {'name': '包含空格', 'pattern': r'\s', 'example': 'user name'},
                {'name': '为空', 'value': '', 'example': ''},
            ]
        },
        'password': {
            'valid': [
                {'name': '有效密码长度', 'range': (8, 16), 'example': 'Pass123!'},
                {'name': '包含大小写', 'pattern': r'[a-z].*[A-Z]|[A-Z].*[a-z]', 'example': 'Password1'},
                {'name': '包含数字', 'pattern': r'[0-9]', 'example': 'pass1234'},
                {'name': '包含特殊字符', 'pattern': r'[!@#$%^&*]', 'example': 'pass!123'},
            ],
            'invalid': [
                {'name': '长度不足', 'range': (1, 7), 'example': 'pass'},
                {'name': '长度超限', 'range': (17, 50), 'example': 'verylongpassword123'},
                {'name': '纯数字', 'pattern': r'^[0-9]+$', 'example': '12345678'},
                {'name': '纯字母', 'pattern': r'^[a-zA-Z]+$', 'example': 'password'},
                {'name': '为空', 'value': '', 'example': ''},
            ]
        },
        'email': {
            'valid': [
                {'name': '标准邮箱格式', 'pattern': r'^[\w.-]+@[\w.-]+\.\w+$', 'example': 'test@example.com'},
                {'name': '带子域名', 'pattern': r'^[\w.-]+@[\w.-]+\.[\w.-]+\.\w+$', 'example': 'test@sub.example.com'},
            ],
            'invalid': [
                {'name': '缺少@符号', 'pattern': r'^[\w.-]+$', 'example': 'testexample.com'},
                {'name': '缺少域名', 'pattern': r'^[\w.-]+@$', 'example': 'test@'},
                {'name': '缺少后缀', 'pattern': r'^[\w.-]+@[\w.-]+$', 'example': 'test@example'},
                {'name': '特殊字符错误', 'pattern': r'[<>]', 'example': 'test<>@example.com'},
                {'name': '为空', 'value': '', 'example': ''},
            ]
        },
        'phone': {
            'valid': [
                {'name': '11位手机号', 'pattern': r'^1[3-9]\d{9}$', 'example': '13812345678'},
                {'name': '带区号', 'pattern': r'^\+86\d{11}$', 'example': '+8613812345678'},
            ],
            'invalid': [
                {'name': '位数不足', 'pattern': r'^\d{1,10}$', 'example': '123456789'},
                {'name': '位数超限', 'pattern': r'^\d{12,}$', 'example': '123456789012'},
                {'name': '非法开头', 'pattern': r'^[02]\d{10}$', 'example': '01234567890'},
                {'name': '包含字母', 'pattern': r'[a-zA-Z]', 'example': '138abc45678'},
                {'name': '为空', 'value': '', 'example': ''},
            ]
        },
        'id_card': {
            'valid': [
                {'name': '18位身份证', 'pattern': r'^\d{17}[\dXx]$', 'example': '123456789012345678'},
                {'name': '15位身份证', 'pattern': r'^\d{15}$', 'example': '123456789012345'},
            ],
            'invalid': [
                {'name': '位数错误', 'pattern': r'^\d{1,14}|\d{19,}$', 'example': '12345678'},
                {'name': '非法字符', 'pattern': r'[^\dXx]', 'example': '1234567890AB'},
                {'name': '为空', 'value': '', 'example': ''},
            ]
        },
        'amount': {
            'valid': [
                {'name': '正整数金额', 'pattern': r'^[1-9]\d*$', 'example': '100'},
                {'name': '小数金额', 'pattern': r'^\d+\.\d{1,2}$', 'example': '99.99'},
                {'name': '最小金额', 'value': '0.01', 'example': '0.01'},
            ],
            'invalid': [
                {'name': '负数金额', 'pattern': r'^-\d+', 'example': '-100'},
                {'name': '零金额', 'value': '0', 'example': '0'},
                {'name': '格式错误', 'pattern': r'[^\d.]', 'example': '100abc'},
                {'name': '为空', 'value': '', 'example': ''},
            ]
        },
        'age': {
            'valid': [
                {'name': '有效年龄', 'range': (1, 120), 'example': '25'},
                {'name': '最小年龄', 'value': '1', 'example': '1'},
                {'name': '最大年龄', 'value': '120', 'example': '120'},
            ],
            'invalid': [
                {'name': '负数年龄', 'pattern': r'^-\d+', 'example': '-1'},
                {'name': '零年龄', 'value': '0', 'example': '0'},
                {'name': '超限年龄', 'range': (121, 200), 'example': '150'},
                {'name': '非数字', 'pattern': r'[^\d]', 'example': 'abc'},
                {'name': '为空', 'value': '', 'example': ''},
            ]
        },
        'date': {
            'valid': [
                {'name': 'YYYY-MM-DD格式', 'pattern': r'^\d{4}-\d{2}-\d{2}$', 'example': '2024-01-01'},
                {'name': 'YYYY/MM/DD格式', 'pattern': r'^\d{4}/\d{2}/\d{2}$', 'example': '2024/01/01'},
            ],
            'invalid': [
                {'name': '格式错误', 'pattern': r'^\d{4}\d{2}\d{2}$', 'example': '20240101'},
                {'name': '非法月份', 'pattern': r'^\d{4}-1[3-9]-', 'example': '2024-13-01'},
                {'name': '非法日期', 'pattern': r'^\d{4}-\d{2}-3[2-9]', 'example': '2024-01-32'},
                {'name': '为空', 'value': '', 'example': ''},
            ]
        },
        'url': {
            'valid': [
                {'name': 'http协议', 'pattern': r'^http://', 'example': 'http://example.com'},
                {'name': 'https协议', 'pattern': r'^https://', 'example': 'https://example.com'},
            ],
            'invalid': [
                {'name': '缺少协议', 'pattern': r'^[^h]', 'example': 'example.com'},
                {'name': '非法协议', 'pattern': r'^ftp://', 'example': 'ftp://example.com'},
                {'name': '为空', 'value': '', 'example': ''},
            ]
        }
    }

    @staticmethod
    def detect_input_type(description: str) -> Optional[str]:
        """根据描述检测输入类型"""
        type_keywords = {
            'username': ['用户名', '账号', 'username', 'account', '登录名'],
            'password': ['密码', 'password', 'pwd', '口令'],
            'email': ['邮箱', 'email', '邮件', 'e-mail'],
            'phone': ['手机', '电话', 'phone', 'mobile', '联系方式'],
            'id_card': ['身份证', 'idcard', '证件号'],
            'amount': ['金额', '价格', 'amount', 'price', '费用', '钱'],
            'age': ['年龄', 'age', '岁数'],
            'date': ['日期', 'date', '时间', 'time', '出生日期'],
            'url': ['网址', 'url', '链接', 'link', '地址'],
        }

        for input_type, keywords in type_keywords.items():
            for keyword in keywords:
                if keyword.lower() in description.lower():
                    return input_type
        return None

    @staticmethod
    def generate_equivalence_test_cases(description: str, input_type: str = None) -> List[Dict]:
        """生成等价类测试用例"""
        if not input_type:
            input_type = EquivalenceClassAnalyzer.detect_input_type(description)

        if not input_type or input_type not in EquivalenceClassAnalyzer.INPUT_TYPE_RULES:
            return []

        rules = EquivalenceClassAnalyzer.INPUT_TYPE_RULES[input_type]
        test_cases = []

        # 有效等价类测试用例
        for idx, valid_rule in enumerate(rules['valid'], 1):
            test_cases.append({
                'id': f'EQ-V{idx:03d}',
                'type': '等价类-有效',
                'name': valid_rule['name'],
                'description': f"验证{input_type}的有效等价类：{valid_rule['name']}",
                'test_data': valid_rule.get('example', ''),
                'expected': '输入验证通过，系统正常处理',
                'priority': 'P1'
            })

        # 无效等价类测试用例
        for idx, invalid_rule in enumerate(rules['invalid'], 1):
            test_cases.append({
                'id': f'EQ-I{idx:03d}',
                'type': '等价类-无效',
                'name': invalid_rule['name'],
                'description': f"验证{input_type}的无效等价类：{invalid_rule['name']}",
                'test_data': invalid_rule.get('example', ''),
                'expected': '输入验证失败，提示相应错误信息',
                'priority': 'P2'
            })

        return test_cases


class BoundaryValueAnalyzer:
    """
    边界值分析法分析器
    在等价类边界上选取测试数据
    """

    @staticmethod
    def extract_boundary_info(description: str) -> Dict:
        """从描述中提取边界信息"""
        boundary_info = {
            'min': None,
            'max': None,
            'unit': None,
            'type': None
        }

        # 提取数字范围
        range_patterns = [
            r'(\d+)[-~到至](\d+)',  # 6-20, 6~20
            r'(\d+)到(\d+)',  # 6到20
            r'最少(\d+)',  # 最少6
            r'最多(\d+)',  # 最多20
            r'最小(\d+)',
            r'最大(\d+)',
            r'(\d+)位',  # 6位
            r'(\d+)个',  # 6个
        ]

        for pattern in range_patterns:
            match = re.search(pattern, description)
            if match:
                if len(match.groups()) >= 2:
                    boundary_info['min'] = int(match.group(1))
                    boundary_info['max'] = int(match.group(2))
                else:
                    num = int(match.group(1))
                    if '最少' in description or '最小' in description:
                        boundary_info['min'] = num
                    elif '最多' in description or '最大' in description:
                        boundary_info['max'] = num
                break

        # 提取单位
        if '位' in description:
            boundary_info['unit'] = '字符'
            boundary_info['type'] = 'length'
        elif '个' in description:
            boundary_info['unit'] = '个'
            boundary_info['type'] = 'count'
        elif '元' in description or '金额' in description:
            boundary_info['unit'] = '元'
            boundary_info['type'] = 'amount'
        elif '岁' in description or '年龄' in description:
            boundary_info['unit'] = '岁'
            boundary_info['type'] = 'age'

        return boundary_info

    @staticmethod
    def generate_boundary_test_cases(description: str, boundary_info: Dict = None) -> List[Dict]:
        """生成边界值测试用例"""
        if not boundary_info:
            boundary_info = BoundaryValueAnalyzer.extract_boundary_info(description)

        # 获取min和max，处理None情况
        min_val = boundary_info.get('min')
        max_val = boundary_info.get('max')

        if min_val is None and max_val is None:
            # 使用默认边界值规则
            default_boundaries = {
                'length': {'min': 1, 'max': 100},
                'count': {'min': 0, 'max': 100},
                'amount': {'min': 0.01, 'max': 99999.99},
                'age': {'min': 0, 'max': 120},
            }
            boundary_type = boundary_info.get('type', 'length')
            if boundary_type in default_boundaries:
                min_val = default_boundaries[boundary_type]['min']
                max_val = default_boundaries[boundary_type]['max']
            else:
                # 如果没有检测到边界信息，返回空列表
                return []
        elif min_val is None:
            min_val = 1
        elif max_val is None:
            max_val = 100

        unit = boundary_info.get('unit', '字符')

        # 边界值测试点：最小值-1、最小值、最小值+1、最大值-1、最大值、最大值+1
        boundary_points = [
            {'value': min_val - 1, 'type': '下边界-无效', 'valid': False, 'name': f'最小值-1 ({min_val-1}{unit})'},
            {'value': min_val, 'type': '下边界-有效', 'valid': True, 'name': f'最小值 ({min_val}{unit})'},
            {'value': min_val + 1, 'type': '下边界+1', 'valid': True, 'name': f'最小值+1 ({min_val+1}{unit})'},
            {'value': max_val - 1, 'type': '上边界-1', 'valid': True, 'name': f'最大值-1 ({max_val-1}{unit})'},
            {'value': max_val, 'type': '上边界-有效', 'valid': True, 'name': f'最大值 ({max_val}{unit})'},
            {'value': max_val + 1, 'type': '上边界-无效', 'valid': False, 'name': f'最大值+1 ({max_val+1}{unit})'},
        ]

        test_cases = []
        for idx, point in enumerate(boundary_points, 1):
            test_cases.append({
                'id': f'BV-{idx:03d}',
                'type': '边界值测试',
                'name': point['name'],
                'description': f"验证边界值：{point['type']}",
                'test_data': str(point['value']),
                'expected': '验证通过' if point['valid'] else '验证失败，提示超出范围',
                'priority': 'P0' if point['value'] in [min_val, max_val] else 'P1'
            })

        return test_cases


class ScenarioDesigner:
    """
    场景设计法分析器
    基于业务流程设计测试场景
    """

    # 常见业务场景模板
    SCENARIO_TEMPLATES = {
        'login': {
            'name': '登录场景',
            'flows': [
                {'name': '正常登录', 'steps': ['输入正确用户名', '输入正确密码', '点击登录'], 'expected': '登录成功'},
                {'name': '用户名错误', 'steps': ['输入错误用户名', '输入正确密码', '点击登录'], 'expected': '提示用户不存在'},
                {'name': '密码错误', 'steps': ['输入正确用户名', '输入错误密码', '点击登录'], 'expected': '提示密码错误'},
                {'name': '账号锁定', 'steps': ['连续输入错误密码5次', '尝试登录'], 'expected': '提示账号已锁定'},
                {'name': '空输入', 'steps': ['用户名留空', '点击登录'], 'expected': '提示必填'},
                {'name': '记住密码', 'steps': ['勾选记住密码', '登录成功', '退出', '再次访问'], 'expected': '自动填充用户名'},
            ]
        },
        'register': {
            'name': '注册场景',
            'flows': [
                {'name': '正常注册', 'steps': ['填写完整信息', '提交注册'], 'expected': '注册成功'},
                {'name': '重复注册', 'steps': ['使用已存在账号注册'], 'expected': '提示账号已存在'},
                {'name': '信息不完整', 'steps': ['必填项留空', '提交'], 'expected': '提示必填项'},
                {'name': '验证码错误', 'steps': ['输入错误验证码', '提交'], 'expected': '提示验证码错误'},
                {'name': '协议未勾选', 'steps': ['不勾选用户协议', '提交'], 'expected': '提示需同意协议'},
            ]
        },
        'search': {
            'name': '搜索场景',
            'flows': [
                {'name': '精确搜索', 'steps': ['输入精确关键词', '点击搜索'], 'expected': '返回精确结果'},
                {'name': '模糊搜索', 'steps': ['输入部分关键词', '点击搜索'], 'expected': '返回相关结果'},
                {'name': '空搜索', 'steps': ['搜索框留空', '点击搜索'], 'expected': '提示或返回全部'},
                {'name': '特殊字符', 'steps': ['输入特殊字符', '点击搜索'], 'expected': '正确处理或提示'},
                {'name': '超长关键词', 'steps': ['输入超长关键词', '点击搜索'], 'expected': '截断或提示'},
            ]
        },
        'order': {
            'name': '下单场景',
            'flows': [
                {'name': '正常下单', 'steps': ['选择商品', '确认订单', '支付'], 'expected': '下单成功'},
                {'name': '库存不足', 'steps': ['选择库存为0商品'], 'expected': '提示库存不足'},
                {'name': '价格变动', 'steps': ['下单过程中价格变化'], 'expected': '提示价格变动'},
                {'name': '支付失败', 'steps': ['支付环节失败'], 'expected': '订单保留，提示重试'},
                {'name': '取消订单', 'steps': ['下单后取消'], 'expected': '订单取消成功'},
            ]
        },
        'upload': {
            'name': '上传场景',
            'flows': [
                {'name': '正常上传', 'steps': ['选择合规文件', '点击上传'], 'expected': '上传成功'},
                {'name': '格式限制', 'steps': ['选择不支持格式'], 'expected': '提示格式不支持'},
                {'name': '大小限制', 'steps': ['选择超大文件'], 'expected': '提示大小超限'},
                {'name': '空文件', 'steps': ['选择空文件'], 'expected': '提示或处理'},
                {'name': '批量上传', 'steps': ['选择多个文件', '上传'], 'expected': '批量上传成功'},
            ]
        },
        'export': {
            'name': '导出场景',
            'flows': [
                {'name': '正常导出', 'steps': ['选择数据', '点击导出'], 'expected': '导出成功'},
                {'name': '无数据导出', 'steps': ['无数据时导出'], 'expected': '提示无数据'},
                {'name': '大数据导出', 'steps': ['导出大量数据'], 'expected': '分批或提示等待'},
                {'name': '格式选择', 'steps': ['选择导出格式', '导出'], 'expected': '按格式导出'},
            ]
        }
    }

    @staticmethod
    def detect_scenario_type(description: str) -> Optional[str]:
        """检测场景类型"""
        type_keywords = {
            'login': ['登录', 'login', '登入', 'signin'],
            'register': ['注册', 'register', 'signup', '登记'],
            'search': ['搜索', '查询', 'search', '检索', '查找'],
            'order': ['下单', '订单', '购买', 'order', 'buy', '采购'],
            'upload': ['上传', 'upload', '导入', 'import'],
            'export': ['导出', 'export', '下载', 'download'],
        }

        for scenario_type, keywords in type_keywords.items():
            for keyword in keywords:
                if keyword.lower() in description.lower():
                    return scenario_type
        return None

    @staticmethod
    def generate_scenario_test_cases(description: str, scenario_type: str = None) -> List[Dict]:
        """生成场景测试用例"""
        if not scenario_type:
            scenario_type = ScenarioDesigner.detect_scenario_type(description)

        if not scenario_type or scenario_type not in ScenarioDesigner.SCENARIO_TEMPLATES:
            # 生成通用场景
            return ScenarioDesigner._generate_generic_scenario(description)

        template = ScenarioDesigner.SCENARIO_TEMPLATES[scenario_type]
        test_cases = []

        for idx, flow in enumerate(template['flows'], 1):
            steps_text = '\n'.join([f'{i+1}. {step}' for i, step in enumerate(flow['steps'])])
            test_cases.append({
                'id': f'SC-{idx:03d}',
                'type': '场景测试',
                'name': f"{template['name']}-{flow['name']}",
                'description': f"验证{template['name']}流程：{flow['name']}",
                'preconditions': '系统正常运行',
                'test_steps': steps_text,
                'expected': flow['expected'],
                'priority': 'P0' if idx <= 2 else 'P1'
            })

        return test_cases

    @staticmethod
    def _generate_generic_scenario(description: str) -> List[Dict]:
        """生成通用场景测试用例"""
        test_cases = [
            {
                'id': 'SC-001',
                'type': '场景测试',
                'name': '正常流程',
                'description': f'验证{description}的正常执行流程',
                'preconditions': '前置条件满足',
                'test_steps': '1. 准备测试数据\n2. 执行操作\n3. 验证结果',
                'expected': '操作成功完成',
                'priority': 'P0'
            },
            {
                'id': 'SC-002',
                'type': '场景测试',
                'name': '异常流程',
                'description': f'验证{description}的异常处理流程',
                'preconditions': '前置条件不满足或数据异常',
                'test_steps': '1. 准备异常数据\n2. 执行操作\n3. 验证错误处理',
                'expected': '系统正确处理异常，给出明确提示',
                'priority': 'P1'
            },
            {
                'id': 'SC-003',
                'type': '场景测试',
                'name': '中断流程',
                'description': f'验证{description}的中断恢复流程',
                'preconditions': '操作进行中',
                'test_steps': '1. 开始操作\n2. 中断操作\n3. 检查状态',
                'expected': '系统正确处理中断，数据不丢失',
                'priority': 'P2'
            }
        ]
        return test_cases


class ErrorGuessAnalyzer:
    """
    错误猜测法分析器
    基于经验猜测可能出错的地方
    """

    # 常见错误场景
    ERROR_SCENARIOS = [
        {'category': '输入错误', 'scenarios': [
            {'name': '空输入', 'description': '必填字段为空', 'test_data': '', 'expected': '提示必填'},
            {'name': '超长输入', 'description': '输入超出最大长度', 'test_data': '超长字符串...', 'expected': '截断或提示'},
            {'name': '特殊字符', 'description': '输入特殊字符', 'test_data': '!@#$%^&*()', 'expected': '正确处理'},
            {'name': '非法字符', 'description': '输入非法字符', 'test_data': '<script>alert(1)</script>', 'expected': '过滤或拒绝'},
            {'name': 'SQL注入', 'description': '尝试SQL注入', 'test_data': "' OR '1'='1", 'expected': '过滤或拒绝'},
            {'name': '格式错误', 'description': '输入格式不正确', 'test_data': '错误格式数据', 'expected': '提示格式错误'},
        ]},
        {'category': '并发错误', 'scenarios': [
            {'name': '并发操作', 'description': '多个用户同时操作同一数据', 'test_data': '并发请求', 'expected': '正确处理并发'},
            {'name': '重复提交', 'description': '快速重复提交表单', 'test_data': '重复点击', 'expected': '防重复提交'},
        ]},
        {'category': '权限错误', 'scenarios': [
            {'name': '无权限访问', 'description': '未登录访问需权限页面', 'test_data': '未登录', 'expected': '跳转登录'},
            {'name': '权限不足', 'description': '低权限用户访问高权限功能', 'test_data': '低权限账号', 'expected': '提示权限不足'},
        ]},
        {'category': '数据错误', 'scenarios': [
            {'name': '数据不存在', 'description': '访问不存在的数据', 'test_data': '无效ID', 'expected': '提示数据不存在'},
            {'name': '数据已删除', 'description': '访问已删除的数据', 'test_data': '已删除ID', 'expected': '提示或跳转'},
            {'name': '数据冲突', 'description': '数据唯一性冲突', 'test_data': '重复数据', 'expected': '提示已存在'},
        ]},
        {'category': '网络错误', 'scenarios': [
            {'name': '网络断开', 'description': '操作过程中网络断开', 'test_data': '断网', 'expected': '提示网络错误'},
            {'name': '请求超时', 'description': '请求响应超时', 'test_data': '超时场景', 'expected': '提示超时'},
        ]},
        {'category': '系统错误', 'scenarios': [
            {'name': '服务异常', 'description': '后端服务异常', 'test_data': '服务不可用', 'expected': '友好提示'},
            {'name': '资源耗尽', 'description': '系统资源不足', 'test_data': '高负载', 'expected': '限流或提示'},
        ]},
    ]

    @staticmethod
    def generate_error_test_cases(description: str) -> List[Dict]:
        """生成错误猜测测试用例"""
        test_cases = []
        tc_index = 1

        # 根据描述选择相关的错误场景
        relevant_categories = ErrorGuessAnalyzer._select_relevant_categories(description)

        for category_info in ErrorGuessAnalyzer.ERROR_SCENARIOS:
            if category_info['category'] in relevant_categories or not relevant_categories:
                for scenario in category_info['scenarios']:
                    test_cases.append({
                        'id': f'ER-{tc_index:03d}',
                        'type': '错误猜测',
                        'category': category_info['category'],
                        'name': scenario['name'],
                        'description': f"{scenario['description']}",
                        'test_data': scenario['test_data'],
                        'expected': scenario['expected'],
                        'priority': 'P2'
                    })
                    tc_index += 1

        return test_cases[:20]  # 限制数量

    @staticmethod
    def _select_relevant_categories(description: str) -> List[str]:
        """选择与描述相关的错误类别"""
        categories = []

        if any(kw in description for kw in ['输入', '填写', '提交', '表单']):
            categories.append('输入错误')
        if any(kw in description for kw in ['并发', '同时', '多用户']):
            categories.append('并发错误')
        if any(kw in description for kw in ['权限', '登录', '认证']):
            categories.append('权限错误')
        if any(kw in description for kw in ['数据', '记录', '信息']):
            categories.append('数据错误')
        if any(kw in description for kw in ['网络', '请求', '接口']):
            categories.append('网络错误')

        return categories


class RuleEngine:
    """
    综合规则引擎
    整合多种测试设计方法
    """

    @staticmethod
    def analyze_requirement(description: str) -> Dict:
        """综合分析需求描述"""
        result = {
            'input_type': EquivalenceClassAnalyzer.detect_input_type(description),
            'scenario_type': ScenarioDesigner.detect_scenario_type(description),
            'boundary_info': BoundaryValueAnalyzer.extract_boundary_info(description),
            'keywords': RuleEngine.extract_keywords(description),
            'priority': RuleEngine.determine_priority(description)
        }
        return result

    @staticmethod
    def generate_comprehensive_test_cases(description: str) -> List[Dict]:
        """生成综合测试用例"""
        all_test_cases = []

        # 1. 等价类划分测试用例
        eq_cases = EquivalenceClassAnalyzer.generate_equivalence_test_cases(description)
        all_test_cases.extend(eq_cases)

        # 2. 边界值分析测试用例
        bv_cases = BoundaryValueAnalyzer.generate_boundary_test_cases(description)
        all_test_cases.extend(bv_cases)

        # 3. 场景设计测试用例
        sc_cases = ScenarioDesigner.generate_scenario_test_cases(description)
        all_test_cases.extend(sc_cases)

        # 4. 错误猜测测试用例
        er_cases = ErrorGuessAnalyzer.generate_error_test_cases(description)
        all_test_cases.extend(er_cases)

        return all_test_cases

    @staticmethod
    def extract_keywords(text: str) -> List[str]:
        """提取关键词"""
        keywords = []
        important_words = ['用户', '登录', '注册', '查询', '添加', '删除', '修改', '更新',
                          '验证', '检查', '输入', '提交', '取消', '确认', '重置', '导出', '导入',
                          '搜索', '筛选', '排序', '分页', '上传', '下载', '支付', '订单']
        for word in important_words:
            if word in text:
                keywords.append(word)
        return keywords

    @staticmethod
    def determine_priority(description: str) -> str:
        """确定优先级"""
        high_priority_keywords = ['核心', '主要', '重要', '必须', '关键', 'p0', 'P0', '紧急', '安全']
        medium_priority_keywords = ['一般', '普通', '常规', '次要', 'p1', 'P1', '优化']

        for keyword in high_priority_keywords:
            if keyword in description:
                return 'P0'
        for keyword in medium_priority_keywords:
            if keyword in description:
                return 'P1'
        return 'P2'

    @staticmethod
    def generate_test_case_id(category: str, index: int) -> str:
        """生成测试用例ID"""
        prefix_map = {
            '等价类-有效': 'EQ-V',
            '等价类-无效': 'EQ-I',
            '边界值测试': 'BV',
            '场景测试': 'SC',
            '错误猜测': 'ER',
            '功能测试': 'FT',
            '异常测试': 'EX',
        }
        prefix = prefix_map.get(category, 'TC')
        return f"{prefix}-{index:03d}"