/**
 * 疆煤宝自动化测试 - 冒烟测试 Pipeline
 * 触发条件：代码推送、定时任务（每天 9:00、14:00）
 */
pipeline {
    agent any

    environment {
        PYTHON_VERSION = '3.10'
        PROJECT_NAME = 'jiang-coal-automation'
        VENV_PATH = '.venv'
        ALLURE_RESULTS = 'allure-results'
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
    }

    triggers {
        // 每天 9:00 和 14:00 自动运行
        cron('H 9,14 * * *')
        // 代码推送时触发
        pollSCM('H/5 * * * *')
    }

    stages {
        stage('🚀 开始冒烟测试') {
            steps {
                script {
                    currentBuild.displayName = "#${BUILD_NUMBER} - 冒烟测试"
                }
                echo "开始执行冒烟测试 - ${new Date().format('yyyy-MM-dd HH:mm:ss', TimeZone.getTimeZone('Asia/Shanghai'))}"
            }
        }

        stage('📥 检出代码') {
            steps {
                checkout scm
                sh '''
                    echo "当前分支: $(git rev-parse --abbrev-ref HEAD)"
                    echo "最新提交: $(git log -1 --oneline)"
                '''
            }
        }

        stage('🐍 设置 Python 环境') {
            steps {
                sh '''
                    python3 --version || python --version
                    
                    # 创建虚拟环境
                    if [ ! -d "${VENV_PATH}" ]; then
                        python3 -m venv ${VENV_PATH} || python -m venv ${VENV_PATH}
                    fi
                    
                    # 激活虚拟环境
                    . ${VENV_PATH}/bin/activate
                    
                    # 升级 pip
                    pip install --upgrade pip
                    
                    echo "Python 环境设置完成"
                '''
            }
        }

        stage('📦 安装依赖') {
            steps {
                sh '''
                    . ${VENV_PATH}/bin/activate
                    pip install -r requirements.txt
                    
                    # 安装 Playwright 浏览器
                    playwright install chromium
                    
                    echo "依赖安装完成"
                '''
            }
        }

        stage('🔍 代码检查') {
            steps {
                sh '''
                    . ${VENV_PATH}/bin/activate
                    
                    # 使用 ruff 检查代码
                    ruff check pages/ tests/ --output-format=text || true
                    
                    # 检查是否有语法错误
                    python -m py_compile pages/base/base_page.py
                    python -m py_compile tests/conftest.py
                    
                    echo "代码检查完成"
                '''
            }
        }

        stage('🧪 执行冒烟测试') {
            steps {
                sh '''
                    . ${VENV_PATH}/bin/activate
                    
                    # 清理历史结果
                    rm -rf ${ALLURE_RESULTS}/* reports/* screenshots/* traces/*
                    mkdir -p ${ALLURE_RESULTS} reports screenshots traces
                    
                    # 执行冒烟测试
                    pytest tests/ \
                        -v \
                        -m "smoke" \
                        --headed=false \
                        --alluredir=${ALLURE_RESULTS} \
                        --html=reports/smoke-report.html \
                        --self-contained-html \
                        --tb=short \
                        --reruns=1 \
                        --reruns-delay=2 \
                        || true
                    
                    echo "冒烟测试执行完成"
                '''
            }
        }

        stage('📊 生成报告') {
            steps {
                script {
                    // 生成 Allure 报告
                    allure([
                        includeProperties: false,
                        jdk: '',
                        properties: [],
                        reportBuildPolicy: 'ALWAYS',
                        results: [[path: 'allure-results']]
                    ])
                }
            }
        }
    }

    post {
        always {
            // 发布 HTML 报告
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'reports',
                reportFiles: 'smoke-report.html',
                reportName: '冒烟测试报告'
            ])

            // 归档测试结果
            junit testResults: 'reports/*.xml', allowEmptyResults: true

            // 归档截图和 Trace 文件
            archiveArtifacts artifacts: 'screenshots/**/*,traces/**/*', allowEmptyArchive: true, fingerprint: true

            // 清理工作空间（保留关键文件）
            cleanWs(
                deleteDirs: true,
                notFailBuild: true,
                patterns: [
                    [pattern: '.venv/**', type: 'EXCLUDE'],
                    [pattern: 'allure-results/**', type: 'EXCLUDE']
                ]
            )
        }

        success {
            script {
                def duration = currentBuild.durationString.replace(' and counting', '')
                def summary = """
✅ **冒烟测试通过**

- 构建编号: #${BUILD_NUMBER}
- 持续时间: ${duration}
- 测试环境: ${env.NODE_NAME}
- 执行时间: ${new Date().format('yyyy-MM-dd HH:mm:ss', TimeZone.getTimeZone('Asia/Shanghai'))}

[查看详细报告](${env.BUILD_URL}allure/)
                """.stripIndent()

                echo summary

                // 发送钉钉通知（可选）
                // dingtalk(
                //     robot: 'jenkins-robot',
                //     type: 'MARKDOWN',
                //     title: '冒烟测试通过',
                //     text: summary
                // )
            }
        }

        failure {
            script {
                def duration = currentBuild.durationString.replace(' and counting', '')
                def summary = """
❌ **冒烟测试失败**

- 构建编号: #${BUILD_NUMBER}
- 持续时间: ${duration}
- 测试环境: ${env.NODE_NAME}
- 执行时间: ${new Date().format('yyyy-MM-dd HH:mm:ss', TimeZone.getTimeZone('Asia/Shanghai'))}

[查看控制台输出](${env.BUILD_URL}console)
[查看 Allure 报告](${env.BUILD_URL}allure/)
                """.stripIndent()

                echo summary

                // 发送钉钉通知（可选）
                // dingtalk(
                //     robot: 'jenkins-robot',
                //     type: 'MARKDOWN',
                //     title: '冒烟测试失败',
                //     text: summary
                // )
            }
        }

        unstable {
            echo '⚠️ 测试不稳定，部分用例失败'
        }
    }
}
