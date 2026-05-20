/**
 * 钉钉通知配置
 * 在 Jenkinsfile 的 post 部分使用
 */

// 钉钉机器人 Webhook 地址（请替换为您的实际地址）
def DINGTALK_WEBHOOK = 'https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN'
def DINGTALK_SECRET = 'YOUR_SECRET'  // 如果启用了加签

/**
 * 发送钉钉通知
 * @param status 构建状态: SUCCESS, FAILURE, UNSTABLE
 * @param title 通知标题
 * @param content 通知内容
 */
def sendDingTalkNotification(String status, String title, String content) {
    def color = status == 'SUCCESS' ? '00ff00' : (status == 'FAILURE' ? 'ff0000' : 'ffaa00')
    def emoji = status == 'SUCCESS' ? '✅' : (status == 'FAILURE' ? '❌' : '⚠️')
    
    def message = """
    {
        "msgtype": "markdown",
        "markdown": {
            "title": "${title}",
            "text": "### ${emoji} ${title}\\n\\n${content}\\n\\n---\\n**构建时间**: ${new Date().format('yyyy-MM-dd HH:mm:ss', TimeZone.getTimeZone('Asia/Shanghai'))}"
        },
        "at": {
            "isAtAll": false
        }
    }
    """
    
    // 使用 HTTP Request 插件发送通知
    httpRequest(
        httpMode: 'POST',
        contentType: 'APPLICATION_JSON',
        requestBody: message,
        url: DINGTALK_WEBHOOK,
        validResponseCodes: '200'
    )
}

/**
 * 生成测试摘要
 */
def generateTestSummary() {
    def testResults = currentBuild.rawBuild.getAction(hudson.tasks.junit.TestResultAction.class)
    
    if (testResults) {
        def total = testResults.totalCount
        def failed = testResults.failCount
        def skipped = testResults.skipCount
        def passed = total - failed - skipped
        def passRate = total > 0 ? String.format("%.2f", (passed / total) * 100) : "0.00"
        
        return """
**测试统计**
- 总计: ${total} 个用例
- 通过: ${passed} 个 ✅
- 失败: ${failed} 个 ❌
- 跳过: ${skipped} 个 ⏭️
- 通过率: ${passRate}%
        """.stripIndent()
    }
    
    return "暂无测试统计数据"
}

/**
 * 发送构建成功通知
 */
def notifySuccess() {
    def duration = currentBuild.durationString.replace(' and counting', '')
    def summary = generateTestSummary()
    
    def content = """
**构建信息**
- 项目名称: ${env.JOB_NAME}
- 构建编号: #${env.BUILD_NUMBER}
- 持续时间: ${duration}
- 构建分支: ${env.GIT_BRANCH ?: 'unknown'}
- 提交作者: ${env.GIT_AUTHOR_NAME ?: 'unknown'}

${summary}

**查看详情**
- [Jenkins 控制台](${env.BUILD_URL}console)
- [Allure 报告](${env.BUILD_URL}allure/)
- [HTML 报告](${env.BUILD_URL}HTML_20Report/)
    """.stripIndent()
    
    sendDingTalkNotification('SUCCESS', '自动化测试通过', content)
}

/**
 * 发送构建失败通知
 */
def notifyFailure() {
    def duration = currentBuild.durationString.replace(' and counting', '')
    
    def content = """
**构建信息**
- 项目名称: ${env.JOB_NAME}
- 构建编号: #${env.BUILD_NUMBER}
- 持续时间: ${duration}
- 构建分支: ${env.GIT_BRANCH ?: 'unknown'}
- 提交作者: ${env.GIT_AUTHOR_NAME ?: 'unknown'}

**失败原因**
请查看控制台输出获取详细错误信息

**查看详情**
- [Jenkins 控制台](${env.BUILD_URL}console)
- [Allure 报告](${env.BUILD_URL}allure/)
    """.stripIndent()
    
    sendDingTalkNotification('FAILURE', '自动化测试失败', content)
}

/**
 * 发送构建不稳定通知
 */
def notifyUnstable() {
    def duration = currentBuild.durationString.replace(' and counting', '')
    def summary = generateTestSummary()
    
    def content = """
**构建信息**
- 项目名称: ${env.JOB_NAME}
- 构建编号: #${env.BUILD_NUMBER}
- 持续时间: ${duration}

${summary}

**查看详情**
- [Jenkins 控制台](${env.BUILD_URL}console)
- [Allure 报告](${env.BUILD_URL}allure/)
    """.stripIndent()
    
    sendDingTalkNotification('UNSTABLE', '自动化测试不稳定', content)
}

/**
 * 在 Jenkinsfile 中使用示例：
 * 
 * post {
 *     success {
 *         script {
 *             load 'jenkins/dingtalk-config.groovy'
 *             notifySuccess()
 *         }
 *     }
 *     failure {
 *         script {
 *             load 'jenkins/dingtalk-config.groovy'
 *             notifyFailure()
 *         }
 *     }
 *     unstable {
 *         script {
 *             load 'jenkins/dingtalk-config.groovy'
 *             notifyUnstable()
 *         }
 *     }
 * }
 */
