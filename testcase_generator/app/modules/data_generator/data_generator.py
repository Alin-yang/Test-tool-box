"""
测试数据生成器
提供各种测试数据的生成功能
"""
import random
import string
import datetime
from typing import Any, Dict, List, Union


class DataGenerator:
    """测试数据生成器"""
    
    # 常用姓名库 - 单姓
    FIRST_NAMES = ['张', '李', '王', '刘', '陈', '杨', '赵', '黄', '周', '吴',
                   '徐', '孙', '马', '朱', '胡', '郭', '何', '林', '罗', '高',
                   '梁', '郑', '谢', '宋', '唐', '许', '韩', '冯', '邓', '曹',
                   '彭', '曾', '肖', '田', '董', '袁', '潘', '于', '蒋', '蔡']
    
    # 双姓（复姓）
    DOUBLE_FIRST_NAMES = ['欧阳', '太史', '端木', '上官', '司马', '东方', 
                         '独孤', '南宫', '万俟', '闻人', '夏侯', '诸葛',
                         '尉迟', '公羊', '赫连', '澹台', '皇甫', '宗政',
                         '濮阳', '公冶', '太叔', '申屠', '公孙', '慕容']
    
    # 常用名字（单字）
    LAST_NAMES = ['伟', '强', '勇', '军', '涛', '明', '辉', '刚', '健', '强',
                  '敏', '静', '丽', '芳', '燕', '娜', '婷', '雪', '梅', '华',
                  '杰', '磊', '鹏', '飞', '超', '勇', '帅', '洋', '亮', '光']
    
    # 常用名字（双字）
    DOUBLE_LAST_NAMES = ['志强', '伟强', '丽娟', '秀英', '桂英', '建华',
                        '建国', '建军', '卫东', '晓东', '晓燕', '海燕',
                        '丽华', '红霞', '红梅', '玉兰', '秀兰', '桂兰',
                        '俊杰', '鹏飞', '志强', '卫东', '国栋', '海波']
    
    # 英文名字
    ENGLISH_FIRST_NAMES = ['John', 'Jane', 'Michael', 'Emily', 'David', 'Sarah',
                          'Robert', 'Jennifer', 'William', 'Jessica', 'James', 'Mary',
                          'Richard', 'Patricia', 'Joseph', 'Linda', 'Thomas', 'Barbara',
                          'Charles', 'Elizabeth', 'Daniel', 'Susan', 'Matthew', 'Jessica']
    
    ENGLISH_LAST_NAMES = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia',
                         'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez',
                         'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore',
                         'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson', 'White']
    
    # 常用邮箱域名
    EMAIL_DOMAINS = ['qq.com', '163.com', '126.com', 'gmail.com', 'hotmail.com',
                     'yahoo.com', 'sina.com', 'sohu.com', '139.com', 'outlook.com']
    
    # 常用城市
    CITIES = ['北京', '上海', '广州', '深圳', '杭州', '南京', '成都', '武汉', '西安', '重庆',
              '天津', '苏州', '郑州', '长沙', '沈阳', '青岛', '济南', '哈尔滨', '福州', '合肥']
    
    # 地址数据
    PROVINCES = ['北京市', '上海市', '广东省', '江苏省', '浙江省', '山东省', '四川省', '湖北省', 
                 '河南省', '湖南省', '福建省', '安徽省', '河北省', '辽宁省', '陕西省', '重庆市']
    
    DISTRICTS = ['朝阳区', '海淀区', '西城区', '东城区', '浦东新区', '徐汇区', '黄埔区', 
                 '天河区', '越秀区', '福田区', '南山区', '西湖区', '江干区', '玄武区', '鼓楼区']
    
    STREETS = ['大街', '路', '胡同', '巷', '道', '弄', '支路', '街']
    
    BUILDINGS = ['小区', '大厦', '公寓', '花园', '广场', '中心', '楼', '苑', '居']
    
    STREET_NAMES = ['长安', '建国', '新华', '人民', '中山', '解放', '胜利', '东风', 
                   '光明', '朝阳', '幸福', '平安', '健康', '和谐', '团结', '友爱']
    
    @staticmethod
    def generate_name() -> str:
        """生成随机姓名（支持中文2-4字、英文姓名）"""
        # 随机选择姓名类型
        name_type = random.choices(['chinese_2', 'chinese_3', 'chinese_4', 'english'], 
                                  weights=[40, 30, 10, 20])[0]
        
        if name_type == 'chinese_2':
            # 两字中文姓名（单姓+单字名）
            first = random.choice(DataGenerator.FIRST_NAMES)
            last = random.choice(DataGenerator.LAST_NAMES)
            return first + last
        elif name_type == 'chinese_3':
            # 三字中文姓名（单姓+双字名）
            first = random.choice(DataGenerator.FIRST_NAMES)
            last = random.choice(DataGenerator.DOUBLE_LAST_NAMES)
            return first + last
        elif name_type == 'chinese_4':
            # 四字中文姓名（复姓+双字名）
            first = random.choice(DataGenerator.DOUBLE_FIRST_NAMES)
            last = random.choice(DataGenerator.DOUBLE_LAST_NAMES)
            return first + last
        else:
            # 英文姓名
            first = random.choice(DataGenerator.ENGLISH_FIRST_NAMES)
            last = random.choice(DataGenerator.ENGLISH_LAST_NAMES)
            return f"{first} {last}"
    
    @staticmethod
    def generate_mac_address() -> str:
        """生成随机MAC地址"""
        hex_chars = '0123456789ABCDEF'
        return ':'.join(''.join(random.choices(hex_chars, k=2)) for _ in range(6))
    
    @staticmethod
    def generate_phone() -> str:
        """生成随机手机号"""
        prefix = ['138', '139', '137', '136', '135', '134', '159', '158', '157', '150',
                  '151', '152', '188', '187', '186', '185', '189', '178', '177', '176']
        return random.choice(prefix) + ''.join(random.choices('0123456789', k=8))
    
    @staticmethod
    def generate_email() -> str:
        """生成随机邮箱"""
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        domain = random.choice(DataGenerator.EMAIL_DOMAINS)
        return f"{username}@{domain}"
    
    @staticmethod
    def generate_id_card() -> str:
        """生成随机身份证号"""
        province = ['11', '12', '13', '14', '15', '21', '22', '23', '31', '32',
                    '33', '34', '35', '36', '37', '41', '42', '43', '44', '45',
                    '46', '50', '51', '52', '53', '54', '61', '62', '63', '64', '65']
        year = str(random.randint(1970, 2005))
        month = str(random.randint(1, 12)).zfill(2)
        day = str(random.randint(1, 28)).zfill(2)
        seq = ''.join(random.choices('0123456789', k=3))
        check_code = random.choice('0123456789X')
        return f"{random.choice(province)}{year}{month}{day}{seq}{check_code}"
    
    @staticmethod
    def generate_ip() -> str:
        """生成随机IP地址"""
        return '.'.join(str(random.randint(1, 254)) for _ in range(4))
    
    @staticmethod
    def generate_url() -> str:
        """生成随机URL"""
        protocols = ['http://', 'https://']
        domains = ['example.com', 'test.com', 'api.com', 'service.com', 'app.com']
        paths = ['/api/user', '/api/data', '/v1/login', '/v2/query', '/search']
        return f"{random.choice(protocols)}{random.choice(domains)}{random.choice(paths)}"
    
    @staticmethod
    def generate_string(length: int = 10) -> str:
        """生成随机字符串"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    @staticmethod
    def generate_int(min_val: int = 0, max_val: int = 100) -> int:
        """生成随机整数"""
        return random.randint(min_val, max_val)
    
    @staticmethod
    def generate_float(min_val: float = 0.0, max_val: float = 100.0) -> float:
        """生成随机浮点数"""
        return round(random.uniform(min_val, max_val), 2)
    
    @staticmethod
    def generate_date(start_year: int = 2020, end_year: int = 2025) -> str:
        """生成随机日期"""
        year = random.randint(start_year, end_year)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        return f"{year}-{month:02d}-{day:02d}"
    
    @staticmethod
    def generate_datetime() -> str:
        """生成随机日期时间"""
        now = datetime.datetime.now()
        delta = datetime.timedelta(days=random.randint(-365, 365), 
                                   hours=random.randint(0, 23),
                                   minutes=random.randint(0, 59),
                                   seconds=random.randint(0, 59))
        return (now + delta).strftime('%Y-%m-%d %H:%M:%S')
    
    @staticmethod
    def generate_bool() -> bool:
        """生成随机布尔值"""
        return random.choice([True, False])
    
    @staticmethod
    def generate_list(item_generator, count: int = 5) -> List[Any]:
        """生成随机列表"""
        return [item_generator() for _ in range(count)]
    
    @staticmethod
    def generate_boundary_string(length: int = 10) -> Dict[str, str]:
        """生成边界值字符串"""
        return {
            'empty': '',
            'min_1': 'a',
            'min_boundary': 'a' * (length - 1),
            'normal': 'a' * length,
            'max_boundary': 'a' * (length + 1),
            'max_10': 'a' * 10,
            'max_100': 'a' * 100,
            'max_500': 'a' * 500,
            'special_chars': '!@#$%^&*()_+-=[]{}|;:,.<>?',
            'sql_injection': "' OR '1'='1",
            'xss': '<script>alert("test")</script>',
            'unicode': '测试中文'
        }
    
    @staticmethod
    def generate_boundary_number(min_val: int = 0, max_val: int = 100) -> Dict[str, Union[int, float]]:
        """生成边界值数字"""
        return {
            'negative': -1,
            'zero': 0,
            'min': min_val,
            'min_plus_1': min_val + 1,
            'normal': random.randint(min_val + 1, max_val - 1),
            'max_minus_1': max_val - 1,
            'max': max_val,
            'max_plus_1': max_val + 1,
            'large_number': 999999999,
            'decimal': 1.5,
            'negative_decimal': -1.5
        }
    
    @staticmethod
    def generate_json_structure(fields: Dict[str, str]) -> Dict[str, Any]:
        """根据字段定义生成JSON结构"""
        result = {}
        type_map = {
            'string': DataGenerator.generate_string,
            'int': DataGenerator.generate_int,
            'float': DataGenerator.generate_float,
            'bool': DataGenerator.generate_bool,
            'date': DataGenerator.generate_date,
            'datetime': DataGenerator.generate_datetime,
            'email': DataGenerator.generate_email,
            'phone': DataGenerator.generate_phone,
            'id_card': DataGenerator.generate_id_card,
            'ip': DataGenerator.generate_ip,
            'url': DataGenerator.generate_url,
            'name': DataGenerator.generate_name
        }
        
        for field_name, field_type in fields.items():
            generator = type_map.get(field_type, DataGenerator.generate_string)
            result[field_name] = generator()
        
        return result
    
    @staticmethod
    def generate_address() -> str:
        """生成真实格式的地址"""
        province = random.choice(DataGenerator.PROVINCES)
        district = random.choice(DataGenerator.DISTRICTS)
        street_name = random.choice(DataGenerator.STREET_NAMES)
        street = random.choice(DataGenerator.STREETS)
        building_type = random.choice(DataGenerator.BUILDINGS)
        
        street_num = random.randint(1, 200)
        building_num = random.randint(1, 30)
        unit_num = random.randint(1, 10)
        room_num = random.randint(101, 999)
        
        address = f"{province}{district}{street_name}{street}{street_num}号{building_num}{building_type}{unit_num}单元{room_num}室"
        return address
    
    @staticmethod
    def generate_user() -> Dict[str, str]:
        """生成用户信息"""
        return {
            'name': DataGenerator.generate_name(),
            'phone': DataGenerator.generate_phone(),
            'email': DataGenerator.generate_email(),
            'id_card': DataGenerator.generate_id_card(),
            'city': random.choice(DataGenerator.CITIES),
            'address': DataGenerator.generate_address()
        }
    
    @staticmethod
    def generate_pagination_params() -> Dict[str, int]:
        """生成分页参数"""
        return {
            'page': random.randint(1, 100),
            'size': random.randint(1, 100),
            'total': random.randint(100, 10000)
        }
    
    @staticmethod
    def generate_search_params() -> Dict[str, Any]:
        """生成搜索参数"""
        return {
            'keyword': DataGenerator.generate_string(10),
            'start_date': DataGenerator.generate_date(),
            'end_date': DataGenerator.generate_date(),
            'status': random.choice(['0', '1', '2', '3']),
            'page': random.randint(1, 10),
            'size': random.randint(10, 50)
        }
