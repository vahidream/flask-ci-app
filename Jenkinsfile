pipeline {
    agent any

    environment {
        SNYK_TOKEN = credentials('snyk-token') 
        DEFECTDOJO_API_TOKEN = credentials('defectdojo-api-token') 
        DEFECTDOJO_HOST = credentials('defectdojo-host') 
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/vahidream/flask-python.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sshagent (credentials: ['deployuser']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no deployuser@192.168.11.139 <<EOF
                        cd ~/flask-ci-app
                        docker build --network=host -t flask-ci-app .
                        EOF
                    '''
                }
            }
        }

        stage('Snyk Scan') {
            steps {
                sh '''
                    snyk auth $SNYK_TOKEN
                    snyk test || true
                '''
            }
        }

        stage('Upload to DefectDojo') {
            steps {
                sh '''
                    curl -X POST "$DEFECTDOJO_HOST/api/v2/import-scan/" \
                    -H "Authorization: Token $DEFECTDOJO_API_TOKEN" \
                    -F "scan_type=Dynamic Analysis" \
                    -F "file=@result.json" \
                    -F "minimum_severity=Low" \
                    -F "active=true" \
                    -F "verified=true" \
                    -F "product_name=Flask-CI-App"
                '''
            }
        }
    }
}

