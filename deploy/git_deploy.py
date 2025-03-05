import subprocess
import sys


def git_deploy():
    try:
        # Stage all changes
        subprocess.run(["git", "add", "."], check=True)
        # Commit changes with an automated message
        subprocess.run(
            ["git", "commit", "-m", "Automated commit and deploy"], check=True)
        # Push to the default remote branch
        subprocess.run(["git", "push"], check=True)
        print("Code pushed successfully and GitHub deployment triggered.")
    except subprocess.CalledProcessError as e:
        print(f"Error during git push: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    git_deploy()
