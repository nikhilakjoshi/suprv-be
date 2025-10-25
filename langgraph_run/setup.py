#!/usr/bin/env python3
"""
Setup script for the LangGraph audio processing system.
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"  Command: {cmd}")
        print(f"  Error: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("✗ Python 3.8 or higher is required")
        print(f"  Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    else:
        print(
            f"✓ Python version {version.major}.{version.minor}.{version.micro} is compatible"
        )
        return True


def install_dependencies():
    """Install required dependencies."""
    requirements_file = Path(__file__).parent / "requirements.txt"
    if not requirements_file.exists():
        print("✗ requirements.txt not found")
        return False

    cmd = f"{sys.executable} -m pip install -r {requirements_file}"
    return run_command(cmd, "Installing dependencies")


def setup_environment():
    """Setup environment configuration."""
    env_example = Path(__file__).parent / ".env.example"
    env_file = Path(__file__).parent / ".env"

    if not env_example.exists():
        print("✗ .env.example not found")
        return False

    if env_file.exists():
        print("✓ .env file already exists")
        return True

    try:
        with open(env_example, "r") as f:
            content = f.read()

        with open(env_file, "w") as f:
            f.write(content)

        print("✓ Created .env file from template")
        print("  Please edit .env with your actual configuration values")
        return True
    except Exception as e:
        print(f"✗ Failed to create .env file: {e}")
        return False


def check_google_cloud_auth():
    """Check Google Cloud authentication."""
    print("🔧 Checking Google Cloud authentication...")

    # Check for service account key
    gcp_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if gcp_creds and Path(gcp_creds).exists():
        print("✓ Google Cloud service account credentials found")
        return True

    # Check gcloud CLI authentication
    cmd = "gcloud auth application-default print-access-token"
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, capture_output=True, text=True
        )
        if result.stdout.strip():
            print("✓ Google Cloud CLI authentication found")
            return True
    except subprocess.CalledProcessError:
        pass

    print("⚠️  Google Cloud authentication not detected")
    print("   Please set up authentication using one of these methods:")
    print("   1. Service Account Key:")
    print("      export GOOGLE_APPLICATION_CREDENTIALS='path/to/key.json'")
    print("   2. gcloud CLI:")
    print("      gcloud auth application-default login")
    return False


def run_tests():
    """Run system tests."""
    test_file = Path(__file__).parent / "test.py"
    if not test_file.exists():
        print("✗ test.py not found")
        return False

    cmd = f"{sys.executable} {test_file}"
    return run_command(cmd, "Running system tests")


def main():
    """Main setup function."""
    print("LangGraph Audio Processing System Setup")
    print("=" * 50)

    steps = [
        ("Checking Python version", check_python_version),
        ("Installing dependencies", install_dependencies),
        ("Setting up environment", setup_environment),
        ("Checking Google Cloud auth", check_google_cloud_auth),
        ("Running tests", run_tests),
    ]

    failed_steps = []

    for step_name, step_func in steps:
        print()
        if not step_func():
            failed_steps.append(step_name)

    print("\n" + "=" * 50)
    print("Setup Summary:")

    if not failed_steps:
        print("✓ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Edit .env file with your configuration")
        print("2. Set up Google Cloud authentication if needed")
        print("3. Run: python -m langgraph_run.main demo")
    else:
        print(f"✗ Setup completed with {len(failed_steps)} issues:")
        for step in failed_steps:
            print(f"  - {step}")
        print("\nPlease resolve the issues above before proceeding.")

    return len(failed_steps) == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
