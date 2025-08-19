#!/usr/bin/env python3
"""
Launch script for the Vahan Dashboard
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit dashboard"""
    print("Starting Vehicle Registration Analytics Dashboard...")
    print("Dashboard will be available at: http://localhost:8501")
    print("Press Ctrl+C to stop the dashboard")
    print("-" * 50)
    
    # Change to dashboard directory
    dashboard_path = os.path.join(os.path.dirname(__file__), 'dashboard')
    
    try:
        # Run streamlit
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 
            'main.py',
            '--server.port=8501',
            '--server.address=localhost',
            '--browser.gatherUsageStats=false'
        ], cwd=dashboard_path, check=True)
    
    except KeyboardInterrupt:
        print("\nDashboard stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"Error running dashboard: {e}")
        print("Make sure Streamlit is installed: pip install streamlit")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
