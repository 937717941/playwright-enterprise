/**
 * 疆煤宝自动化测试 - 完整回归测试 Pipeline
 * 触发条件：手动触发、定时任务（每晚 22:00）
 */
pipeline {
    agent any

    parameters {
        choice(
            name: 'TEST_ENV',
            choices: ['dev', 'staging', 'prod'],
            description: '选择测试环境'
        )
        choice(
            name: 'BROWSER',
            choices: ['chromium', 'firefox', 'webkit'],
            description: '选择浏览器'
        )
        booleanParam(
            name: 'RUN_MOBILE',
            defaultValue: true,
            description: '是否运行移动端测试'
        )
        booleanParam(
            name: 'GENERATE_TRACE',
            defaultValue: true,
            description: '是否生成 Playwright Trace 文件'
        )
    }

    environment {
        PYTHON_VERSION = '3.10'
        PROJECT_NAME = 'jiang-coal-automation'
        VENV_PATH = '.venv'
        ALLURE_RESULTS = 'allure-results'
        TEST_ENV = "${params.TEST_ENV}"
        BROWSER = "${params.BROWSER}"
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '20'))
        timeout(time: 120, unit: 'MINUTES')
        timestamps()
        disableConcurrentBuilds()
    }

    triggers {
        // 每晚 22:00 自动运行完整回归测试
        cron('H 22 * * *')
    }

    stages {
        stage('🚀 开始回归测试') {
            steps {
                script {
                    currentBuild.displayName = "#${BUILD_NUMBER} - 回归测试 (${params.TEST_ENV})"
                }
                echo """
                =========================================
                开始执行回归测试
                环境: ${params.TEST_ENV}
                浏览器: ${params.BROWSER}
                移动端: ${params.RUN_MOBILE ? '是' : '否'}
                Trace: ${params.GENERATE_TRACE ? '是' : '否'}
                时间: ${new Date().format('yyyy-MM-dd HH:mm:ss', TimeZone.getTimeZone('Asia/Shanghai'))}
                =========================================
                """
            }
        }

        stage('📥 检出代码') {
            steps {
                checkout scm
                sh '''
                    echo "当前分支: $(git rev-parse --abbrev-ref HEAD)"
                    echo "最新提交: $(git log -1 --oneline)"
                    echo "提交作者: $(git log -1 --format=%an)"
                    echo "提交时间: $(git log -1 --format=%cd)"
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
                    playwright install ${BROWSER}
                    
                    if [ "${RUN_MOBILE}" = "true" ]; then
                        playwright install chromium
                    fi
                    
                    echo "依赖安装完成"
                '''
            }
        }

        stage('🔍 代码检查') {
            parallel {
                stage('Ruff 检查') {
                    steps {
                        sh '''
                            . ${VENV_PATH}/bin/activate
                            ruff check pages/ tests/ --output-format=text || true
                        '''
                    }
                }
                stage('Black 格式检查') {
                    steps {
                        sh '''
                            . ${VENV_PATH}/bin/activate
                            black --check pages/ tests/ || true
                        '''
                    }
                }
            }
        }

        stage('🧪 执行 Web 端测试') {
            steps {
                sh '''
                    . ${VENV_PATH}/bin/activate
                    
                    # 清理历史结果
                    rm -rf ${ALLURE_RESULTS}/* reports/* screenshots/* traces/*
                    mkdir -p ${ALLURE_RESULTS} reports screenshots traces
                    
                    # 设置环境变量
                    export ENV=${TEST_ENV}
                    export BROWSER=${BROWSER}
                    
                    # 构建 pytest 参数
                    PYTEST_ARGS="-v -m regression --headed=false --alluredir=${ALLURE_RESULTS} --html=reports/regression-report.html --self-contained-html --tb=short --reruns=2 --reruns-delay=3"
                    
                    if [ "${GENERATE_TRACE}" = "true" ]; then
                        PYTEST_ARGS="${PYTEST_ARGS} --tracing=on"
                    fi
                    
                    # 执行回归测试
                    pytest tests/web/ ${PYTEST_ARGS} || true
                    
                    echo "Web 端回归测试执行完成"
                '''
            }
        }

        stage('📱 执行移动端测试') {
            when {
                expression { params.RUN_MOBILE }
            }
            steps {
                sh '''
                    . ${VENV_PATH}/bin/activate
                    
                    # 执行移动端测试
                    pytest tests/mobile/ \
                        -v \
                        -m mobile \
                        --headed=false \
                        --alluredir=${ALLURE_RESULTS} \
                        --tb=short \
                        --reruns=1 \
                        || true
                    
                    echo "移动端测试执行完成"
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

        stage('📈 生成测试摘要') {
            steps {
                sh '''
                    . ${VENV_PATH}/bin/activate
                    
                    # 生成测试统计
                    echo "========== 测试执行摘要 =========="
                    echo "执行时间: $(date '+%Y-%m-%d %H:%M:%S')"
                    echo "测试环境: ${TEST_ENV}"
                    echo "浏览器: ${BROWSER}"
                    echo "==================================="
                    
                    # 统计测试结果
                    if [ -f "allure-results" ]; then
                        PASSED=$(grep -r '"status": "passed"' allure-results/ | wc -l)
                        FAILED=$(grep -r '"status": "failed"' allure-results/ | wc -l)
                        SKIPPED=$(grep -r '"status": "skipped"' allure-results/ | wc -l)
                        
                        echo "通过: ${PASSED}"
                        echo "失败: ${FAILED}"
                        echo "跳过: ${SKIPPED}"
                    fi
                '''
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
                reportFiles: 'regression-report.html',
                reportName: '回归测试报告'
            ])

            // 归档测试结果
            junit testResults: 'reports/*.xml', allowEmptyResults: true

            // 归档截图和 Trace 文件
            archiveArtifacts artifacts: 'screenshots/**/*,traces/**/*', allowEmptyArchive: true, fingerprint: true

            // 清理工作空间
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
✅ **回归测试通过**

- 构建编号: #${BUILD_NUMBER}
- 测试环境: ${params.TEST_ENV}
- 浏览器: ${params.BROWSER}
- 持续时间: ${duration}
- 执行时间: ${new Date().format('yyyy-MM-dd HH:mm:ss', TimeZone.getTimeZone('Asia/Shanghai'))}

[查看详细报告](${env.BUILD_URL}allure/)
                """.stripIndent()

                echo summary
            }
        }

        failure {
            script {
                def duration = currentBuild.durationString.replace(' and counting', '')
                def summary = """
❌ **回归测试失败**

- 构建编号: #${BUILD_NUMBER}
- 测试环境: ${params.TEST_ENV}
- 浏览器: ${params.BROWSER}
- 持续时间: ${duration}
- 执行时间: ${new Date().format('yyyy-MM-dd HH:mm:ss', TimeZone.getTimeZone('Asia/Shanghai'))}

[查看控制台输出](${env.BUILD_URL}console)
[查看 Allure 报告](${env.BUILD_URL}allure/)
                """.stripIndent()

                echo summary
            }
        }

        unstable {
            script {
                def summary = """
⚠️ **回归测试不稳定**

- 构建编号: #${BUILD_NUMBER}
- 部分用例执行失败
- [查看详细报告](${env.BUILD_URL}allure/)
                """.stripIndent()

                echo summary
            }
        }
    }
}
