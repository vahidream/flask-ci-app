pipeline {
    agent any

    environment {
        SNYK_TOKEN = credentials('snyk-token')               // Snyk API Token
        DEFECTDOJO_API_TOKEN = credentials('defectdojo-api-token') // DefectDojo API Token (admin -> apidən alacaqsan)
        DEFECTDOJO_HOST = credentials('DEFECTDOJO_HOST')       // Bizim Secret Text olan DefectDojo Host
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/vahidream/flask-python.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sshagent(credentials: ['jenkinsagent']) {
                    sh '''
                    ssh -o StrictHostKeyChecking=no jenkinsagent@192.168.11.139 <<EOF
                    cd ~/flask-ci-app
                    docker build --network=host -t flask-ci-app .
                    EOF
                    '''
                }
            }
        }

        stage('Snyk Scan') {
            steps {
                sshagent(credentials: ['jenkinsagent']) {
                    sh '''
                    ssh -o StrictHostKeyChecking=no jenkinsagent@192.168.11.139 <<EOF
                    snyk auth $SNYK_TOKEN
                    snyk container test flask-ci-app --file=Dockerfile || true
                    snyk container monitor flask-ci-app --file=Dockerfile || true
                    EOF
                    '''
                }
            }
        }

        stage('Upload to DefectDojo') {
            steps {
                sshagent(credentials: ['jenkinsagent']) {
                    sh '''
                    ssh -o StrictHostKeyChecking=no jenkinsagent@192.168.11.139 <<EOF
                    curl -k -X POST "$DEFECTDOJO_HOST/api/v2/import-scan/" \
                    -H "Authorization: Token $DEFECTDOJO_API_TOKEN" \
                    -F "minimum_severity=Low" \
                    -F "scan_type=Snyk Scan" \
                    -F "product_name=Flask-CI-App" \
                    -F "file=@snyk.sarif" \
                    -F "engagement_name=CI-CD Scan" \
                    -F "auto_create_context=true"
                    EOF
                    '''
                }
            }
        }
    }
}

