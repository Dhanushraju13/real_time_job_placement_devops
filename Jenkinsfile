pipeline {
  agent any

  parameters {
    booleanParam(name: 'PUSH_TO_DOCKERHUB', defaultValue: false, description: 'Push built versioned Docker images to Docker Hub')
    string(
      name: 'DOCKERHUB_CREDENTIALS_ID',
      defaultValue: 'dockerhub-credentials',
      description: 'Jenkins Credentials ID (Username with password)'
    )
    booleanParam(name: 'SECURITY_SCAN', defaultValue: true, description: 'Run Trivy container vulnerability security scan')
    choice(name: 'ENVIRONMENT', choices: ['staging', 'production', 'local'], description: 'Deployment target environment')
  }

  environment {
    BACKEND_IMAGE = 'placement-backend'
    FRONTEND_IMAGE = 'placement-frontend'
    IMAGE_TAG = "${env.BUILD_NUMBER ?: 'latest'}"
    DATABASE_URL = 'sqlite:///test.db'
  }

  stages {
    stage('Checkout') {
      steps {
        echo "=========================================================="
        echo "Stage 1: Checkout Source Code"
        echo "=========================================================="
        checkout scm
      }
    }

    stage('Backend Tests') {
      steps {
        echo "=========================================================="
        echo "Stage 2: Backend Unit & Integration Tests (Pytest)"
        echo "=========================================================="
        // 1. Build backend test runner image with dependencies
        bat 'docker build -t placement-backend:test ./backend'

        // 2. Execute Pytest suite and generate JUnit XML report
        bat '''
          if not exist test-results mkdir test-results
          docker run --rm -e DATABASE_URL=sqlite:///test.db -v "%cd%\\test-results:/app/test-results" placement-backend:test python -m pytest -v --junitxml=test-results/pytest-results.xml
        '''
      }
      post {
        always {
          junit testResults: 'test-results/pytest-results.xml', allowEmptyResults: true
        }
      }
    }

    stage('Frontend Build') {
      steps {
        echo "=========================================================="
        echo "Stage 3: Frontend Build & Asset Verification"
        echo "=========================================================="
        bat '''
          cd frontend
          call npm install
          call npm run build
          cd ..
        '''
      }
    }

    stage('Docker Image Build') {
      steps {
        echo "=========================================================="
        echo "Stage 4: Build Versioned Docker Images (${IMAGE_TAG})"
        echo "=========================================================="
        bat """
          docker version
          docker compose version
          docker build -t ${BACKEND_IMAGE}:${IMAGE_TAG} -t ${BACKEND_IMAGE}:latest ./backend
          docker build -t ${FRONTEND_IMAGE}:${IMAGE_TAG} -t ${FRONTEND_IMAGE}:latest ./frontend
        """
      }
    }

    stage('Security Scanning') {
      when {
        expression { return params.SECURITY_SCAN == true }
      }
      steps {
        echo "=========================================================="
        echo "Stage 5: Container Security Vulnerability Scan"
        echo "=========================================================="
        bat(
          script: "docker run --rm -v //var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image --severity HIGH,CRITICAL --exit-code 0 ${BACKEND_IMAGE}:${IMAGE_TAG} || echo Trivy scan completed",
          returnStatus: true
        )
      }
    }

    stage('Docker Hub Push') {
      when {
        expression { return params.PUSH_TO_DOCKERHUB == true }
      }
      steps {
        echo "=========================================================="
        echo "Stage 6: Authenticate & Push Images to Docker Hub"
        echo "=========================================================="
        withCredentials([usernamePassword(
          credentialsId: params.DOCKERHUB_CREDENTIALS_ID,
          usernameVariable: 'DOCKER_USER',
          passwordVariable: 'DOCKER_PASS'
        )]) {
          bat """
            echo %DOCKER_PASS% | docker login -u "%DOCKER_USER%" --password-stdin
            docker tag ${BACKEND_IMAGE}:${IMAGE_TAG} %DOCKER_USER%/${BACKEND_IMAGE}:${IMAGE_TAG}
            docker tag ${BACKEND_IMAGE}:latest %DOCKER_USER%/${BACKEND_IMAGE}:latest
            docker tag ${FRONTEND_IMAGE}:${IMAGE_TAG} %DOCKER_USER%/${FRONTEND_IMAGE}:${IMAGE_TAG}
            docker tag ${FRONTEND_IMAGE}:latest %DOCKER_USER%/${FRONTEND_IMAGE}:latest
            docker push %DOCKER_USER%/${BACKEND_IMAGE}:${IMAGE_TAG}
            docker push %DOCKER_USER%/${BACKEND_IMAGE}:latest
            docker push %DOCKER_USER%/${FRONTEND_IMAGE}:${IMAGE_TAG}
            docker push %DOCKER_USER%/${FRONTEND_IMAGE}:latest
            docker logout
          """
        }
      }
    }

    stage('Deploy') {
      steps {
        echo "=========================================================="
        echo "Stage 7: Deploying Stack using Docker Compose (${IMAGE_TAG})"
        echo "=========================================================="
        bat """
          set BACKEND_IMAGE=${BACKEND_IMAGE}:${IMAGE_TAG}
          set FRONTEND_IMAGE=${FRONTEND_IMAGE}:${IMAGE_TAG}
          docker compose down --remove-orphans || ver >nul
          docker compose up -d
        """
      }
    }

    stage('Health Check') {
      steps {
        echo "=========================================================="
        echo "Stage 8: Resilient Health & Readiness Polling (PowerShell)"
        echo "=========================================================="
        powershell '''
          $maxRetries = 15
          $waitInterval = 4
          $attempt = 1
          $isHealthy = $false

          Write-Host "Polling system health status on Nginx ingress (http://localhost/health)..."
          while ($attempt -le $maxRetries) {
            Write-Host "Health check attempt $attempt of $maxRetries..."
            try {
              $response = Invoke-RestMethod -Uri "http://localhost/health" -Method Get -TimeoutSec 3 -ErrorAction Stop
              if ($response.status -eq "UP") {
                Write-Host "Service is UP and healthy!"
                $isHealthy = $true
                break
              }
            } catch {
              Write-Host "Health check attempt $attempt failed, retrying in ${waitInterval}s..."
            }
            $attempt++
            Start-Sleep -Seconds $waitInterval
          }

          if (-not $isHealthy) {
            Write-Error "Health check failed after $maxRetries attempts."
            exit 1
          }
        '''
      }
    }

    stage('Smoke Tests') {
      steps {
        echo "=========================================================="
        echo "Stage 9: End-to-End Smoke Tests"
        echo "=========================================================="
        bat 'python scripts\\smoke_test.py http://localhost'
      }
    }
  }

  post {
    always {
      echo "Cleaning up temporary test artifacts..."
      bat(script: 'docker rmi placement-backend:test >nul 2>&1', returnStatus: true)
    }
    success {
      echo """
===================================================================
  SUCCESS: BUILD #${env.IMAGE_TAG} DEPLOYED AND VERIFIED!
  Application URL: http://localhost
  API Documentation: http://localhost/api/docs
  Health Endpoint: http://localhost/health
===================================================================
      """
    }
    failure {
      echo """
===================================================================
  FAILURE: BUILD #${env.IMAGE_TAG} ENCOUNTERED ERRORS!
  Dumping diagnostic container logs:
===================================================================
      """
      bat(script: 'docker compose logs --tail=50', returnStatus: true)
    }
  }
}
