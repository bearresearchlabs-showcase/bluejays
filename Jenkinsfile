// BIRD Benchmark Infrastructure - Parallel validation pipeline
// CI/CD: Jenkins. Local testing: same pipeline with .env.
// Uses ANTHROPIC_API_KEY from .env for Anthropic models when multiple sessions run independently.
// tb3_workbench always available for assertions.

pipeline {
    agent any

    environment {
        // PG_HOST, PG_USER, PG_PASSWORD, PG_DATABASE, DB_PORTS_START from .env or Jenkins
        // ANTHROPIC_API_KEY from .env for Claude/Anthropic model steps (qa-claude, etc.)
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'chmod +x scripts/jenkins_run.sh'
                sh './scripts/jenkins_run.sh python3 scripts/env_validator.py --op db || true'
            }
        }

        stage('Build (db + tb3_workbench + langgraph)') {
            steps {
                sh 'PYTHONWARNINGS=ignore ./scripts/build.sh --no-venv'
            }
        }

        stage('Docker Compose') {
            steps {
                sh './scripts/jenkins_run.sh docker compose -f docker/docker-compose.multi-db.yml up -d'
                sh 'sleep 15'
            }
        }

        stage('Parallel Validate') {
            parallel {
                stage('db-1') { steps { sh './scripts/jenkins_run.sh python3 scripts/db_check.py validate 1 || true' } }
                stage('db-2') { steps { sh './scripts/jenkins_run.sh python3 scripts/db_check.py validate 2 || true' } }
                stage('db-3') { steps { sh './scripts/jenkins_run.sh python3 scripts/db_check.py validate 3 || true' } }
                stage('db-4') { steps { sh './scripts/jenkins_run.sh python3 scripts/db_check.py validate 4 || true' } }
                stage('db-5') { steps { sh './scripts/jenkins_run.sh python3 scripts/db_check.py validate 5 || true' } }
                stage('db-6') { steps { sh './scripts/jenkins_run.sh python3 scripts/db_check.py validate 6 || true' } }
                stage('db-7') { steps { sh './scripts/jenkins_run.sh python3 scripts/db_check.py validate 7 || true' } }
                stage('db-8') { steps { sh './scripts/jenkins_run.sh python3 scripts/db_check.py validate 8 || true' } }
                stage('db-9') { steps { sh './scripts/jenkins_run.sh python3 scripts/db_check.py validate 9 || true' } }
                stage('db-10') { steps { sh './scripts/jenkins_run.sh python3 scripts/db_check.py validate 10 || true' } }
                stage('db-11') { steps { sh './scripts/jenkins_run.sh python3 scripts/db_check.py validate 11 || true' } }
                stage('db-12') { steps { sh './scripts/jenkins_run.sh python3 scripts/db_check.py validate 12 || true' } }
                stage('db-13') { steps { sh './scripts/jenkins_run.sh python3 scripts/db_check.py validate 13 || true' } }
                stage('db-14') { steps { sh './scripts/jenkins_run.sh python3 scripts/db_check.py validate 14 || true' } }
                stage('db-15') { steps { sh './scripts/jenkins_run.sh python3 scripts/db_check.py validate 15 || true' } }
                stage('db-16') { steps { sh './scripts/jenkins_run.sh python3 scripts/db_check.py validate 16 || true' } }
            }
        }

        stage('BIRD Export') {
            steps {
                sh './scripts/jenkins_run.sh python3 scripts/bird_export.py -a --single || true'
            }
        }

        stage('BIRD Workbench') {
            steps {
                sh './scripts/jenkins_run.sh python3 scripts/db_check.py bird-workbench -a || true'
            }
        }

        stage('GDPval LangGraph') {
            steps {
                sh './scripts/jenkins_run.sh python3 scripts/db_check.py gdpval-langgraph -a || true'
            }
        }

        stage('MVC Backend Test') {
            steps {
                sh './scripts/jenkins_run.sh python3 scripts/mvc_backend_test.py 2>&1 | head -80 || true'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'traces/*,logs/*,bird_export/*,results/compliance_report.json,gdpval_langgraph_report.json', allowEmptyArchive: true
            sh 'docker compose -f docker/docker-compose.multi-db.yml down || true'
        }
    }
}
