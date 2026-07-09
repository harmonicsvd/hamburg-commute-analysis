#!/bin/bash

# J&J Deutschlandticket Analysis - Complete Setup Script
# This script sets up the entire project environment

echo "🎫 J&J Deutschlandticket Analysis - Setup Script"
echo "================================================"
echo ""

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "❌ Conda is not installed. Please install Anaconda or Miniconda first."
    echo "Visit: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

echo "✅ Conda found: $(conda --version)"
echo ""

# Create conda environment
echo "📦 Creating conda environment 'jandj'..."
conda create -n jandj python=3.10 -y
echo "✅ Environment 'jandj' created"
echo ""

# Activate environment
echo "🔄 Activating environment..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate jandj
echo "✅ Environment activated"
echo ""

# Install requirements
echo "📥 Installing Python packages..."
pip install -r requirements.txt
echo "✅ Packages installed"
echo ""

# Create necessary directories
echo "📁 Creating data directories..."
mkdir -p data
echo "✅ Data directories created"
echo ""

echo "🎉 Setup Complete!"
echo ""
echo "================================================"
echo "📋 NEXT STEPS:"
echo "================================================"
echo ""
echo "1. Activate the environment:"
echo "   conda activate jandj"
echo ""
echo "2. Launch the interactive dashboard:"
echo "   streamlit run streamlit_dashboard.py"
echo ""
echo "3. Access the dashboard at:"
echo "   http://localhost:8501"
echo ""
echo "================================================"
echo "📊 DATA AVAILABILITY:"
echo "================================================"
echo ""
echo "The dashboard uses existing data from:"
echo "- data/synthetic_employees_with_optimal_commutes.csv"
echo "- data/hvv_stations_filtered.csv"
echo "- jj_office_snapped.json"
echo ""
echo "Note: Run notebooks 01-05 only if you need to regenerate data."
echo "This can take several hours due to API calls and routing calculations."
echo ""
echo "================================================"
echo "🚀 Ready to analyze J&J Deutschlandticket adoption!"
echo "================================================"

# Ask if user wants to launch dashboard now
echo ""
read -p "Would you like to launch the dashboard now? (y/n): " launch_dashboard

if [ "$launch_dashboard" = "y" ] || [ "$launch_dashboard" = "Y" ]; then
    echo ""
    echo "🚀 Launching Streamlit dashboard..."
    echo "Access at: http://localhost:8501"
    echo ""
    streamlit run streamlit_dashboard.py
fi