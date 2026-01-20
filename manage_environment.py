import argparse
import sys
from db_manager import DBManager

def main():
    parser = argparse.ArgumentParser(description="Manage Environments for Prompt Similarity Detector")
    parser.add_argument("--project", required=True, help="Parent project name")
    parser.add_argument("--name", required=True, help="Environment name")
    
    args = parser.parse_args()
    
    try:
        db = DBManager()
        env_id = db.create_environment(args.project, args.name)
        print(f"[+] Environment '{args.name.lower()}' created/found for project '{args.project.lower()}' (ID: {env_id}).")
        db.close()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
