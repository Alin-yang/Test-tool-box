"""
测试用例自动生成工具 - 启动入口
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    print("=" * 50)
    print("测试用例自动生成工具已启动")
    print("访问地址: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
