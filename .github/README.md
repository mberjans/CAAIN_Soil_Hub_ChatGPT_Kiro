# AFAS CI/CD Pipeline Documentation

This directory contains the CI/CD pipeline configuration for the Autonomous Farm Advisory System (AFAS).

## Workflows

### 1. Main CI Pipeline (`ci.yml`)
**Triggers:** Push to main/develop, Pull requests
**Purpose:** Comprehensive testing and validation

**Jobs:**
- **Code Quality**: Black formatting, Flake8 linting, MyPy type checking, Bandit security scan
- **Unit Tests**: Parallel testing of all 7 microservices
- **Agricultural Validation**: Expert-validated agricultural logic testing
- **Integration Tests**: End-to-end testing with databases
- **Performance Tests**: Response time validation (<3s requirement)
- **Build**: Package creation for deployment
- **Deployment Check**: Final readiness validation

### 2. Agricultural Validation Pipeline (`agricultural-validation.yml`)
**Triggers:** Changes to agricultural logic files
**Purpose:** Specialized validation for agricultural accuracy

**Jobs:**
- **Agricultural Accuracy Tests**: Nutrient calculations, crop suitability, soil health
- **Data Validation**: Soil test ranges, agricultural units consistency
- **Real Farm Data Testing**: Iowa, California, and challenging soil scenarios
- **Safety Checks**: Dangerous recommendation prevention, fertilizer limits
- **Expert Review**: Automated flagging for agricultural expert review

### 3. Security Pipeline (`security.yml`)
**Triggers:** Push, PR, Daily schedule
**Purpose:** Comprehensive security scanning

**Jobs:**
- **Dependency Scan**: Vulnerability scanning with Safety
- **Static Analysis**: Bandit and Semgrep security analysis
- **Agricultural Data Security**: Farm data protection validation
- **API Security**: Authentication, authorization, input validation testing
- **Container Security**: Trivy vulnerability scanning
- **Secrets Scan**: TruffleHog secrets detection

### 4. Deployment Pipeline (`deploy.yml`)
**Triggers:** Push to main, Tags, Manual dispatch
**Purpose:** Automated deployment to staging/production

**Jobs:**
- **Pre-deployment Checks**: Readiness validation, expert approvals
- **Build Services**: Package all 7 microservices
- **Deploy Staging**: Automated staging deployment with validation
- **Deploy Production**: Blue-green production deployment
- **Post-deployment Monitoring**: Health checks and performance monitoring
- **Rollback**: Automatic rollback on failure

## Key Features

### Agricultural-Specific Validation
- **Expert Review Requirements**: Automatic flagging for agricultural logic changes
- **Extension Guidelines Validation**: Compliance with university extension recommendations
- **Safety Limits**: Prevention of dangerous fertilizer recommendations
- **Regional Adaptation**: Testing across different agricultural regions

### Performance Requirements
- **Response Time**: <3 seconds for recommendations
- **Concurrency**: Support for 100+ concurrent users
- **Agricultural Accuracy**: Maintained under load conditions
- **Database Performance**: <500ms for soil test queries

### Security Standards
- **Agricultural Data Protection**: GPS coordinates, financial data encryption
- **API Security**: Authentication, authorization, rate limiting
- **Dependency Scanning**: Daily vulnerability checks
- **Secrets Management**: Prevention of API key exposure

## Supporting Scripts

### Validation Scripts (`scripts/`)
- `validate_agricultural_logic.py`: Core agricultural logic validation
- `check_agricultural_sources.py`: Source credibility verification
- `validate_performance.py`: Performance requirement validation
- `deployment_readiness_check.py`: Pre-deployment validation

### Test Structure
```
tests/
├── unit/                    # Service-specific unit tests
├── integration/             # Cross-service integration tests
├── agricultural/            # Agricultural accuracy tests
│   ├── test_nutrient_calculations.py
│   ├── test_crop_suitability.py
│   └── test_soil_health.py
├── performance/             # Performance and load tests
└── security/               # Security-specific tests
```

## Environment Configuration

### Required Secrets
- `DATABASE_URL`: PostgreSQL connection string
- `MONGODB_URL`: MongoDB connection string
- `REDIS_URL`: Redis connection string
- Agricultural API keys (environment-specific)

### Environment Variables
- `PYTHON_VERSION`: Python version (default: 3.11)
- `AGRICULTURAL_EXPERT_VALIDATION`: Enable expert validation
- `RECOMMENDATION_CONFIDENCE_THRESHOLD`: Minimum confidence score
- `ENABLE_CONSERVATIVE_MODE`: Conservative recommendation mode

## Deployment Environments

### Staging
- **Purpose**: Pre-production testing and validation
- **Triggers**: Push to main branch
- **Features**: Full agricultural validation, performance testing
- **Database**: Staging database with test data

### Production
- **Purpose**: Live system serving farmers
- **Triggers**: Tagged releases, manual deployment
- **Features**: Blue-green deployment, comprehensive monitoring
- **Requirements**: Agricultural expert approval, full test suite pass

## Monitoring and Alerting

### Key Metrics
- **Agricultural Accuracy**: Recommendation confidence scores
- **Performance**: Response times, error rates
- **Security**: Vulnerability counts, failed authentication attempts
- **Usage**: Active users, recommendation requests

### Alerts
- **Performance Degradation**: Response times >3 seconds
- **Agricultural Accuracy**: Confidence scores <80%
- **Security Issues**: Critical vulnerabilities detected
- **Deployment Failures**: Failed deployments or rollbacks

## Best Practices

### Code Changes
1. All agricultural logic changes require expert review
2. Performance tests must pass before merge
3. Security scans must show no critical issues
4. Test coverage must be >80%

### Deployment
1. Staging deployment and validation required
2. Agricultural expert approval for production
3. Gradual rollout with monitoring
4. Rollback capability maintained

### Monitoring
1. Continuous performance monitoring
2. Agricultural accuracy tracking
3. Security vulnerability scanning
4. User feedback integration

## Troubleshooting

### Common Issues
- **Agricultural Validation Failures**: Check extension guideline compliance
- **Performance Test Failures**: Optimize database queries, check resource usage
- **Security Scan Failures**: Update dependencies, fix code issues
- **Deployment Failures**: Verify configuration, check service health

### Support
- Agricultural issues: Consult agricultural experts
- Technical issues: Check logs, run local validation scripts
- Security issues: Review security scan reports
- Performance issues: Check monitoring dashboards

This CI/CD pipeline ensures that AFAS maintains the highest standards of agricultural accuracy, technical quality, and security while enabling rapid, reliable deployments.