import argparse
import sys
from db_manager import DBManager

def main():
    parser = argparse.ArgumentParser(description="Manage Projects for Prompt Similarity Detector")
    parser.add_argument("--name", required=True, help="Project name")
    parser.add_argument("--requirements", help="Project requirements text")
    parser.add_argument("--file", help="Path to a file containing requirements")
    
    args = parser.parse_args()
    
    requirements = args.requirements
    if args.file:
        try:
            with open(args.file, 'r') as f:
                requirements = f.read().strip()
        except Exception as e:
            print(f"Error reading requirements from file: {e}")
            sys.exit(1)
            
    try:
        db = DBManager()
        project_id = db.create_project(args.name, requirements)
        print(f"[+] Project '{args.name.lower()}' created/updated successfully (ID: {project_id}).")
        db.close()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
