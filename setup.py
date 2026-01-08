# setup.py
import os
import sys
import subprocess

def setup_environment():
    """Setup the application environment"""
    print("🚀 Setting up Branch CS Messaging App...")
    
    # Create necessary directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('.streamlit', exist_ok=True)
    
    print("📁 Created directories")
    
    # Create .streamlit/config.toml
    config_content = """
[theme]
primaryColor = "#0d6efd"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f8f9fa"
textColor = "#262730"
font = "sans serif"
"""
    
    with open('.streamlit/config.toml', 'w') as f:
        f.write(config_content)
    
    print("⚙️ Created Streamlit config")
    
    # Check if CSV exists, if not provide instructions
    csv_path = 'data/GeneralistRails_Project_MessageData.csv'
    if not os.path.exists(csv_path):
        print("\n⚠️  IMPORTANT: CSV file not found!")
        print("Please place 'GeneralistRails_Project_MessageData.csv' in the 'data' folder.")
        print("\nTo create sample data instead, press Enter.")
        input("Press Enter to continue with sample data...")
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run the app: streamlit run app.py")
    print("3. Open browser: http://localhost:8501")

if __name__ == "__main__":
    setup_environment()
