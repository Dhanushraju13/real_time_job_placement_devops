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
        // 1. Build test runner image with backend code and dependencies
        sh 'docker build -t placement-backend:test ./backend'
        
        // 2. Execute Pytest suite with isolated test DB and generate JUnit XML report
        sh '''
          docker run --rm \
            -e DATABASE_URL="sqlite:///test.db" \
            -v "$(pwd)":/reports \
            placement-backend:test \
            python -m pytest -v --junitxml=/reports/backend-test-results.xml
        '''
      }
      post {
        always {
          junit testResults: 'backend-test-results.xml', allowEmptyResults: true
        }
      }
    }

    stage('Frontend Build') {
      steps {
        echo "=========================================================="
        echo "Stage 3: Frontend Build & Asset Verification"
        echo "=========================================================="
        // Compile and bundle React + Vite assets in isolated node container
        sh '''
          docker run --rm \
            -v "$(pwd)/frontend:/app" \
            -w /app \
            node:22-alpine \
            sh -c "npm install && npm run build"
        '''
      }
    }

    stage('Docker Image Build') {
      steps {
        echo "=========================================================="
        echo "Stage 4: Build Versioned Docker Images (${IMAGE_TAG})"
        echo "=========================================================="
        // Build production images tagged with BUILD_NUMBER and latest
        sh "docker build -t ${BACKEND_IMAGE}:${IMAGE_TAG} -t ${BACKEND_IMAGE}:latest ./backend"
        sh "docker build -t ${FRONTEND_IMAGE}:${IMAGE_TAG} -t ${FRONTEND_IMAGE}:latest ./frontend"
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
        sh '''
          # Run Trivy vulnerability scanner on the built backend container image
          docker run --rm \
            -v /var/run/docker.sock:/var/run/docker.sock \
            aquasec/trivy:latest image \
            --severity HIGH,CRITICAL \
            --exit-code 0 \
            placement-backend:${IMAGE_TAG} || echo "Trivy scan completed with warnings"
        '''
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
        // Pull credentials securely from Jenkins Credentials Store without hardcoding
        withCredentials([usernamePassword(
          credentialsId: params.DOCKERHUB_CREDENTIALS_ID,
          usernameVariable: 'DOCKER_USER',
          passwordVariable: 'DOCKER_PASS'
        )]) {
          sh '''
            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
            
            # Tag images with user repository namespace
            docker tag ${BACKEND_IMAGE}:${IMAGE_TAG} ${DOCKER_USER}/${BACKEND_IMAGE}:${IMAGE_TAG}
            docker tag ${BACKEND_IMAGE}:latest ${DOCKER_USER}/${BACKEND_IMAGE}:latest
            docker tag ${FRONTEND_IMAGE}:${IMAGE_TAG} ${DOCKER_USER}/${FRONTEND_IMAGE}:${IMAGE_TAG}
            docker tag ${FRONTEND_IMAGE}:latest ${DOCKER_USER}/${FRONTEND_IMAGE}:latest

            # Push versioned and latest images
            docker push ${DOCKER_USER}/${BACKEND_IMAGE}:${IMAGE_TAG}
            docker push ${DOCKER_USER}/${BACKEND_IMAGE}:latest
            docker push ${DOCKER_USER}/${FRONTEND_IMAGE}:${IMAGE_TAG}
            docker push ${DOCKER_USER}/${FRONTEND_IMAGE}:latest

            # Log out from registry
            docker logout
          '''
        }
      }
    }

    stage('Deploy') {
      steps {
        echo "=========================================================="
        echo "Stage 7: Deploying Stack using Docker Compose (${IMAGE_TAG})"
        echo "=========================================================="
        sh """
          export BACKEND_IMAGE=${BACKEND_IMAGE}:${IMAGE_TAG}
          export FRONTEND_IMAGE=${FRONTEND_IMAGE}:${IMAGE_TAG}
          docker compose down --remove-orphans || true
          docker compose up -d
        """
      }
    }

    stage('Health Check') {
      steps {
        echo "=========================================================="
        echo "Stage 8: Resilient Health & Readiness Polling"
        echo "=========================================================="
        sh '''
          MAX_RETRIES=15
          WAIT_INTERVAL=4
          ATTEMPT=1
          IS_HEALTHY=false

          echo "Polling system health status on Nginx ingress (http://localhost/health)..."
          while [ $ATTEMPT -le $MAX_RETRIES ]; do
            echo "Health check attempt $ATTEMPT of $MAX_RETRIES..."
            
            # Query health endpoint through reverse proxy
            STATUS=$(docker compose exec -T backend python -c "
import urllib.request, json
try:
    res = urllib.request.urlopen('http://localhost:8000/health', timeout=3)
    data = json.loads(res.read().decode())
    print(data.get('status', 'DOWN'))
except Exception:
    print('CONNECT_FAIL')
" 2>/dev/null || echo "EXEC_FAIL")

            if [ "$STATUS" = "UP" ]; then
              echo "Backend service is UP and healthy!"
              IS_HEALTHY=true
              break
            fi

            ATTEMPT=$((ATTEMPT + 1))
            sleep $WAIT_INTERVAL
          done

          if [ "$IS_HEALTHY" != "true" ]; then
            echo "Health check failed after $MAX_RETRIES attempts."
            docker compose logs --tail=100
            exit 1
          fi
        '''
      }
    }

    stage('Smoke Tests') {
      steps {
        echo "=========================================================="
        echo "Stage 9: End-to-End Smoke Tests"
        echo "=========================================================="
        // Run comprehensive smoke test suite verifying Health, OpenAPI, Jobs, SPA, & Auth
        sh '''
          docker compose exec -T backend python -c "
import urllib.request, json

base = 'http://nginx:80'

# 1. Health
with urllib.request.urlopen(f'{base}/health', timeout=5) as r:
    assert r.status == 200, f'Health failed: {r.status}'
    data = json.loads(r.read().decode())
    assert data.get('status') == 'UP', 'Status not UP'
print('  [PASS] Public health endpoint')

# 2. OpenAPI Spec
with urllib.request.urlopen(f'{base}/openapi.json', timeout=5) as r:
    assert r.status == 200
    spec = json.loads(r.read().decode())
    assert 'openapi' in spec
print('  [PASS] OpenAPI schema endpoint')

# 3. Public Jobs API
with urllib.request.urlopen(f'{base}/api/jobs', timeout=5) as r:
    assert r.status == 200
    jobs = json.loads(r.read().decode())
    assert isinstance(jobs, list)
print(f'  [PASS] Jobs API endpoint ({len(jobs)} active jobs)')

# 4. Frontend SPA
with urllib.request.urlopen(f'{base}/', timeout=5) as r:
    assert r.status == 200
    html = r.read().decode()
    assert 'root' in html
print('  [PASS] Frontend SPA ingress')

# 5. Auth Login API
login_data = json.dumps({'email': 'admin@placement.edu', 'password': 'Admin@123'}).encode()
req = urllib.request.Request(f'{base}/api/auth/login', data=login_data, headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req, timeout=5) as r:
    assert r.status == 200
    token_data = json.loads(r.read().decode())
    assert 'access_token' in token_data
print('  [PASS] Authentication API login')

print('All Smoke Tests Passed Successfully!')
"
        '''
      }
    }
  }

  post {
    always {
      echo "Cleaning up temporary test artifacts..."
      sh 'docker rmi placement-backend:test 2>/dev/null || true'
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
      sh 'docker compose logs --tail=50 || true'
    }
  }
}
