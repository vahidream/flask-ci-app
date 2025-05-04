pipeline {
  agent any

  environment {
    IMAGE_NAME        = 'vahidevs/flask-ci-app'
    DOCKER_HUB_USR    = credentials('docker-hub-username')
    DOCKER_HUB_PSW    = credentials('docker-hub-password')
    DD_TOKEN          = credentials('defectdojo-api-token')
    DD_ENGAGEMENT_ID  = '5'
    DD_PRODUCT_ID     = '1'
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Build & Scan') {
      steps {
        sh '''
          # build image
          docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} .

          # static scan
          trivy image \
            --format json \
            --output trivy-report.json \
            ${IMAGE_NAME}:${BUILD_NUMBER} || true
        '''
      }
    }

    stage('Upload to DefectDojo') {
      steps {
        sh '''
          curl -s -X POST "http://192.168.11.147:8084/api/v2/import-scan/" \
            -H "Authorization: Token ${DD_TOKEN}" \
            -F "scan_type=Trivy" \
            -F "engagement=${DD_ENGAGEMENT_ID}" \
            -F "product_id=${DD_PRODUCT_ID}" \
            -F "file=@trivy-report.json"
        '''
      }
    }

    stage('Push to Docker Hub') {
      steps {
        sh '''
          echo "${DOCKER_HUB_PSW}" | docker login -u "${DOCKER_HUB_USR}" --password-stdin
          docker push ${IMAGE_NAME}:${BUILD_NUMBER}
          docker tag ${IMAGE_NAME}:${BUILD_NUMBER} ${IMAGE_NAME}:latest
          docker push ${IMAGE_NAME}:latest
        '''
      }
    }

    stage('Deploy to Kubernetes') {
      steps {
        sh '''
          # əgər kubeconfig credential olaraq base64-lədirsə:
          echo "${KUBECONFIG_CONTENT}" | base64 -d > kubeconfig.yaml
          export KUBECONFIG=$PWD/kubeconfig.yaml

          kubectl apply -f postgres-all.yaml   -n flask-app
          kubectl apply -f flask-deployment.yaml -n flask-app
          kubectl apply -f flask-service.yaml    -n flask-app
        '''
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: 'trivy-report.json', fingerprint: true
    }
    success {
      echo '✅ OK'
    }
    failure {
      echo '❌ Xəta'
    }
  }
}

