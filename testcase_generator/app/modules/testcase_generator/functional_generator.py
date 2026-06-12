"""
功能测试用例生成器 - 使用增强的规则引擎
"""
from typing import List, Dict
from .rule_engine import (
    RuleEngine, 
    EquivalenceClassAnalyzer, 
    BoundaryValueAnalyzer, 
    ScenarioDesigner, 
    ErrorGuessAnalyzer
)


class FunctionalGenerator:
    """生成功能测试用例 - 集成多种测试设计方法"""

    @staticmethod
    def generate(requirements: List[Dict]) -> List[Dict]:
        """
        根据需求生成全面的测试用例
        使用等价类、边界值、场景设计、错误猜测等方法
        """
        all_test_cases = []
        global_index = 1

        for req in requirements:
            desc = req.get('description', '')
            
            # 分析需求
            analysis = RuleEngine.analyze_requirement(desc)
            
            # 1. 等价类划分测试用例
            eq_cases = EquivalenceClassAnalyzer.generate_equivalence_test_cases(desc)
            for tc in eq_cases:
                tc['requirement'] = desc[:100]
                tc['id'] = FunctionalGenerator._adjust_id(tc['id'], global_index)
                all_test_cases.append(tc)
                global_index += 1

            # 2. 边界值分析测试用例
            bv_cases = BoundaryValueAnalyzer.generate_boundary_test_cases(desc)
            for tc in bv_cases:
                tc['requirement'] = desc[:100]
                tc['id'] = FunctionalGenerator._adjust_id(tc['id'], global_index)
                all_test_cases.append(tc)
                global_index += 1

            # 3. 场景设计测试用例
            sc_cases = ScenarioDesigner.generate_scenario_test_cases(desc)
            for tc in sc_cases:
                tc['requirement'] = desc[:100]
                tc['id'] = FunctionalGenerator._adjust_id(tc['id'], global_index)
                all_test_cases.append(tc)
                global_index += 1

            # 4. 错误猜测测试用例
            er_cases = ErrorGuessAnalyzer.generate_error_test_cases(desc)
            for tc in er_cases:
                tc['requirement'] = desc[:100]
                tc['id'] = FunctionalGenerator._adjust_id(tc['id'], global_index)
                all_test_cases.append(tc)
                global_index += 1

            # 5. 功能基础测试用例
            base_cases = FunctionalGenerator._generate_base_cases(desc, analysis)
            for tc in base_cases:
                tc['requirement'] = desc[:100]
                tc['id'] = FunctionalGenerator._adjust_id(tc['id'], global_index)
                all_test_cases.append(tc)
                global_index += 1

        # 去重并排序
        unique_cases = FunctionalGenerator._deduplicate_cases(all_test_cases)
        return FunctionalGenerator._sort_by_priority(unique_cases)

    @staticmethod
    def _generate_base_cases(description: str, analysis: Dict) -> List[Dict]:
        """生成基础功能测试用例"""
        test_cases = []
        keywords = analysis.get('keywords', [])
        priority = analysis.get('priority', 'P2')

        # 正向测试
        test_cases.append({
            'id': 'FT-001',
            'type': '功能测试',
            'name': f'正向验证-{description[:30]}',
            'description': f'验证功能正常执行：{description}',
            'preconditions': '1. 系统正常运行\n2. 用户已登录\n3. 测试数据已准备',
            'test_steps': [
                {'step': 1, 'action': '进入功能页面', 'expected': '页面正常加载'},
                {'step': 2, 'action': '输入有效数据', 'expected': '数据验证通过'},
                {'step': 3, 'action': '执行操作', 'expected': '操作成功执行'},
                {'step': 4, 'action': '验证结果', 'expected': '结果符合预期'}
            ],
            'test_data': {'input': '有效测试数据', 'expected_output': '预期结果'},
            'expected': '功能正常执行，结果正确',
            'priority': priority,
            'keywords': keywords
        })

        # 逆向测试
        test_cases.append({
            'id': 'FT-002',
            'type': '功能测试',
            'name': f'逆向验证-{description[:30]}',
            'description': f'验证功能异常处理：{description}',
            'preconditions': '1. 系统正常运行',
            'test_steps': [
                {'step': 1, 'action': '进入功能页面', 'expected': '页面正常加载'},
                {'step': 2, 'action': '输入无效数据', 'expected': '数据验证失败'},
                {'step': 3, 'action': '执行操作', 'expected': '操作被拒绝'},
                {'step': 4, 'action': '验证提示', 'expected': '错误提示清晰'}
            ],
            'test_data': {'input': '无效测试数据', 'expected_output': '错误提示'},
            'expected': '系统正确处理异常，提示清晰',
            'priority': 'P1',
            'keywords': keywords
        })

        # UI测试
        test_cases.append({
            'id': 'UI-001',
            'type': 'UI测试',
            'name': f'界面验证-{description[:30]}',
            'description': f'验证界面显示正确：{description}',
            'preconditions': '1. 系统正常运行',
            'test_steps': [
                {'step': 1, 'action': '进入功能页面', 'expected': '页面正常加载'},
                {'step': 2, 'action': '检查界面元素', 'expected': '元素完整显示'},
                {'step': 3, 'action': '检查布局样式', 'expected': '布局正确无错位'},
                {'step': 4, 'action': '检查交互响应', 'expected': '交互正常'}
            ],
            'test_data': {},
            'expected': '界面显示正确，交互流畅',
            'priority': 'P2',
            'keywords': keywords
        })

        return test_cases

    @staticmethod
    def _adjust_id(original_id: str, global_index: int) -> str:
        """调整用例ID确保唯一性"""
        return f"{original_id.split('-')[0]}-{global_index:04d}"

    @staticmethod
    def _deduplicate_cases(test_cases: List[Dict]) -> List[Dict]:
        """去除重复的测试用例"""
        seen = set()
        unique_cases = []
        for tc in test_cases:
            # 将字典转换为字符串作为key，因为字典不可哈希
            test_data = tc.get('test_data', '')
            if isinstance(test_data, dict):
                test_data = str(test_data)
            key = (tc.get('type', ''), tc.get('name', ''), test_data)
            if key not in seen:
                seen.add(key)
                unique_cases.append(tc)
        return unique_cases

    @staticmethod
    def _sort_by_priority(test_cases: List[Dict]) -> List[Dict]:
        """按优先级排序"""
        priority_order = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}
        return sorted(test_cases, key=lambda x: priority_order.get(x.get('priority', 'P2'), 2))