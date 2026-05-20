# Jenkins CI/CD 配置指南

本文档详细介绍如何配置 Jenkins 来运行疆煤宝自动化测试。

## 📋 目录

- [快速开始](#快速开始)
- [安装 Jenkins](#安装-jenkins)
- [配置 Jenkins](#配置-jenkins)
- [创建 Pipeline 任务](#创建-pipeline-任务)
- [常用操作](#常用操作)
- [故障排查](#故障排查)

## 🚀 快速开始

### 方式一：使用 Docker 快速启动（推荐）

```bash
# 进入 jenkins 目录
cd jiang-coal-automation/jenkins

# 启动 Jenkins
docker-compose up -d

# 查看日志
docker-compose logs -f jenkins

# 访问 Jenkins
open http://localhost:8080
```

**默认账号**：admin / admin123

### 方式二：手动安装

1. 下载 Jenkins LTS 版本：https://www.jenkins.io/download/
2. 安装推荐的插件
3. 安装额外插件（见下文）

## 🔧 安装 Jenkins

### 系统要求

- **操作系统**：Linux / macOS / Windows
- **Java**：JDK 11 或 JDK 17
- **内存**：至少 4GB RAM
- **磁盘**：至少 20GB 可用空间

### Docker 安装（推荐）

已为您准备好 `docker-compose.yml` 文件，包含：
- Jenkins LTS 服务
- Allure 报告服务
- 自动配置时区为亚洲/上海

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看容器状态
docker-compose ps
```

### 传统安装

#### Linux (Ubuntu/Debian)

```bash
# 安装 Java
sudo apt update
sudo apt install openjdk-17-jdk

# 安装 Jenkins
wget -q -O - https://pkg.jenkins.io/debian/jenkins.io.key | sudo apt-key add -
sudo sh -c 'echo deb http://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
sudo apt update
sudo apt install jenkins

# 启动 Jenkins
sudo systemctl start jenkins
sudo systemctl enable jenkins
```

#### macOS

```bash
# 使用 Homebrew 安装
brew install jenkins-lts

# 启动 Jenkins
brew services start jenkins-lts
```

#### Windows

1. 下载 Windows 安装包
2. 运行安装向导
3. 选择"使用本地系统账户运行"
4. 选择端口（默认 8080）

## ⚙️ 配置 Jenkins

### 1. 初始配置

1. 访问 `http://localhost:8080`
2. 输入初始密码（在控制台日志中）
3. 选择"安装推荐的插件"
4. 创建管理员账号

### 2. 安装必要插件

进入 **Manage Jenkins → Plugins → Available plugins**，安装：

#### 必需插件
- **Pipeline** - Pipeline 插件
- **Git** - Git 版本控制
- **GitHub** - GitHub 集成
- **Allure** - Allure 报告
- **HTML Publisher** - HTML 报告发布
- **Timestamper** - 时间戳
- **Workspace Cleanup** - 工作空间清理

#### 推荐插件
- **Blue Ocean** - 现代化 UI
- **Build Timeout** - 构建超时
- **Parameterized Trigger** - 参数化触发
- **DingTalk** - 钉钉通知（可选）
- **Email Extension** - 邮件通知（可选）

### 3. 配置全局工具

进入 **Manage Jenkins → Tools**：

#### Git
- 名称：`Default`
- 路径：`git`（或系统 git 路径）

#### Python（如果使用）
- 名称：`Python3`
- 路径：`/usr/bin/python3`（Linux）或 `python`（Windows）

#### Allure Commandline
- 名称：`Allure`
- 自动安装：勾选
- 版本：选择最新版本

### 4. 配置系统设置

进入 **Manage Jenkins → System**：

#### 时区设置
- 找到 **Locale** 部分
- 设置时区为：`Asia/Shanghai`

#### Allure 报告
- 找到 **Allure Report** 部分
- 配置 Allure Commandline 为上面创建的 `Allure`

## 📝 创建 Pipeline 任务

### 1. 创建冒烟测试任务

1. 点击 **New Item**
2. 输入名称：`jiang-coal-smoke-test`
3. 选择 **Pipeline**，点击 **OK**

#### 配置 General
- 描述：`疆煤宝自动化测试 - 冒烟测试`
- 勾选 **GitHub project**
  - Project url：`https://github.com/YOUR_USERNAME/jiang-coal-automation/`

#### 配置 Build Triggers
- 勾选 **GitHub hook trigger for GITScm polling**（Webhook 触发）
- 勾选 **Poll SCM**（定时轮询）
  - Schedule：`H/5 * * * *`（每5分钟检查一次）

#### 配置 Pipeline
- **Definition**：Pipeline script from SCM
- **SCM**：Git
  - Repository URL：`https://github.com/YOUR_USERNAME/jiang-coal-automation.git`
  - Credentials：添加 GitHub 凭证（如果使用私有仓库）
  - Branch Specifier：`*/main` 或 `*/master`
- **Script Path**：`jenkins/Jenkinsfile-smoke.groovy`

### 2. 创建回归测试任务

1. 点击 **New Item**
2. 输入名称：`jiang-coal-regression-test`
3. 选择 **Pipeline**，点击 **OK**

#### 配置 General
- 描述：`疆煤宝自动化测试 - 完整回归测试`
- 勾选 **This project is parameterized**（参数化构建）
  - 参数已在 Jenkinsfile 中定义，无需额外配置

#### 配置 Build Triggers
- 勾选 **Build periodically**（定时构建）
  - Schedule：`H 22 * * *`（每晚 22:00）

#### 配置 Pipeline
- **Definition**：Pipeline script from SCM
- **SCM**：Git
  - Repository URL：`https://github.com/YOUR_USERNAME/jiang-coal-automation.git`
- **Script Path**：`jenkins/Jenkinsfile-regression.groovy`

## 🎯 常用操作

### 手动触发构建

1. 进入任务页面
2. 点击 **Build Now**（冒烟测试）或 **Build with Parameters**（回归测试）
3. 选择参数（回归测试）
4. 点击 **Build**

### 查看测试报告

#### Allure 报告
1. 进入构建详情页
2. 点击 **Allure Report**
3. 查看详细的测试报告、趋势图、历史记录

#### HTML 报告
1. 进入构建详情页
2. 点击 **HTML Report**
3. 查看 pytest-html 生成的报告

### 查看失败截图

1. 进入构建详情页
2. 点击 **Artifacts**
3. 找到 `screenshots/` 目录
4. 下载查看失败截图

### 配置 GitHub Webhook（自动触发）

1. 进入 GitHub 仓库设置
2. 选择 **Settings → Webhooks → Add webhook**
3. 配置：
   - Payload URL：`http://YOUR_JENKINS_URL/github-webhook/`
   - Content type：`application/json`
   - Secret：（可选，用于安全验证）
   - Events：选择 **Just the push event**
4. 点击 **Add webhook**

## 🔍 故障排查

### 问题1：Jenkins 无法启动

**症状**：访问 8080 端口无响应

**解决方案**：
```bash
# 检查容器状态
docker-compose ps

# 查看日志
docker-compose logs jenkins

# 检查端口占用
netstat -an | grep 8080
```

### 问题2：Git 检出失败

**症状**：Pipeline 在 "检出代码" 阶段失败

**解决方案**：
1. 检查 Git 仓库 URL 是否正确
2. 如果是私有仓库，添加 GitHub 凭证
3. 检查网络连接

### 问题3：Python 环境错误

**症状**：提示 `python3: command not found`

**解决方案**：
1. 在 Jenkins 容器中安装 Python
2. 或使用 Jenkins 节点的 Python 路径
3. 修改 Jenkinsfile 中的 Python 命令

### 问题4：Playwright 浏览器安装失败

**症状**：提示 `playwright install` 失败

**解决方案**：
```bash
# 手动安装浏览器
.docker exec -it jiang-coal-jenkins bash
playwright install chromium
```

### 问题5：Allure 报告无法显示

**症状**：Allure Report 页面空白

**解决方案**：
1. 检查 Allure 插件是否安装
2. 检查 Allure Commandline 是否配置
3. 检查 `allure-results` 目录是否存在

## 📊 监控和维护

### 查看构建历史

- 进入任务页面
- 查看 **Build History**
- 点击构建号查看详情

### 配置构建保留策略

在 Jenkinsfile 中已配置：
```groovy
options {
    buildDiscarder(logRotator(numToKeepStr: '10'))  // 保留最近10次构建
}
```

### 备份 Jenkins

```bash
# 备份 Jenkins 主目录
tar -czvf jenkins-backup-$(date +%Y%m%d).tar.gz /var/jenkins_home

# 如果使用 Docker
docker run --rm --volumes-from jiang-coal-jenkins \
  -v $(pwd):/backup alpine \
  tar czf /backup/jenkins-backup.tar.gz /var/jenkins_home
```

## 📞 获取帮助

- Jenkins 官方文档：https://www.jenkins.io/doc/
- Playwright 文档：https://playwright.dev/python/
- pytest 文档：https://docs.pytest.org/
- Allure 文档：https://docs.qameta.io/allure/

## 📝 更新日志

### 2024-XX-XX
- 初始版本
- 配置冒烟测试和回归测试 Pipeline
- 集成 Allure 报告
- 添加 Docker 部署方案
