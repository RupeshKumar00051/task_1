#Company : CODTECH IT SOLUTIONS
#NAME : RUPESH KUMAR
#INTERN ID : CT04DA417
#Domain : Cyber Security & Ethical Hacking 
#Duration : 4 weeks
Mentor: Neela Santosh

# task_1
# File Integrity Checker

A Python tool to monitor changes in files by calculating and comparing hash values.

## Features

- Creates a baseline snapshot of file hashes (SHA-256)
- Detects changed, new, and missing files
- Saves baseline to JSON file for future comparisons
- Works recursively through directories

## Requirements

- Python 3.x
- No additional dependencies (uses standard libraries)

## Usage

1. Create a baseline:
   ```bash
   python file_integrity_checker.py create /path/to/directory
