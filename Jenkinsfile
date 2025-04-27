pipeline {
    agent any

    environment {
        IMAGE_NAME = "flask-ci-app"
        REMOTE_USER = "jenkinsagent"
        REMOTE_HOST = "192.168.11.143"
        REMOTE_PROJECT_PATH = "/home/jenkinsagent/flask-ci-app"
    }

    stages {
        stage('Declarative: Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Git Checkout') {
            steps {
                echo "Git checkout already done automatically by Jenkins"
            }
        }

        stage('SSH to Remote: Docker Build') {
            steps {
                sshagent(credentials: ['ssh-to-143']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no $REMOTE_USER@$REMOTE_HOST << EOF
                            cd $REMOTE_PROJECT_PATH
                            docker build -t $IMAGE_NAME .
                            docker build --network=host -t $IMAGE_NAME .
          6f7698a (Fix: add --network=host to docker build)
                        EOF
                    '''
                }
            }
        }

        stage('SSH to Remote: Snyk Scan') {
            steps {
                sshagent(credentials: ['ssh-to-143']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no $REMOTE_USER@$REMOTE_HOST << EOF
                            cd $REMOTE_PROJECT_PATH
                            snyk test --docker $IMAGE_NAME --file=Dockerfile --json > sast.json
                        EOF
                    '''
                }
            }
        }

        stage('SSH to Remote: Upload to DefectDojo') {
            steps {
                sshagent(credentials: ['ssh-to-143']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no $REMOTE_USER@$REMOTE_HOST << EOF
                            curl -X POST "$DEFECTDOJO_HOST/api/v2/import-scan/" \
                            -H "Authorization: Token $DEFECTDOJO_API_TOKEN" \
                            -F "file=@$REMOTE_PROJECT_PATH/sast.json" \
                            -F "engagement=$DEFECTDOJO_ENGAGEMENT_ID" \
                            -F "scan_type=Dependency Scan" \
                            -F "minimum_severity=Low" \
                            -F "active=true" \
                            -F "verified=true" \
                            -F "product_name=$DEFECTDOJO_PRODUCT_NAME"
                        EOF
                    '''
                }
            }
        }
    }
}
