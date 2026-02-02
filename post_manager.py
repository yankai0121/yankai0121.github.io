import os
import subprocess
import sys

def run_command(command):
    """Run a shell command and return True if successful."""
    print(f"\n> Running: {command}")
    try:
        # shell=True is often required on Windows for commands like 'hugo' if they are batch files
        result = subprocess.run(command, shell=True, check=False)
        if result.returncode != 0:
            print(f"Command failed with exit code {result.returncode}")
            return False
    except Exception as e:
        print(f"Error running command: {e}")
        return False
    return True

def create_post():
    """Create a new Hugo post."""
    print("\n--- Create New Post ---")
    title = input("Enter post title (e.g., 'My Travel Diary'): ").strip()
    if not title:
        print("Title cannot be empty.")
        return None

    # Create a filename from the title
    # Replace spaces with hyphens, remove special chars, lowercase
    filename = "".join(c if c.isalnum() or c in " -_" else "" for c in title).strip()
    filename = filename.replace(" ", "-").lower() + ".md"
    
    post_path = f"content/posts/{filename}"
    
    command = f"hugo new {post_path}"
    
    if run_command(command):
        print(f"\nPost created successfully at: {post_path}")
        print("Opening file...")
        try:
            # Convert to absolute path to avoid issues with relative paths/slashes
            abs_path = os.path.abspath(post_path)
            if os.path.exists(abs_path):
                os.startfile(abs_path)
            else:
                print(f"File not found: {abs_path}")
        except AttributeError:
            # Fallback for non-Windows systems
            if sys.platform == 'darwin':
                subprocess.call(('open', post_path))
            elif sys.platform.startswith('linux'):
                subprocess.call(('xdg-open', post_path))
        except Exception as e:
            print(f"Could not automatically open file: {e}")
            
        return title
    return None

def deploy(commit_message=None):
    """Build and deploy the site."""
    print("\n--- Deploying to GitHub Pages ---")
    
    # 1. Build the site
    if not run_command("hugo"):
        print("Build failed. Aborting deployment.")
        return

    # 2. Stage changes
    if not run_command("git add ."):
        print("Git add failed. Aborting.")
        return

    # 3. Commit changes
    if not commit_message:
        commit_message = input("Enter commit message (default: 'New post'): ").strip()
        if not commit_message:
            commit_message = "New post"
    
    # Use quotes for the commit message to handle spaces
    if not run_command(f'git commit -m "{commit_message}"'):
        print("Git commit failed (maybe nothing to commit?). Continuing anyway...")

    # 4. Push source to main/master
    if not run_command("git push"):
        print("Git push failed. Aborting.")
        return

    # 5. Push to gh-pages subtree
    print("Pushing subtree to gh-pages... This might take a moment.")
    if not run_command("git subtree push --prefix public origin gh-pages"):
        print("Subtree push failed.")
        return

    print("\nSUCCESS: Site deployed!")

def main():
    while True:
        print("\n=========================")
        print("  Hugo Blog Manager")
        print("=========================")
        print("1. Create new post")
        print("2. Deploy site (Build, Commit, Push)")
        print("3. Create & Deploy")
        print("q. Quit")
        
        choice = input("\nSelect an option: ").strip().lower()

        if choice == '1':
            create_post()
        elif choice == '2':
            deploy()
        elif choice == '3':
            title = create_post()
            if title:
                do_deploy = input(f"\nReady to deploy '{title}'? (y/n): ").strip().lower()
                if do_deploy == 'y':
                    deploy(commit_message=f"New post: {title}")
        elif choice == 'q':
            print("Goodbye!")
            break
        else:
            print("Invalid option, please try again.")

if __name__ == "__main__":
    main()
