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
                    sh """
                    ssh -o StrictHostKeyChecking=no deployuser@192.168.11.139 '
                        cd ~/flask-ci-app &&
                        docker build --network=host -t flask-ci-app .
                    '
                    """
                }
            }
        }

        stage('Snyk Scan') {
            when {
                expression { env.SNYK_TOKEN }
            }
            steps {
                sh """
                echo "Snyk scan burada icra olunacaq. (Scan mərhələsi hazırdır)"
                """
            }
        }

        stage('Upload to DefectDojo') {
            when {
                expression { env.DEFECTDOJO_API_TOKEN }
            }
            steps {
                sh """
                echo "DefectDojo upload burada icra olunacaq. (Upload mərhələsi hazırdır)"
                """
            }
        }
    }
}

