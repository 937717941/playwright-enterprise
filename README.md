# xxxxxx系统 UI 自动化测试

基于 Playwright + Python + pytest 的企业级 UI 自动化测试框架。

## 项目结构

```
jiang-coal-automation/
├── configs/              # 配置文件
│   ├── settings.py      # 全局配置管理
│   └── dev.json         # 开发环境配置
├── data/                # 测试数据
│   └── users/          # 用户数据
│       └── users.json
├── pages/              # 页面对象（POM）
│   ├── base/           # 基础页面类
│   │   └── base_page.py
│   ├── web/            # Web端页面
│   │   └── login_page.py
│   └── mobile/         # 移动端页面
├── components/         # 可复用组件
├── utils/              # 工具类
├── tests/              # 测试用例
│   ├── web/            # Web端测试
│   │   └── test_login.py
│   ├── mobile/         # 移动端测试
│   └── conftest.py     # pytest配置
├── reports/            # 测试报告
├── screenshots/         # 失败截图
├── traces/              # Trace文件
├── jenkins/             # Jenkins配置
│   └── Jenkinsfile
├── requirements.txt     # Python依赖
├── pytest.ini           # pytest配置
└── README.md
```

## 快速开始

### 1. 安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd jiang-coal-automation

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 安装Playwright浏览器
playwright install chromium --with-deps
```

### 2. 配置环境

编辑 `configs/dev.json` 修改测试环境URL：

```json
{
  "dev": {
    "base_url": "https://testerp.xjcec.com"
  }
}
```

### 3. 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行冒烟测试
pytest tests/ -m smoke

# 运行Web端测试
pytest tests/web/ -m web

# 运行移动端测试
pytest tests/mobile/ -m mobile

# 并行执行（需要pytest-xdist）
pytest tests/ -n 4

# 生成HTML报告
pytest tests/ --html=reports/report.html --self-contained-html
```

### 4. 常用命令

```bash
# 安装依赖
make install

# 运行测试
make test

# 运行冒烟测试
make test-smoke

# 运行所有浏览器
make test-all

# 代码检查
make lint

# 代码格式化
make format

# 生成报告
make report

# 清理临时文件
make clean
```

## 测试标记

| 标记 | 说明 |
|-----|------|
| `@pytest.mark.smoke` | 冒烟测试，每次提交必跑 |
| `@pytest.mark.regression` | 回归测试，全量回归时运行 |
| `@pytest.mark.web` | Web端测试 |
| `@pytest.mark.mobile` | 移动端H5测试 |
| `@pytest.mark.slow` | 执行时间较长的测试 |
| `@pytest.mark.flaky` | 不稳定测试，需要重试 |

## 页面对象模型 (POM)

每个页面对应一个Python类，继承自 `BasePage`：

```python
from pages.base.base_page import BasePage

class LoginPage(BasePage):
    USERNAME_INPUT = '#username'

    def login(self, username, password):
        self.fill(self.USERNAME_INPUT, username)
        self.click('.login-btn')
```

## 登录态复用

首次登录后会自动保存 `auth.json`，后续测试直接复用登录状态：

```python
# conftest.py 中已配置
@pytest.fixture(scope="function")
def authenticated_page(page):
    # 自动加载或创建 auth.json
    ...
```

## CI/CD

### Jenkins

使用 `jenkins/Jenkinsfile` 配置Jenkins流水线：

- PR触发：冒烟测试
- Main分支：完整回归
- 定时任务：每日夜间回归

### 本地Jenkins配置

1. 创建新的Jenkins Pipeline项目
2. 配置源码管理为Git，指向本仓库
3. 在Pipeline配置中使用 `jenkins/Jenkinsfile`
4. 配置HTML Publisher插件显示测试报告

## 测试报告

测试报告输出到 `reports/` 目录：

- `report.html` - HTML测试报告
- `junit.xml` - JUnit格式报告（用于CI集成）

## 常见问题

### 1. 浏览器驱动问题

```bash
# 重新安装浏览器
playwright install chromium
playwright install --force
```

### 2. 依赖安装失败

```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. 截图乱码

确保系统安装了中文字体：

```bash
# Ubuntu/Debian
apt-get install fonts-wqy-microhei fonts-wqy-zenhei

# macOS
brew install font-wqy-microhei
```

## 联系方式

- 项目负责人：[姓名]
- 测试团队：[团队]
