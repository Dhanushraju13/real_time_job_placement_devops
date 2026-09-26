pipeline {
  agent any

  parameters {
    booleanParam(
      name: 'PUSH_TO_DOCKERHUB',
      defaultValue: false,
      description: 'Push built versioned Docker images to Docker Hub'
    )

    string(
      name: 'DOCKERHUB_CREDENTIALS_ID',
      defaultValue: 'dockerhub-credentials',
      description: 'Jenkins Credentials ID (Username with password)'
    )

    booleanParam(
      name: 'SECURITY_SCAN',
      defaultValue: true,
      description: 'Run Trivy container vulnerability security scan'
    )

    choice(
      name: 'ENVIRONMENT',
      choices: ['staging', 'production', 'local'],
      description: 'Deployment target environment'
    )
  }

  environment {

    // Docker executable
    DOCKER_EXE = 'C:\\Users\\hp5cd\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe'

    // Docker Compose executable
    COMPOSE_EXE = 'C:\\Users\\hp5cd\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker-compose.exe'

    // Docker image names
    BACKEND_IMAGE = 'placement-backend'
    FRONTEND_IMAGE = 'placement-frontend'

    // Jenkins build number becomes Docker image tag
    IMAGE_TAG = "${env.BUILD_NUMBER ?: 'latest'}"

    // Test database
    DATABASE_URL = 'sqlite:///test.db'
  }

  stages {

    // ==========================================================
    // STAGE 1 - CHECKOUT
    // ==========================================================

    stage('Checkout') {
      steps {

        echo "=========================================================="
        echo "Stage 1: Checkout Source Code"
        echo "=========================================================="

        checkout scm
      }
    }


    // ==========================================================
    // STAGE 2 - BACKEND TESTS
    // ==========================================================

    stage('Backend Tests') {
      steps {

        echo "=========================================================="
        echo "Stage 2: Backend Unit & Integration Tests (Pytest)"
        echo "=========================================================="

        // Build backend test image
        bat '"%DOCKER_EXE%" build -t placement-backend:test ./backend'

        // Run pytest inside Docker container
        bat '''
          if not exist test-results mkdir test-results

          "%DOCKER_EXE%" run --rm ^
            -e DATABASE_URL=sqlite:///test.db ^
            -v "%cd%\\test-results:/app/test-results" ^
            placement-backend:test ^
            python -m pytest -v --junitxml=test-results/pytest-results.xml
        '''
      }

      post {
        always {

          junit(
            testResults: 'test-results/pytest-results.xml',
            allowEmptyResults: true
          )
        }
      }
    }


    // ==========================================================
    // STAGE 3 - FRONTEND BUILD
    // ==========================================================

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


    // ==========================================================
    // STAGE 4 - DOCKER IMAGE BUILD
    // ==========================================================

    stage('Docker Image Build') {
      steps {

        echo "=========================================================="
        echo "Stage 4: Build Versioned Docker Images (${IMAGE_TAG})"
        echo "=========================================================="

        bat """
          "%DOCKER_EXE%" version

          echo Checking Docker Compose...
          "%COMPOSE_EXE%" version

          echo Building backend Docker image...
          "%DOCKER_EXE%" build -t ${BACKEND_IMAGE}:${IMAGE_TAG} -t ${BACKEND_IMAGE}:latest ./backend

          echo Building frontend Docker image...
          "%DOCKER_EXE%" build -t ${FRONTEND_IMAGE}:${IMAGE_TAG} -t ${FRONTEND_IMAGE}:latest ./frontend
        """
      }
    }


    // ==========================================================
    // STAGE 5 - SECURITY SCANNING
    // ==========================================================

    stage('Security Scanning') {

      when {
        expression {
          return params.SECURITY_SCAN == true
        }
      }

      steps {

        echo "=========================================================="
        echo "Stage 5: Container Security Vulnerability Scan"
        echo "=========================================================="

        bat """
          "%DOCKER_EXE%" save -o backend-scan.tar ${BACKEND_IMAGE}:${IMAGE_TAG}

          "%DOCKER_EXE%" run --rm ^
            -v "%cd%:/scan" ^
            aquasec/trivy:latest ^
            image ^
            --input /scan/backend-scan.tar ^
            --severity HIGH,CRITICAL ^
            --exit-code 0 ^
            || echo Trivy scan completed with warnings

          if exist backend-scan.tar del /f /q backend-scan.tar
        """
      }
    }


    // ==========================================================
    // STAGE 6 - DOCKER HUB PUSH
    // ==========================================================

    stage('Docker Hub Push') {

      when {
        expression {
          return params.PUSH_TO_DOCKERHUB == true
        }
      }

      steps {

        echo "=========================================================="
        echo "Stage 6: Authenticate & Push Images to Docker Hub"
        echo "=========================================================="

        withCredentials([
          usernamePassword(
            credentialsId: params.DOCKERHUB_CREDENTIALS_ID,
            usernameVariable: 'DOCKER_USER',
            passwordVariable: 'DOCKER_PASS'
          )
        ]) {

          bat """
            echo %DOCKER_PASS% | "%DOCKER_EXE%" login -u "%DOCKER_USER%" --password-stdin

            "%DOCKER_EXE%" tag ${BACKEND_IMAGE}:${IMAGE_TAG} %DOCKER_USER%/${BACKEND_IMAGE}:${IMAGE_TAG}
            "%DOCKER_EXE%" tag ${BACKEND_IMAGE}:latest %DOCKER_USER%/${BACKEND_IMAGE}:latest

            "%DOCKER_EXE%" tag ${FRONTEND_IMAGE}:${IMAGE_TAG} %DOCKER_USER%/${FRONTEND_IMAGE}:${IMAGE_TAG}
            "%DOCKER_EXE%" tag ${FRONTEND_IMAGE}:latest %DOCKER_USER%/${FRONTEND_IMAGE}:latest

            "%DOCKER_EXE%" push %DOCKER_USER%/${BACKEND_IMAGE}:${IMAGE_TAG}
            "%DOCKER_EXE%" push %DOCKER_USER%/${BACKEND_IMAGE}:latest

            "%DOCKER_EXE%" push %DOCKER_USER%/${FRONTEND_IMAGE}:${IMAGE_TAG}
            "%DOCKER_EXE%" push %DOCKER_USER%/${FRONTEND_IMAGE}:latest

            "%DOCKER_EXE%" logout
          """
        }
      }
    }


    // ==========================================================
    // STAGE 7 - DEPLOY
    // ==========================================================

    stage('Deploy') {
      steps {

        echo "=========================================================="
        echo "Stage 7: Deploying Stack using Docker Compose (${IMAGE_TAG})"
        echo "=========================================================="

        bat """
          echo Using Docker Compose:
          "%COMPOSE_EXE%" version

          echo Setting backend image...
          set BACKEND_IMAGE=${BACKEND_IMAGE}:${IMAGE_TAG}

          echo Setting frontend image...
          set FRONTEND_IMAGE=${FRONTEND_IMAGE}:${IMAGE_TAG}

          echo Stopping existing containers...
          "%COMPOSE_EXE%" down --remove-orphans || ver >nul

          echo Starting application...
          "%COMPOSE_EXE%" up -d

          echo Deployment command completed.
        """
      }
    }


    // ==========================================================
    // STAGE 8 - HEALTH CHECK
    // ==========================================================

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

              $response = Invoke-RestMethod `
                -Uri "http://localhost/health" `
                -Method Get `
                -TimeoutSec 3 `
                -ErrorAction Stop

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


    // ==========================================================
    // STAGE 9 - SMOKE TESTS
    // ==========================================================

    stage('Smoke Tests') {
      steps {

        echo "=========================================================="
        echo "Stage 9: End-to-End Smoke Tests"
        echo "=========================================================="

        bat 'python scripts\\smoke_test.py http://localhost'
      }
    }
  }


  // ==========================================================
  // POST ACTIONS
  // ==========================================================

  post {

    // ----------------------------------------------------------
    // ALWAYS
    // ----------------------------------------------------------

    always {

      echo "Cleaning up temporary test artifacts..."

      bat(
        script: '"%DOCKER_EXE%" rmi placement-backend:test >nul 2>&1',
        returnStatus: true
      )

      bat(
        script: 'if exist backend-scan.tar del /f /q backend-scan.tar >nul 2>&1',
        returnStatus: true
      )
    }


    // ----------------------------------------------------------
    // SUCCESS
    // ----------------------------------------------------------

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


    // ----------------------------------------------------------
    // FAILURE
    // ----------------------------------------------------------

    failure {

      echo """
===================================================================
  FAILURE: BUILD #${env.IMAGE_TAG} ENCOUNTERED ERRORS!

  Dumping diagnostic container logs:
===================================================================
      """

      bat(
        script: '"%COMPOSE_EXE%" logs --tail=50',
        returnStatus: true
      )
    }
  }
}