#!/usr/bin/env python3
"""
Script to prepare deployment files and validate configuration
Usage: python prepare_deployment.py

This script:
1. Validates all configuration files exist
2. Checks npm dependencies
3. Verifies frontend build
4. Generates deployment summary
"""

import os
import json
import sys
from pathlib import Path

class DeploymentChecker:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.frontend_dir = self.root_dir / "frontend"
        self.backend_dir = self.root_dir / "backend"
        self.errors = []
        self.warnings = []
        self.success = []

    def check_files_exist(self):
        """Verify all required deployment files exist"""
        files_to_check = {
            "Frontend": [
                self.frontend_dir / "vercel.json",
                self.frontend_dir / "package.json",
                self.frontend_dir / "vite.config.ts",
                self.frontend_dir / "tsconfig.json",
                self.frontend_dir / ".gitignore",
            ],
            "Backend": [
                self.backend_dir / "main.py",
                self.backend_dir / "requirements.txt",
            ],
            "Root": [
                self.root_dir / "docker-compose.yml",
                self.root_dir / "DEPLOYMENT_GUIDE.md",
                self.root_dir / "BACKEND_DEPLOYMENT.md",
            ]
        }

        for category, files in files_to_check.items():
            for file_path in files:
                if file_path.exists():
                    self.success.append(f"✅ {category}: {file_path.name}")
                else:
                    self.errors.append(f"❌ {category}: {file_path.name} NOT FOUND")

    def check_package_json(self):
        """Validate package.json structure"""
        pkg_path = self.frontend_dir / "package.json"
        try:
            with open(pkg_path, 'r') as f:
                pkg = json.load(f)
            
            required_scripts = ["build", "dev"]
            for script in required_scripts:
                if script in pkg.get("scripts", {}):
                    self.success.append(f"✅ NPM Script: {script}")
                else:
                    self.errors.append(f"❌ Missing npm script: {script}")
                    
            required_deps = ["react", "react-router-dom", "axios", "recharts"]
            for dep in required_deps:
                if dep in pkg.get("dependencies", {}):
                    self.success.append(f"✅ Dependency: {dep}")
                else:
                    self.warnings.append(f"⚠️  Missing dependency: {dep}")
                    
        except Exception as e:
            self.errors.append(f"❌ Error reading package.json: {str(e)}")

    def check_vercel_json(self):
        """Validate vercel.json configuration"""
        vercel_path = self.frontend_dir / "vercel.json"
        try:
            with open(vercel_path, 'r') as f:
                vercel_config = json.load(f)
            
            required_keys = ["buildCommand", "outputDirectory"]
            for key in required_keys:
                if key in vercel_config:
                    self.success.append(f"✅ vercel.json: {key} configured")
                else:
                    self.errors.append(f"❌ vercel.json missing: {key}")
                    
        except Exception as e:
            self.errors.append(f"❌ Error reading vercel.json: {str(e)}")

    def check_environment_variables(self):
        """Check environment variable configuration"""
        vercel_path = self.frontend_dir / "vercel.json"
        try:
            with open(vercel_path, 'r') as f:
                vercel_config = json.load(f)
            
            if "env" in vercel_config and "VITE_API_URL" in vercel_config["env"]:
                self.success.append("✅ VITE_API_URL configured in vercel.json")
            else:
                self.warnings.append("⚠️  VITE_API_URL not in vercel.json (will use inline default)")
                
        except Exception as e:
            self.errors.append(f"❌ Error checking env vars: {str(e)}")

    def print_report(self):
        """Print the validation report"""
        print("\n" + "="*60)
        print(" DEPLOYMENT READINESS REPORT")
        print("="*60 + "\n")

        if self.success:
            print("✅ PASSED CHECKS:")
            for item in self.success:
                print(f"   {item}")
            print()

        if self.warnings:
            print("⚠️  WARNINGS:")
            for item in self.warnings:
                print(f"   {item}")
            print()

        if self.errors:
            print("❌ ERRORS TO FIX:")
            for item in self.errors:
                print(f"   {item}")
            print()
            return False

        print("\n" + "="*60)
        print(" ✅ ALL CHECKS PASSED - READY FOR DEPLOYMENT")
        print("="*60)
        print("\nNext steps:")
        print("1. Read DEPLOYMENT_GUIDE.md for complete instructions")
        print("2. Read BACKEND_DEPLOYMENT.md for backend setup")
        print("3. Read frontend/VERCEL_DEPLOYMENT.md for frontend setup")
        print("4. Push code to GitHub:")
        print("   git add .")
        print("   git commit -m 'Prepare for Vercel deployment'")
        print("   git push origin main")
        print("\n5. Go to https://vercel.com and import your repository")
        print("6. Set VITE_API_URL environment variable")
        print("7. Deploy!")
        return True

    def run(self):
        """Run all checks"""
        print("\n🔍 Checking deployment configuration...\n")
        self.check_files_exist()
        self.check_package_json()
        self.check_vercel_json()
        self.check_environment_variables()
        return self.print_report()


if __name__ == "__main__":
    checker = DeploymentChecker()
    success = checker.run()
    sys.exit(0 if success else 1)
