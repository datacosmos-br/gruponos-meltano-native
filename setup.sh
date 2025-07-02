#!/bin/bash

# =============================================================================
# GRUPONOS MELTANO NATIVE - SETUP SCRIPT
# =============================================================================

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project information
PROJECT_NAME="GrupoNOS WMS Meltano Native"
PROJECT_DIR="$(pwd)"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  $PROJECT_NAME - Setup Script${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Function to print status messages
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3.9+ is available
check_python() {
    print_status "Checking Python version..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
        
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 9 ]; then
            print_status "Python $PYTHON_VERSION found - OK"
            PYTHON_CMD="python3"
        else
            print_error "Python 3.9+ required, found $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 not found. Please install Python 3.9+ first."
        exit 1
    fi
}

# Check if Oracle Instant Client is available
check_oracle_client() {
    print_status "Checking Oracle Instant Client..."
    
    if [ -z "$ORACLE_HOME" ] && [ -z "$LD_LIBRARY_PATH" ]; then
        print_warning "Oracle Instant Client environment variables not set."
        print_warning "Make sure Oracle Instant Client is installed and configured."
        print_warning "Set ORACLE_HOME and LD_LIBRARY_PATH if needed."
    else
        print_status "Oracle environment variables detected - OK"
    fi
}

# Create virtual environment
create_venv() {
    print_status "Creating Python virtual environment..."
    
    if [ ! -d ".venv" ]; then
        $PYTHON_CMD -m venv .venv
        print_status "Virtual environment created"
    else
        print_status "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    print_status "Virtual environment activated"
    
    # Upgrade pip
    pip install --upgrade pip
    print_status "pip upgraded"
}

# Install Meltano and dependencies
install_meltano() {
    print_status "Installing Meltano and core dependencies..."
    
    # Install Meltano
    pip install "meltano>=3.0.0,<4.0.0"
    
    # Install Oracle database support
    pip install "oracledb>=2.0.0"
    pip install "cx-Oracle>=8.3.0"  # Fallback Oracle driver
    
    # Install dbt with Oracle adapter
    pip install "dbt-core>=1.8.0,<2.0.0"
    pip install "dbt-oracle>=1.8.0,<2.0.0"
    
    # Install additional utilities
    pip install "pandas>=2.0.0"
    pip install "sqlalchemy>=2.0.0"
    pip install "pydantic>=2.0.0"
    
    print_status "Core dependencies installed"
}

# Install local tap and target
install_local_plugins() {
    print_status "Installing local tap-oracle-wms and target-oracle-wms..."
    
    # Check if local plugins exist
    TAP_PATH="../flext-tap-oracle-wms"
    TARGET_PATH="../flext-target-oracle-wms"
    
    if [ -d "$TAP_PATH" ]; then
        pip install -e "$TAP_PATH"
        print_status "tap-oracle-wms installed from $TAP_PATH"
    else
        print_warning "Local tap-oracle-wms not found at $TAP_PATH"
        print_warning "You may need to install it manually or adjust the path in meltano.yml"
    fi
    
    if [ -d "$TARGET_PATH" ]; then
        pip install -e "$TARGET_PATH"
        print_status "target-oracle-wms installed from $TARGET_PATH"
    else
        print_warning "Local target-oracle-wms not found at $TARGET_PATH"
        print_warning "You may need to install it manually or use an alternative target"
    fi
}

# Setup environment configuration
setup_environment() {
    print_status "Setting up environment configuration..."
    
    # Copy .env.example to .env if it doesn't exist
    if [ ! -f ".env" ]; then
        cp .env.example .env
        print_status "Created .env file from .env.example"
        print_warning "Please edit .env file with your actual database credentials"
    else
        print_status ".env file already exists"
    fi
    
    # Set MELTANO_PROJECT_ROOT in .env
    if grep -q "MELTANO_PROJECT_ROOT=" .env; then
        sed -i "s|MELTANO_PROJECT_ROOT=.*|MELTANO_PROJECT_ROOT=$PROJECT_DIR|" .env
    else
        echo "MELTANO_PROJECT_ROOT=$PROJECT_DIR" >> .env
    fi
    
    print_status "Environment configuration updated"
}

# Initialize Meltano project
initialize_meltano() {
    print_status "Initializing Meltano project..."
    
    # Source environment variables
    if [ -f ".env" ]; then
        export $(grep -v '^#' .env | xargs)
    fi
    
    # Initialize Meltano if not already done
    if [ ! -f ".meltano.yml" ]; then
        meltano install
        print_status "Meltano plugins installed"
    else
        print_status "Meltano already initialized"
    fi
}

# Setup dbt
setup_dbt() {
    print_status "Setting up dbt..."
    
    # Create necessary directories
    mkdir -p transform/profiles
    mkdir -p transform/logs
    mkdir -p transform/target
    mkdir -p transform/models/staging
    mkdir -p transform/models/intermediate
    mkdir -p transform/models/marts/core
    mkdir -p transform/models/marts/warehouse
    mkdir -p transform/models/marts/inventory
    mkdir -p transform/macros
    mkdir -p transform/tests
    mkdir -p transform/analyses
    mkdir -p transform/seeds
    mkdir -p transform/snapshots
    
    print_status "dbt directory structure created"
    
    # Test dbt connection (if credentials are available)
    if [ -f ".env" ]; then
        export $(grep -v '^#' .env | xargs)
        cd transform
        if dbt debug --profiles-dir profiles 2>/dev/null; then
            print_status "dbt connection test successful"
        else
            print_warning "dbt connection test failed - check your database credentials"
        fi
        cd ..
    fi
}

# Setup orchestration (optional)
setup_orchestration() {
    if [ "$1" = "--with-airflow" ]; then
        print_status "Setting up Airflow orchestration..."
        
        # Install Airflow
        pip install "apache-airflow>=2.9.0"
        pip install "apache-airflow-providers-oracle"
        
        # Create Airflow directories
        mkdir -p orchestrate/dags
        mkdir -p orchestrate/plugins
        mkdir -p orchestrate/logs
        mkdir -p orchestrate/config
        
        # Initialize Airflow database
        export AIRFLOW_HOME="$PROJECT_DIR/orchestrate"
        airflow db init
        
        print_status "Airflow setup completed"
        print_status "Run 'airflow users create-admin' to create an admin user"
    fi
}

# Setup monitoring and logging
setup_monitoring() {
    print_status "Setting up monitoring and logging..."
    
    # Create log directories
    mkdir -p logs/meltano
    mkdir -p logs/dbt
    mkdir -p logs/tap-oracle-wms
    mkdir -p logs/target-oracle
    mkdir -p logs/airflow
    
    # Create monitoring directories
    mkdir -p monitoring/health-checks
    mkdir -p monitoring/performance
    mkdir -p monitoring/data-quality
    
    print_status "Monitoring structure created"
}

# Create utility scripts
create_scripts() {
    print_status "Creating utility scripts..."
    
    mkdir -p scripts
    
    # Create test connection script
    cat > scripts/test-connections.sh << 'EOF'
#!/bin/bash
echo "Testing WMS Oracle connection..."
meltano invoke tap-oracle-wms --test-connection

echo "Testing target Oracle connection..."
meltano invoke target-oracle --test-connection

echo "Testing dbt connection..."
cd transform && dbt debug --profiles-dir profiles
EOF
    
    # Create run pipeline script
    cat > scripts/run-pipeline.sh << 'EOF'
#!/bin/bash
set -e

ENVIRONMENT=${1:-dev}
echo "Running WMS pipeline in $ENVIRONMENT environment..."

# Set environment
export MELTANO_ENVIRONMENT=$ENVIRONMENT

# Run extraction and loading
echo "Step 1: Extract and Load data..."
meltano run tap-oracle-wms target-oracle

# Run dbt transformations  
echo "Step 2: Run dbt transformations..."
meltano invoke dbt-oracle-wms:run

# Run dbt tests
echo "Step 3: Run dbt tests..."
meltano invoke dbt-oracle-wms:test

echo "Pipeline completed successfully!"
EOF
    
    # Create schema discovery script
    cat > scripts/discover-schema.sh << 'EOF'
#!/bin/bash
echo "Discovering WMS schema..."
meltano invoke tap-oracle-wms --discover > schema/catalog.json
echo "Schema saved to schema/catalog.json"
EOF
    
    # Make scripts executable
    chmod +x scripts/*.sh
    
    print_status "Utility scripts created in scripts/ directory"
}

# Setup data quality checks
setup_data_quality() {
    print_status "Setting up data quality framework..."
    
    mkdir -p data-quality/tests
    mkdir -p data-quality/reports
    mkdir -p data-quality/configs
    
    # Create basic data quality config
    cat > data-quality/configs/quality-rules.yml << 'EOF'
# Data Quality Rules for WMS Sync
tables:
  allocation:
    row_count:
      min: 1000
      warn_threshold: 5000
    freshness:
      max_age_hours: 2
    columns:
      allocation_id:
        tests: [not_null, unique]
      quantity_allocated:
        tests: [not_null, positive]
        
  order_hdr:
    row_count:
      min: 100
    freshness:
      max_age_hours: 24
    columns:
      order_id:
        tests: [not_null, unique]
      total_amount:
        tests: [not_null, positive]
EOF
    
    print_status "Data quality framework setup completed"
}

# Main setup function
main() {
    print_status "Starting $PROJECT_NAME setup..."
    echo ""
    
    # Parse arguments
    WITH_AIRFLOW=false
    for arg in "$@"; do
        case $arg in
            --with-airflow)
                WITH_AIRFLOW=true
                shift
                ;;
        esac
    done
    
    # Run setup steps
    check_python
    check_oracle_client
    create_venv
    install_meltano
    install_local_plugins
    setup_environment
    initialize_meltano
    setup_dbt
    
    if [ "$WITH_AIRFLOW" = true ]; then
        setup_orchestration --with-airflow
    fi
    
    setup_monitoring
    create_scripts
    setup_data_quality
    
    echo ""
    print_status "Setup completed successfully!"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Edit .env file with your database credentials"
    echo "2. Test connections: ./scripts/test-connections.sh"
    echo "3. Discover schema: ./scripts/discover-schema.sh"
    echo "4. Run pipeline: ./scripts/run-pipeline.sh"
    echo ""
    echo -e "${BLUE}Useful commands:${NC}"
    echo "- Activate environment: source .venv/bin/activate"
    echo "- Run Meltano: meltano run tap-oracle-wms target-oracle"
    echo "- Run dbt: cd transform && dbt run --profiles-dir profiles"
    echo "- View logs: tail -f logs/meltano/meltano.log"
    echo ""
    print_status "Happy data pipelining! 🚀"
}

# Run main function with all arguments
main "$@"