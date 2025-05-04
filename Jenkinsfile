pipeline {
  agent {
    kubernetes {
      label 'flask-ci-agent'
      defaultContainer 'dind'
      yaml """
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: dind
    image: docker:20-dind
    securityContext:
      privileged: true
    volumeMounts:
    - name: docker-sock
      mountPath: /var/run/docker.sock
  - name: jnlp
    image: jenkins/inbound-agent:latest
    args: ['$(JENKINS_SECRET)', '$(JENKINS_AGENT_NAME)']
  volumes:
  - name: docker-sock
    hostPath:
      path: /var/run/docker.sock
      type: Socket
"""
    }
  }

  environment {
    DOCKER_IMAGE           = 'vahidevs/flask-ci-app'
    DEFECTDOJO_HOST        = 'http://192.168.11.147:8084'
    DEFECTDOJO_API_TOKEN   = credentials('defectdojo-api-token')
    DD_ENGAGEMENT_ID       = credentials('defectdojo-engagement-id')
    DOCKER_HUB_USERNAME    = credentials('docker-hub-username')
    DOCKER_HUB_PASSWORD    = credentials('docker-hub-password')
    KUBECONFIG_CONTENT     = credentials('kubeconfig-content')
  }

  stages {
    stage('Build') {
      steps {
        container('dind') {
          sh 'docker version'
          sh 'docker build -t $DOCKER_IMAGE:${BUILD_NUMBER} .'
        }
      }
    }

    stage('Trivy Scan') {
      steps {
        container('dind') {
          sh 'docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image --format json -o trivy-report.json $DOCKER_IMAGE:${BUILD_NUMBER}'
        }
      }
    }

    stage('Upload to DefectDojo') {
      steps {
        container('dind') {
          sh '''
            curl -X POST "$DEFECTDOJO_HOST/api/v2/import-scan/" \
              -H "Authorization: Token $DEFECTDOJO_API_TOKEN" \
              -F "scan_type=Trivy" \
              -F "engagement=$DD_ENGAGEMENT_ID" \
              -F "product_name=Flask CI App" \
              -F "file=@trivy-report.json"
          '''
        }
      }
    }

    stage('Push to Docker Hub') {
      steps {
        container('dind') {
          sh 'echo $DOCKER_HUB_PASSWORD | docker login -u $DOCKER_HUB_USERNAME --password-stdin'
          sh 'docker push $DOCKER_IMAGE:${BUILD_NUMBER}'
        }
      }
    }

    stage('Deploy to Kubernetes') {
      steps {
        container('dind') {
          sh '''
            echo "$KUBECONFIG_CONTENT" | base64 -d > kubeconfig.yaml
            export KUBECONFIG=$PWD/kubeconfig.yaml
            kubectl apply -f postgres-all.yaml -n flask-app
            kubectl apply -f flask-deployment.yaml -n flask-app
            kubectl apply -f flask-service.yaml -n flask-app
          '''
        }
      }
    }
  }
}

