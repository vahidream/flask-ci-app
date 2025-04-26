pipeline {
    agent any

    environment {
        // Jenkins Credentials-da yaradacağın dəyişənlər
        SNYK_TOKEN = credentials('ef06c444-cbae-495b-a5b5-cb6e02bccfa4')
        DEFECTDOJO_API_KEY = credentials('11ae79c57e1f8afd4ced2faa484ac0f3b5630d1e')
        DEFECTDOJO_HOST = "http://192.168.11.140:8888"
        PROJECT_NAME = "flask-python"
    }

    stages {
        stage('Checkout') {
            steps {
                // Kod repozitoriyasını Jenkins-ə gətirir
                git branch: 'main', url: 'https://github.com/user/flask-python.git'
            }
        }

        stage('Docker Build') {
            steps {
                // Docker image qurulur
                sh '''
                docker build -t myapp:${BUILD_NUMBER} .
                '''
            }
        }

        stage('Snyk Security Scan') {
            steps {
                // Snyk ilə Dockerfile skan edilir
                sh '''
                docker run --rm -e SNYK_TOKEN=${SNYK_TOKEN} \
                -v $(pwd):/project snyk/snyk-cli:docker test \
                --file=Dockerfile --json > snyk-report.json || true
                '''
            }
        }

        stage('Upload to DefectDojo') {
            steps {
                // DefectDojo-ya skan nəticəsi yüklənir
                sh '''
                curl -X POST "${DEFECTDOJO_HOST}/api/v2/import-scan/" \
                -H "Authorization: Token ${DEFECTDOJO_API_KEY}" \
                -F 'scan_type=Snyk Scan' \
                -F 'file=@snyk-report.json' \
                -F 'engagement_name='${PROJECT_NAME}' Snyk Scan' \
                -F 'product_name='${PROJECT_NAME}''
                '''
            }
        }

        stage('Docker Push') {
            steps {
                // Docker Hub-a yükləyirik
                withCredentials([usernamePassword(credentialsId: 'docker-hub-cred', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh '''
                    echo "${DOCKER_PASS}" | docker login -u "${DOCKER_USER}" --password-stdin
                    docker tag myapp:${BUILD_NUMBER} SENIN_DOCKERHUB_IDIN/myapp:${BUILD_NUMBER}
                    docker push SENIN_DOCKERHUB_IDIN/myapp:${BUILD_NUMBER}
                    '''
                }
            }
        }
    }
}


  agent any

  environment {
    REMOTE_SERVER = 'jenkinsagent@192.168.11.143'
    IMAGE_NAME = 'vahidevs/flask-ci-app'
    SNYK_TOKEN = credentials('snyk_token')
    DEFECTDOJO_API = 'http://192.168.11.140:8888/api/v2/import-scan/'
    DEFECTDOJO_TOKEN = '11ae79c57e1f8afd4ced2faa484ac0f3b5630d1e'
    ENGAGEMENT_ID = '2'
    PRODUCT_NAME = 'flask-python'
  }

  stages {
    stage('Git Checkout') {
      steps {
        git branch: 'main', url: 'https://github.com/vahidream/flask-python.git'
      }
    }

    stage('SSH to Remote: Docker Build') {
      steps {
        sh '''
        ssh -o StrictHostKeyChecking=no $REMOTE_SERVER '
          cd /home/jenkinsagent/flask-ci-app &&
          docker build -t $IMAGE_NAME .
        '
        '''
      }
    }

    stage('SSH to Remote: Snyk Scan') {
      steps {
        sh '''
        ssh $REMOTE_SERVER '
          cd /home/jenkinsagent/flask-ci-app &&
          snyk auth $SNYK_TOKEN &&
          snyk test --docker $IMAGE_NAME --json > sast.json
        '
        '''
      }
    }

    stage('SSH to Remote: Upload to DefectDojo') {
      steps {
        sh '''
        ssh $REMOTE_SERVER '
          curl -X POST $DEFECTDOJO_API \
            -H "Authorization: Token $DEFECTDOJO_TOKEN" \
            -F engagement=$ENGAGEMENT_ID \
            -F scan_type="Dependency Scan" \
            -F file=@/home/jenkinsagent/flask-ci-app/sast.json \
            -F product_name=$PRODUCT_NAME
        '
        '''
      }
    }
  }

