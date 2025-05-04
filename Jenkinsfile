pipeline {
  agent any

  environment {
    // Credentials stored in Jenkins > Manage Credentials
    DOCKER_HUB_USERNAME    = credentials('docker-hub-username')
    DOCKER_HUB_PASSWORD    = credentials('docker-hub-password')
    SNYK_TOKEN             = credentials('snyk-token')
    DD_API_TOKEN           = credentials('defectdojo-api-token')
    KUBECONFIG_CONTENT     = credentials('kubeconfig-content')

    // Static settings
    DOCKER_IMAGE           = 'vahidevs/flask-ci-app'
    DEFECTDOJO_HOST        = '192.168.11.147:8084'
    DEFECTDOJO_ENGAGEMENT  = '5'
    DEFECTDOJO_PRODUCT     = 'Flask CI App'
    K8S_NAMESPACE          = 'flask-app'
  }

  options {
    // Keep only last 10 builds
    buildDiscarder(logRotator(numToKeepStr: '10'))
    timestamps()
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Build Docker Image') {
      steps {
        sh """
          docker build -t ${DOCKER_IMAGE}:${env.BUILD_NUMBER} .
        """
      }
    }

    stage('Snyk Scan') {
      steps {
        sh """
          echo "${SNYK_TOKEN}" | snyk auth
          snyk container test ${DOCKER_IMAGE}:${BUILD_NUMBER} --severity-threshold=high || true
        """
      }
    }

    stage('Trivy Scan') {
      steps {
        sh """
          trivy image \
            --format json \
            --output trivy-report.json \
            --severity HIGH,CRITICAL \
            ${DOCKER_IMAGE}:${BUILD_NUMBER} || true
        """
      }
      post {
        always {
          archiveArtifacts artifacts: 'trivy-report.json', allowEmptyArchive: true
        }
      }
    }

    stage('Upload to DefectDojo') {
      steps {
        sh """
          curl -X POST "http://${DEFECTDOJO_HOST}/api/v2/import-scan/" \
            -H "Authorization: Token ${DD_API_TOKEN}" \
            -F "scan_type=Trivy" \
            -F "engagement=${DEFECTDOJO_ENGAGEMENT}" \
            -F "product_name=${DEFECTDOJO_PRODUCT}" \
            -F "file=@trivy-report.json"
        """
      }
    }

    stage('Push to Docker Hub') {
      steps {
        sh """
          echo "${DOCKER_HUB_PASSWORD}" | docker login -u "${DOCKER_HUB_USERNAME}" --password-stdin
          docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}
        """
      }
    }

    stage('Deploy to Kubernetes') {
      steps {
        sh """
          echo "${KUBECONFIG_CONTENT}" | base64 -d > kubeconfig.yaml
          export KUBECONFIG=\$PWD/kubeconfig.yaml
          kubectl apply -f k8s/postgres-all.yaml -n ${K8S_NAMESPACE}
          kubectl apply -f k8s/flask-deployment.yaml -n ${K8S_NAMESPACE}
          kubectl apply -f k8s/flask-service.yaml -n ${K8S_NAMESPACE}
        """
      }
    }
  }

  post {
    always {
      deleteDir()  // clean workspace
    }
    success {
      echo "Pipeline completed successfully!"
    }
    failure {
      echo "Pipeline failed. Check the logs."
    }
  }
}

