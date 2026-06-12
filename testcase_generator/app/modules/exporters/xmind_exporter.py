"""
XMind格式导出器 - 生成真正的.xmind文件（ZIP格式）
"""
from typing import List, Dict
import json
import zipfile
import io
import uuid


class XMindExporter:
    """导出功能测试用例为真正的XMind格式(.xmind)"""

    @staticmethod
    def export(test_cases: List[Dict], output_path: str):
        """导出测试用例为XMind文件"""
        # 创建ZIP文件内容
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            # 添加mimetype文件 - 必须是第一个且不压缩
            mimetype_info = zipfile.ZipInfo('mimetype')
            mimetype_info.compress_type = zipfile.ZIP_STORED
            zf.writestr(mimetype_info, 'application/xmind'.encode('utf-8'))
            
            # 添加content.xml
            content_xml = XMindExporter._create_content_xml(test_cases)
            zf.writestr('content.xml', content_xml.encode('utf-8'))
            
            # 添加metadata.xml
            metadata_xml = XMindExporter._create_metadata_xml()
            zf.writestr('metadata.xml', metadata_xml.encode('utf-8'))
            
            # 添加styles.xml
            styles_xml = XMindExporter._create_styles_xml()
            zf.writestr('styles.xml', styles_xml.encode('utf-8'))
            
            # 添加markers.xml（优先级图标）
            markers_xml = XMindExporter._create_markers_xml()
            zf.writestr('markers.xml', markers_xml.encode('utf-8'))
            
            # 创建sheet目录
            sheet_id = uuid.uuid4().hex[:8]
            zf.writestr(f'sheets/sheet{sheet_id}.xml', XMindExporter._create_sheet_xml(test_cases, sheet_id).encode('utf-8'))
        
        # 写入文件
        with open(output_path, 'wb') as f:
            f.write(zip_buffer.getvalue())

    @staticmethod
    def _create_content_xml(test_cases: List[Dict]) -> str:
        """创建content.xml"""
        sheet_id = uuid.uuid4().hex[:8]
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<xmap-content xmlns="urn:xmind:xmap:xmlns:content:2.0" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:svg="http://www.w3.org/2000/svg" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:xlink="http://www.w3.org/1999/xlink">
    <sheet id="sheet{sheet_id}" title="测试用例">
        <topic id="root-{sheet_id}" timestamp="0">
            <title>测试用例</title>
            {XMindExporter._create_topics_xml(test_cases)}
        </topic>
    </sheet>
</xmap-content>'''

    @staticmethod
    def _create_topics_xml(test_cases: List[Dict]) -> str:
        """创建主题XML"""
        topics = []
        for idx, tc in enumerate(test_cases):
            tc_id = f'tc{idx+1}'
            title = tc.get('name', tc.get('title', '未命名用例'))
            # 转义特殊字符
            title = XMindExporter._escape_xml(title)
            priority = tc.get('priority', 'P2')
            
            # 优先级图标
            priority_marker = ''
            if priority == 'P0':
                priority_marker = '<marker-ref marker-id="priority-1"/>'
            elif priority == 'P1':
                priority_marker = '<marker-ref marker-id="priority-2"/>'
            
            desc = XMindExporter._escape_xml(tc.get('description', ''))
            preconditions = XMindExporter._escape_xml(tc.get('preconditions', ''))
            expected = XMindExporter._escape_xml(tc.get('expected', ''))
            test_type = XMindExporter._escape_xml(tc.get('type', tc.get('test_type', '功能测试')))
            
            topics.append(f'''<topic id="{tc_id}" timestamp="0">
    <title>{title}</title>
    {priority_marker}
    <topic id="{tc_id}-id" timestamp="0">
        <title>用例ID: {XMindExporter._escape_xml(tc.get('id', ''))}</title>
    </topic>
    <topic id="{tc_id}-priority" timestamp="0">
        <title>优先级: {priority}</title>
    </topic>
    <topic id="{tc_id}-type" timestamp="0">
        <title>类型: {test_type}</title>
    </topic>
    <topic id="{tc_id}-desc" timestamp="0">
        <title>描述: {desc}</title>
    </topic>
    <topic id="{tc_id}-pre" timestamp="0">
        <title>前置条件: {preconditions}</title>
    </topic>
    <topic id="{tc_id}-steps" timestamp="0">
        <title>测试步骤</title>
        {XMindExporter._create_steps_xml(tc.get('test_steps', []), tc_id)}
    </topic>
    <topic id="{tc_id}-data" timestamp="0">
        <title>测试数据</title>
        {XMindExporter._create_test_data_xml(tc.get('test_data', {}), tc_id)}
    </topic>
    <topic id="{tc_id}-expected" timestamp="0">
        <title>预期结果: {expected}</title>
    </topic>
</topic>''')
        
        return '\n'.join(topics)

    @staticmethod
    def _create_steps_xml(steps: List, tc_id: str) -> str:
        """创建测试步骤XML"""
        if not isinstance(steps, list):
            return ''
        
        step_elements = []
        for idx, step in enumerate(steps, 1):
            if isinstance(step, dict):
                action = XMindExporter._escape_xml(step.get('action', ''))
                expected = XMindExporter._escape_xml(step.get('expected', ''))
                step_elements.append(f'''<topic id="{tc_id}-step{idx}" timestamp="0">
    <title>步骤{idx}: {action}</title>
    <topic id="{tc_id}-step{idx}-exp" timestamp="0">
        <title>预期: {expected}</title>
    </topic>
</topic>''')
            elif isinstance(step, str):
                step_elements.append(f'''<topic id="{tc_id}-step{idx}" timestamp="0">
    <title>步骤{idx}: {XMindExporter._escape_xml(step)}</title>
</topic>''')
        
        return '\n'.join(step_elements)

    @staticmethod
    def _create_test_data_xml(test_data, tc_id: str) -> str:
        """创建测试数据XML"""
        data_elements = []
        
        if isinstance(test_data, dict):
            for idx, (key, value) in enumerate(test_data.items(), 1):
                data_elements.append(f'''<topic id="{tc_id}-data{idx}" timestamp="0">
    <title>{XMindExporter._escape_xml(str(key))}: {XMindExporter._escape_xml(str(value))}</title>
</topic>''')
        elif isinstance(test_data, str):
            data_elements.append(f'''<topic id="{tc_id}-data1" timestamp="0">
    <title>{XMindExporter._escape_xml(test_data)}</title>
</topic>''')
        
        return '\n'.join(data_elements)

    @staticmethod
    def _create_metadata_xml() -> str:
        """创建metadata.xml"""
        return '''<?xml version="1.0" encoding="UTF-8"?>
<metadata xmlns="urn:xmind:xmap:xmlns:metadata:2.0">
    <creator>Test Case Generator</creator>
    <created>2024-01-01T00:00:00Z</created>
    <modified>2024-01-01T00:00:00Z</modified>
</metadata>'''

    @staticmethod
    def _create_styles_xml() -> str:
        """创建styles.xml"""
        return '''<?xml version="1.0" encoding="UTF-8"?>
<styles xmlns="urn:xmind:xmap:xmlns:style:2.0">
    <style id="default" type="topic">
        <property name="font-family">Microsoft YaHei</property>
        <property name="font-size">12</property>
        <property name="font-color">#000000</property>
    </style>
</styles>'''

    @staticmethod
    def _create_markers_xml() -> str:
        """创建markers.xml（优先级图标）"""
        return '''<?xml version="1.0" encoding="UTF-8"?>
<markers xmlns="urn:xmind:xmap:xmlns:marker:2.0">
    <marker id="priority-1" marker-type="priority" modified="0">
        <properties>
            <property name="style">1</property>
        </properties>
    </marker>
    <marker id="priority-2" marker-type="priority" modified="0">
        <properties>
            <property name="style">2</property>
        </properties>
    </marker>
    <marker id="priority-3" marker-type="priority" modified="0">
        <properties>
            <property name="style">3</property>
        </properties>
    </marker>
</markers>'''

    @staticmethod
    def _create_sheet_xml(test_cases: List[Dict], sheet_id: str) -> str:
        """创建sheet XML"""
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<sheet xmlns="urn:xmind:xmap:xmlns:content:2.0" id="sheet{sheet_id}">
    <topic id="root-{sheet_id}" timestamp="0">
        <title>测试用例</title>
        {XMindExporter._create_topics_xml(test_cases)}
    </topic>
</sheet>'''

    @staticmethod
    def _escape_xml(text: str) -> str:
        """转义XML特殊字符"""
        if not text:
            return ''
        text = str(text)
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&apos;')
        return text
