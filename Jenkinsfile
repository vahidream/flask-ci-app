pipeline {
  agent any

  environment {
    // Docker Hub credentials (separate username & password)
    DOCKER_HUB_USERNAME    = credentials('docker-hub-username')
    DOCKER_HUB_PASSWORD    = credentials('docker-hub-password')
    // Snyk token (optional)
    SNYK_TOKEN             = credentials('snyk-token')
    // DefectDojo API token & engagement ID
    DD_TOKEN               = credentials('defectdojo-api-token')
    DD_ENGAGEMENT_ID       = credentials('defectdojo-engagement-id')
    // Base64-encoded kubeconfig for kubectl
    KUBECONFIG_CONTENT     = credentials('kubeconfig-content')

    // Static settings
    DOCKER_IMAGE           = 'vahidevs/flask-ci-app'
    DD_HOST                = '192.168.11.147:8084'
    DD_PRODUCT_NAME        = 'Flask CI App'
    K8S_NAMESPACE          = 'flask-app'
  }

  stages {
    stage('Checkout') {
      steps {
        // Assumes you've set up HTTPS SCM in the job config with appropriate credentials
        checkout scm
      }
    }

    stage('Build Docker Image') {
      steps {
        sh "docker build -t ${DOCKER_IMAGE}:${env.BUILD_NUMBER} ."
      }
    }

    stage('Snyk Scan') {
      when { expression { env.SNYK_TOKEN } }
      steps {
        sh """
          docker run --rm                   \\
            -e SNYK_TOKEN=$SNYK_TOKEN       \\
            -v /var/run/docker.sock:/var/run/docker.sock \\
            snyk/snyk:docker test ${DOCKER_IMAGE}:${BUILD_NUMBER} --json > snyk-report.json || true
        """
      }
    }

    stage('Trivy Scan') {
      steps {
        sh """
          docker run --rm                                   \\
            -v /var/run/docker.sock:/var/run/docker.sock   \\
            aquasec/trivy:latest image                     \\
              --timeout 5m                                 \\
              --severity HIGH,CRITICAL                     \\
              --format json                                \\
              --output trivy-report.json                   \\
              ${DOCKER_IMAGE}:${BUILD_NUMBER} || true
        """
      }
    }

    stage('Upload to DefectDojo') {
      steps {
        sh """
          curl -X POST "http://${DD_HOST}/api/v2/import-scan/" \\
              -H "Authorization: Token ${DD_TOKEN}"            \\
              -F "scan_type=Trivy"                            \\
              -F "engagement=${DD_ENGAGEMENT_ID}"             \\
              -F "product_name=${DD_PRODUCT_NAME}"            \\
              -F "file=@trivy-report.json"
        """
      }
    }

    stage('Push to Docker Hub') {
      steps {
        sh """
          echo "$DOCKER_HUB_PASSWORD" | docker login -u "$DOCKER_HUB_USERNAME" --password-stdin
          docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}
        """
      }
    }

    stage('Deploy to Kubernetes') {
      steps {
        sh """
          echo "$KUBECONFIG_CONTENT" | base64 -d > kubeconfig.yaml
          export KUBECONFIG=\$PWD/kubeconfig.yaml
          kubectl apply -f k8s/postgres-all.yaml  -n ${K8S_NAMESPACE}
          kubectl apply -f k8s/flask-deployment.yaml -n ${K8S_NAMESPACE}
          kubectl apply -f k8s/flask-service.yaml -n ${K8S_NAMESPACE}
        """
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: 'snyk-report.json,trivy-report.json', allowEmptyArchive: true
      cleanWs()
    }
  }
}

