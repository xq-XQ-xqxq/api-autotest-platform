// Jenkins 流水线：接口自动化回归
// 功能：定时执行 + 提交触发 + Allure 报告 + 构建后通知，实现「提交即回归」
pipeline {
    agent any

    triggers {
        cron('H 2 * * *')          // 每天凌晨自动回归
        pollSCM('H/10 * * * *')    // 轮询代码仓库，有提交即触发（也可改为 Git Webhook）
    }

    stages {
        stage('安装依赖') {
            steps {
                // Windows 节点用 bat；Linux 节点改为: sh 'pip install -r requirements.txt'
                bat 'python -m pip install -r requirements.txt'
            }
        }
        stage('执行接口自动化测试') {
            steps {
                bat 'python -m pytest --alluredir=reports/allure-results --clean-alluredir'
            }
        }
    }

    post {
        always {
            // 生成 Allure 报告（需 Jenkins 安装 Allure 插件）
            allure includeProperties: false, jdk: '', results: [[path: 'reports/allure-results']]
        }
        success {
            bat 'python ci_notify.py success'
        }
        failure {
            bat 'python ci_notify.py failure'
        }
    }
}
