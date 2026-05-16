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
                        -v \$(pwd)/report/allure/results:/app/report/allure/results \\
                        langgraph-agent-tests:latest \\
                        pytest test/unit test/security test/regression \\
                        -v --tb=short --alluredir=report/allure/results/unit
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
                        -v \$(pwd)/report/allure/results:/app/report/allure/results \\
                        -v \$(pwd)/report/healing:/app/report/healing \\
                        langgraph-agent-tests:latest \\
                        pytest test/ui -v --tb=short --alluredir=report/allure/results/ui
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
                        -v \$(pwd)/report/allure/results:/app/report/allure/results \\
                        langgraph-agent-tests:latest \\
                        pytest test/api -v --tb=short --alluredir=report/allure/results/api
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
                        -v \$(pwd)/report/allure/results:/app/report/allure/results \\
                        langgraph-agent-tests:latest \\
                        pytest test/security -v --tb=short --alluredir=report/allure/results/security
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
                        -v \$(pwd)/report/allure/results:/app/report/allure/results \\
                        langgraph-agent-tests:latest \\
                        pytest test/evaluation -v --tb=short --alluredir=report/allure/results/evaluation
                """
            }
        }

        stage('Generate Allure Report') {
            steps {
                sh 'allure generate report/allure/results --clean -o report/allure/html'
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
                            --report-dir report/allure/html \\
                            --build-id ${BUILD_NUMBER} \\
                            --region us-east-1
                    """
                }
            }
        }
    }

    post {
        always {
            publishHTML(target: [
                reportName: 'Allure Report',
                reportDir: 'report/allure/html',
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
