pipeline {
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
        echo 'Git checkout already done automatically by Jenkins'
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
        ssh -o StrictHostKeyChecking=no $REMOTE_SERVER '
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
        ssh -o StrictHostKeyChecking=no $REMOTE_SERVER '
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
}

