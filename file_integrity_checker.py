import hashlib
import os
import json
from datetime import datetime

class FileIntegrityChecker:
    def __init__(self, baseline_file="baseline.json"):
        self.baseline_file = baseline_file
        self.baseline_data = self.load_baseline()

    def calculate_hash(self, file_path):
        """Calculate SHA-256 hash of a file"""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                # Read file in chunks for large files
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except IOError as e:
            print(f"Error reading file {file_path}: {e}")
            return None

    def load_baseline(self):
        """Load baseline data from file"""
        if os.path.exists(self.baseline_file):
            try:
                with open(self.baseline_file, "r") as f:
                    return json.load(f)
            except (IOError, json.JSONDecodeError) as e:
                print(f"Error loading baseline: {e}")
        return {}

    def save_baseline(self):
        """Save current baseline to file"""
        try:
            with open(self.baseline_file, "w") as f:
                json.dump(self.baseline_data, f, indent=4)
            print(f"Baseline saved to {self.baseline_file}")
        except IOError as e:
            print(f"Error saving baseline: {e}")

    def create_baseline(self, directory):
        """Create initial baseline for files in directory"""
        if not os.path.isdir(directory):
            print(f"Error: {directory} is not a valid directory")
            return

        self.baseline_data = {
            "directory": directory,
            "timestamp": datetime.now().isoformat(),
            "files": {}
        }

        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_hash = self.calculate_hash(file_path)
                if file_hash:
                    relative_path = os.path.relpath(file_path, directory)
                    self.baseline_data["files"][relative_path] = {
                        "hash": file_hash,
                        "last_checked": datetime.now().isoformat()
                    }

        self.save_baseline()
        print(f"Baseline created for {directory} with {len(self.baseline_data['files'])} files")

    def verify_integrity(self):
        """Verify current files against baseline"""
        if not self.baseline_data:
            print("No baseline data available. Please create a baseline first.")
            return

        directory = self.baseline_data.get("directory")
        if not directory or not os.path.isdir(directory):
            print(f"Error: Baseline directory {directory} is not valid")
            return

        changed_files = []
        new_files = []
        missing_files = []

        baseline_files = self.baseline_data["files"]
        current_files = {}

        # Check all files in the baseline
        for relative_path, file_data in baseline_files.items():
            file_path = os.path.join(directory, relative_path)
            if not os.path.exists(file_path):
                missing_files.append(relative_path)
                continue

            current_hash = self.calculate_hash(file_path)
            if current_hash != file_data["hash"]:
                changed_files.append(relative_path)

        # Check for new files not in baseline
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, directory)
                if relative_path not in baseline_files:
                    new_files.append(relative_path)

        # Print results
        if not (changed_files or new_files or missing_files):
            print("All files match the baseline. No changes detected.")
        else:
            if changed_files:
                print("\nChanged files:")
                for file in changed_files:
                    print(f" - {file}")
            
            if new_files:
                print("\nNew files (not in baseline):")
                for file in new_files:
                    print(f" - {file}")
            
            if missing_files:
                print("\nMissing files (in baseline but not found):")
                for file in missing_files:
                    print(f" - {file}")

        # Update last checked time
        self.baseline_data["last_checked"] = datetime.now().isoformat()
        self.save_baseline()

        return {
            "changed_files": changed_files,
            "new_files": new_files,
            "missing_files": missing_files
        }

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="File Integrity Checker - Monitor changes in files by comparing hash values"
    )
    parser.add_argument(
        "command",
        choices=["create", "verify"],
        help="'create' to make a new baseline, 'verify' to check against baseline"
    )
    parser.add_argument(
        "path",
        help="Directory path to create baseline for or verify against"
    )
    parser.add_argument(
        "--baseline",
        default="baseline.json",
        help="Baseline file name (default: baseline.json)"
    )

    args = parser.parse_args()

    checker = FileIntegrityChecker(args.baseline)

    if args.command == "create":
        checker.create_baseline(args.path)
    elif args.command == "verify":
        checker.verify_integrity()

if __name__ == "__main__":
    main()