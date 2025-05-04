pipeline {
  // 1️⃣ PodTemplate tanımı: içində dind (docker:dind) və jnlp var
  agent {
    kubernetes {
      yaml """
apiVersion: v1
kind: Pod
metadata:
  labels:
    app: jenkins-agent
spec:
  securityContext:
    fsGroup: 1000
  containers:
  - name: dind
    image: docker:20-dind
    securityContext:
      privileged: true
    volumeMounts:
      - name: docker-sock
        mountPath: /var/run/docker.sock
  volumes:
  - name: docker-sock
    hostPath:
      path: /var/run/docker.sock
      type: File
"""
    }
  }

  environment {
    DOCKER_HUB_USERNAME    = credentials('docker-hub-username')
    DOCKER_HUB_PASSWORD    = credentials('docker-hub-password')
    DD_TOKEN               = credentials('defectdojo-api-token')
    DD_ENGAGEMENT_ID       = '5'
    KUBECONFIG_CONTENT     = credentials('kubeconfig-content')
    DOCKER_IMAGE           = 'vahidevs/flask-ci-app'
    DD_HOST                = '192.168.11.147:8084'
    DD_PRODUCT_NAME        = 'Flask CI App'
    K8S_NAMESPACE          = 'flask-app'
  }

  stages {
    stage('Checkout') {
      steps {
        // Eğer Known Hosts uyarısı alırsınızsa, bu satırı Temporary disable edin:
        // sshagent(['ssh-deploy']) { git url: 'git@github.com:vahidream/flask-ci-app.git', branch: 'main' }
        checkout scm
      }
    }

    stage('Build Docker Image') {
      steps {
        // dind konteyner içində Docker CLI işlədəcəyik
        container('dind') {
          sh "docker build -t ${DOCKER_IMAGE}:${env.BUILD_NUMBER} ."
        }
      }
    }

    stage('Trivy Scan') {
      steps {
        container('dind') {
          sh """
            docker run --rm \\
              -v /var/run/docker.sock:/var/run/docker.sock \\
              aquasec/trivy:latest image \\
              --timeout 5m \\
              --severity HIGH,CRITICAL \\
              --format json \\
              --output trivy-report.json \\
              ${DOCKER_IMAGE}:${BUILD_NUMBER} || true
          """
        }
      }
    }

    stage('Upload to DefectDojo') {
      steps {
        container('dind') {
          sh '''
            curl -v -X POST "http://${DD_HOST}/api/v2/import-scan/" \
              -H "Authorization: Token ${DD_TOKEN}" \
              -F "scan_type=Trivy" \
              -F "engagement=${DD_ENGAGEMENT_ID}" \
              -F "product_name=${DD_PRODUCT_NAME}" \
              -F "file=@trivy-report.json"
          '''
        }
      }
    }

    stage('Push to Docker Hub') {
      steps {
        container('dind') {
          sh '''
            echo "$DOCKER_HUB_PASSWORD" | docker login -u "$DOCKER_HUB_USERNAME" --password-stdin
            docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}
          '''
        }
      }
    }

    stage('Deploy to Kubernetes') {
      steps {
        container('dind') {
          sh '''
            echo "$KUBECONFIG_CONTENT" | base64 -d > kubeconfig.yaml
            export KUBECONFIG=$PWD/kubeconfig.yaml
            kubectl apply -f k8s/postgres-all.yaml  -n ${K8S_NAMESPACE}
            kubectl apply -f k8s/flask-deployment.yaml -n ${K8S_NAMESPACE}
            kubectl apply -f k8s/flask-service.yaml -n ${K8S_NAMESPACE}
          '''
        }
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: 'trivy-report.json', allowEmptyArchive: true
      deleteDir()   // cleanWs() yox, deleteDir() istifadə edin
    }
  }
}

