pipeline {
    agent any

    environment {
        // Secrets fetched from AWS SSM Parameter Store (free tier)
        ANTHROPIC_API_KEY   = credentials('anthropic-api-key')
        LANGCHAIN_API_KEY   = credentials('langsmith-api-key')
        AWS_S3_BUCKET       = 'langgraph-allure-reports'
        LANGCHAIN_PROJECT   = 'langgraph-healing-engine'
    }

    parameters {
        choice(
            name: 'SUITE',
            choices: ['sanity', 'regression', 'full', 'security', 'evaluation'],
            description: 'Which test suite to run'
        )
        booleanParam(
            name: 'UPLOAD_REPORT',
            defaultValue: true,
            description: 'Upload Allure report to S3 after run'
        )
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t langgraph-agent-tests:latest .'
            }
        }

        stage('Unit Tests') {
            steps {
                sh """
                    docker run --rm \\
                        -e LANGCHAIN_TRACING_V2=false \\
                        -v \$(pwd)/allure-results:/app/allure-results \\
                        langgraph-agent-tests:latest \\
                        pytest tests/unit tests/security tests/regression \\
                        -v --tb=short --alluredir=allure-results/unit
                """
            }
            post {
                always {
                    archiveArtifacts artifacts: 'allure-results/**', allowEmptyArchive: true
                }
            }
        }

        stage('UI Tests') {
            when {
                expression { params.SUITE in ['regression', 'full'] }
            }
            steps {
                sh """
                    docker run --rm \\
                        -e LANGCHAIN_TRACING_V2=true \\
                        -e LANGCHAIN_API_KEY=${LANGCHAIN_API_KEY} \\
                        -e LANGCHAIN_PROJECT=${LANGCHAIN_PROJECT} \\
                        -v \$(pwd)/allure-results:/app/allure-results \\
                        -v \$(pwd)/healing_reports:/app/healing_reports \\
                        langgraph-agent-tests:latest \\
                        pytest tests/ui -v --tb=short --alluredir=allure-results/ui
                """
            }
        }

        stage('API Tests') {
            when {
                expression { params.SUITE in ['sanity', 'regression', 'full'] }
            }
            steps {
                sh """
                    docker run --rm \\
                        -e LANGCHAIN_TRACING_V2=false \\
                        -v \$(pwd)/allure-results:/app/allure-results \\
                        langgraph-agent-tests:latest \\
                        pytest tests/api -v --tb=short --alluredir=allure-results/api
                """
            }
        }

        stage('Security / Adversarial Tests') {
            when {
                expression { params.SUITE in ['security', 'full'] }
            }
            steps {
                sh """
                    docker run --rm \\
                        -e LANGCHAIN_TRACING_V2=false \\
                        -v \$(pwd)/allure-results:/app/allure-results \\
                        langgraph-agent-tests:latest \\
                        pytest tests/security -v --tb=short --alluredir=allure-results/security
                """
            }
        }

        stage('RAG Evaluation — RAGAS + DeepEval') {
            when {
                expression { params.SUITE in ['evaluation', 'full'] }
            }
            steps {
                sh """
                    docker run --rm \\
                        -e ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY} \\
                        -e LANGCHAIN_TRACING_V2=false \\
                        -v \$(pwd)/allure-results:/app/allure-results \\
                        langgraph-agent-tests:latest \\
                        pytest tests/evaluation -v --tb=short --alluredir=allure-results/evaluation
                """
            }
        }

        stage('Generate Allure Report') {
            steps {
                sh 'allure generate allure-results --clean -o allure-report'
            }
        }

        stage('Upload Report to S3') {
            when {
                expression { params.UPLOAD_REPORT }
            }
            steps {
                withAWS(credentials: 'aws-credentials', region: 'us-east-1') {
                    sh """
                        python analytics/s3_uploader.py \\
                            --bucket ${AWS_S3_BUCKET} \\
                            --report-dir allure-report \\
                            --build-id ${BUILD_NUMBER}
                    """
                }
            }
        }
    }

    post {
        always {
            publishHTML(target: [
                reportName: 'Allure Report',
                reportDir: 'allure-report',
                reportFiles: 'index.html',
                keepAll: true,
                alwaysLinkToLastBuild: true,
            ])
        }
        failure {
            echo "Pipeline failed — check LangSmith for agent traces"
            echo "LangSmith project: ${LANGCHAIN_PROJECT}"
        }
    }
}
