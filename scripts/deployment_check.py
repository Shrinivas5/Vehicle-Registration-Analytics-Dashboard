#!/usr/bin/env python3
"""
Deployment readiness checker for Vahan Dashboard
Validates all components before submission
"""

import os
import sys
import sqlite3
import importlib.util
from pathlib import Path
import subprocess

class DeploymentChecker:
    def __init__(self):
        self.checks_passed = 0
        self.total_checks = 0
        self.issues = []

    def check_file_exists(self, filepath, description):
        """Check if required file exists"""
        self.total_checks += 1
        if os.path.exists(filepath):
            print(f"✅ {description}: {filepath}")
            self.checks_passed += 1
            return True
        else:
            print(f"❌ {description}: {filepath} - NOT FOUND")
            self.issues.append(f"Missing file: {filepath}")
            return False

    def check_python_imports(self):
        """Check if all required Python modules can be imported"""
        required_modules = [
            'streamlit', 'pandas', 'plotly', 'sqlite3', 
            'numpy', 'scipy', 'scikit-learn'
        ]
        
        for module in required_modules:
            self.total_checks += 1
            try:
                importlib.import_module(module)
                print(f"✅ Python module: {module}")
                self.checks_passed += 1
            except ImportError:
                print(f"❌ Python module: {module} - NOT INSTALLED")
                self.issues.append(f"Missing Python module: {module}")

    def check_database(self):
        """Check database connectivity and structure"""
        db_path = "data/vahan_data.db"
        self.total_checks += 1
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if main tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = ['vehicle_registrations', 'manufacturers', 'growth_metrics']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if not missing_tables:
                print(f"✅ Database structure: All required tables present")
                self.checks_passed += 1
            else:
                print(f"❌ Database structure: Missing tables: {missing_tables}")
                self.issues.append(f"Missing database tables: {missing_tables}")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Database connectivity: {str(e)}")
            self.issues.append(f"Database error: {str(e)}")

    def check_dashboard_components(self):
        """Check if dashboard components are properly configured"""
        dashboard_files = [
            "dashboard/main.py",
            "dashboard/components.py",
            "dashboard/config.py"
        ]
        
        for file in dashboard_files:
            self.check_file_exists(file, "Dashboard component")

    def check_analytics_engine(self):
        """Test analytics engine functionality"""
        self.total_checks += 1
        try:
            sys.path.append('src')
            from analytics_engine import VahanAnalyticsEngine
            
            # Create test instance
            engine = VahanAnalyticsEngine("data/vahan_data.db")
            
            # Test basic functionality
            test_data = engine.get_sample_data()
            if len(test_data) > 0:
                print("✅ Analytics engine: Basic functionality working")
                self.checks_passed += 1
            else:
                print("❌ Analytics engine: No data returned")
                self.issues.append("Analytics engine returns no data")
                
        except Exception as e:
            print(f"❌ Analytics engine: {str(e)}")
            self.issues.append(f"Analytics engine error: {str(e)}")

    def check_documentation(self):
        """Check documentation completeness"""
        docs = [
            ("README.md", "Main README"),
            ("docs/API_DOCUMENTATION.md", "API Documentation"),
            ("docs/DEPLOYMENT_GUIDE.md", "Deployment Guide"),
            ("docs/USER_MANUAL.md", "User Manual"),
            ("docs/VIDEO_WALKTHROUGH_SCRIPT.md", "Video Script")
        ]
        
        for filepath, description in docs:
            self.check_file_exists(filepath, description)

    def run_all_checks(self):
        """Run all deployment checks"""
        print("🔍 Running Vahan Dashboard Deployment Checks...\n")
        
        print("📁 Checking File Structure...")
        self.check_file_exists("requirements.txt", "Requirements file")
        self.check_file_exists("setup.py", "Setup script")
        self.check_file_exists("run_dashboard.py", "Dashboard runner")
        
        print("\n📚 Checking Documentation...")
        self.check_documentation()
        
        print("\n🐍 Checking Python Dependencies...")
        self.check_python_imports()
        
        print("\n🗄️ Checking Database...")
        self.check_database()
        
        print("\n📊 Checking Dashboard Components...")
        self.check_dashboard_components()
        
        print("\n🔬 Checking Analytics Engine...")
        self.check_analytics_engine()
        
        print(f"\n📋 DEPLOYMENT CHECK SUMMARY")
        print(f"{'='*50}")
        print(f"Checks Passed: {self.checks_passed}/{self.total_checks}")
        print(f"Success Rate: {(self.checks_passed/self.total_checks)*100:.1f}%")
        
        if self.issues:
            print(f"\n⚠️  ISSUES TO RESOLVE:")
            for i, issue in enumerate(self.issues, 1):
                print(f"   {i}. {issue}")
        
        if self.checks_passed == self.total_checks:
            print(f"\n🎉 ALL CHECKS PASSED! Ready for deployment and submission.")
            return True
        else:
            print(f"\n❌ Please resolve the issues above before submission.")
            return False

if __name__ == "__main__":
    checker = DeploymentChecker()
    success = checker.run_all_checks()
    sys.exit(0 if success else 1)
