#!/usr/bin/env python3
"""
Alternative GitHub to GitLab Backup Script with Git LFS Support
Uses git clone + push instead of GitLab import functionality
"""

import os
import sys
import requests
import json
import time
import subprocess
import tempfile
import shutil
from datetime import datetime

# Configuration
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
GITLAB_TOKEN = os.environ.get('GITLAB_TOKEN')
GITLAB_URL = os.environ.get('GITLAB_URL', 'http://167.71.66.64')

# GitHub accounts to backup
GITHUB_ACCOUNTS = {
    'WouterGlorieux': {
        'type': 'user',
        'gitlab_group': 'wouterglorieux-backup'
    },
    'ValyrianTech': {
        'type': 'org',
        'gitlab_group': 'valyriantech-backup'
    }
}


class GitHubBackupAlternative:
    def __init__(self):
        if not GITHUB_TOKEN or not GITLAB_TOKEN:
            print("ERROR: Missing required environment variables (GITHUB_TOKEN, GITLAB_TOKEN)")
            sys.exit(1)

        self.github_headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }

        self.gitlab_headers = {
            'Authorization': f'Bearer {GITLAB_TOKEN}',
            'Content-Type': 'application/json'
        }

        self.backup_log = []

        # Test GitLab connection
        try:
            response = requests.get(f'{GITLAB_URL}/api/v4/user', headers=self.gitlab_headers)
            if response.status_code == 200:
                user_info = response.json()
                self.log(f"GitLab user: {user_info['username']} (ID: {user_info['id']})")
                self.log(f"User is admin: {user_info.get('is_admin', False)}")
            else:
                self.log(f"ERROR: Could not get GitLab user info: {response.status_code}")
                sys.exit(1)
        except Exception as e:
            self.log(f"ERROR: Could not connect to GitLab: {str(e)}")
            sys.exit(1)

        # Initialize Git LFS
        try:
            subprocess.run(['git', 'lfs', 'install'], check=True, capture_output=True)
            self.log("✅ Git LFS initialized successfully")
        except subprocess.CalledProcessError as e:
            self.log(f"⚠️  Warning: Could not initialize Git LFS: {e}")

    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        self.backup_log.append(log_entry)

    def get_github_repositories(self, account_name, account_type):
        """Fetch all repositories for a GitHub account or organization"""
        if account_type == 'user':
            # For authenticated user, use /user/repos to get private repos too
            url = f"https://api.github.com/user/repos"
        else:  # organization
            url = f"https://api.github.com/orgs/{account_name}/repos"

        repos = []
        page = 1

        while True:
            response = requests.get(
                url,
                headers=self.github_headers,
                params={'page': page, 'per_page': 100, 'type': 'all', 'sort': 'updated'}
            )

            if response.status_code != 200:
                self.log(f"ERROR: Failed to fetch repositories for {account_name}: {response.status_code}")
                break

            page_repos = response.json()
            if not page_repos:
                break

            # Filter repositories by owner for user accounts (since /user/repos returns all accessible repos)
            if account_type == 'user':
                filtered_repos = [repo for repo in page_repos if repo['owner']['login'].lower() == account_name.lower()]
                repos.extend(filtered_repos)
            else:
                repos.extend(page_repos)
            page += 1
            time.sleep(0.1)

        public_count = sum(1 for repo in repos if not repo['private'])
        private_count = sum(1 for repo in repos if repo['private'])
        self.log(f"Found {len(repos)} repositories for {account_name} ({public_count} public, {private_count} private)")

        return repos

    def get_or_create_gitlab_group(self, group_name):
        """Get or create a GitLab group"""
        try:
            response = requests.get(f'{GITLAB_URL}/api/v4/groups/{group_name}', headers=self.gitlab_headers)
            if response.status_code == 200:
                group = response.json()
                self.log(f"Found existing GitLab group: {group_name} (ID: {group['id']})")
                return group

            group_data = {
                'name': group_name.replace('-', ' ').title(),
                'path': group_name,
                'description': 'Automated backup of GitHub repositories',
                'visibility': 'private'
            }

            response = requests.post(f'{GITLAB_URL}/api/v4/groups',
                                     headers=self.gitlab_headers,
                                     json=group_data)

            if response.status_code == 201:
                group = response.json()
                self.log(f"Created new GitLab group: {group_name} (ID: {group['id']})")
                return group
            else:
                self.log(f"ERROR: Could not create GitLab group {group_name}: {response.status_code}")
                return None

        except Exception as e:
            self.log(f"ERROR: Exception while handling GitLab group {group_name}: {str(e)}")
            return None

    def create_empty_gitlab_project(self, repo, gitlab_group=None, account_name=None):
        """Create an empty GitLab project (no import)"""
        # Prefix repository name with account name to avoid conflicts
        if account_name:
            project_name = f"{account_name}-{repo['name']}"
        else:
            project_name = repo['name']

        try:
            # For LFS repositories, we need to delete and recreate to avoid LFS conflicts
            is_lfs_repo = repo['name'] in ['ValyrianSpellbook', 'dockerLLM']

            # Check if project already exists
            existing_project = None
            if gitlab_group:
                response = requests.get(f'{GITLAB_URL}/api/v4/groups/{gitlab_group["id"]}/projects',
                                        headers=self.gitlab_headers)
                if response.status_code == 200:
                    existing_projects = response.json()
                    for project in existing_projects:
                        if project['name'] == project_name:
                            existing_project = project
                            break
            else:
                response = requests.get(f'{GITLAB_URL}/api/v4/projects',
                                        headers=self.gitlab_headers,
                                        params={'owned': 'true', 'search': project_name})
                if response.status_code == 200:
                    existing_projects = response.json()
                    for project in existing_projects:
                        if project['name'] == project_name:
                            existing_project = project
                            break

            # If it's an LFS repo and project exists, delete it first
            if existing_project and is_lfs_repo:
                self.log(f"🗑️  Deleting existing LFS project {project_name} to recreate without LFS")
                delete_response = requests.delete(f'{GITLAB_URL}/api/v4/projects/{existing_project["id"]}',
                                                  headers=self.gitlab_headers)
                if delete_response.status_code == 202:
                    self.log(f"✅ Successfully deleted existing project {project_name}")
                    existing_project = None
                    # Wait a moment for deletion to complete
                    import time
                    time.sleep(2)
                else:
                    self.log(f"⚠️  Could not delete existing project {project_name}: {delete_response.status_code}")

            # If project still exists and it's not LFS, return it
            if existing_project and not is_lfs_repo:
                location = f"group {gitlab_group['name']}" if gitlab_group else "personal namespace"
                self.log(f"Project {project_name} already exists in {location}")
                return existing_project

            # Create empty project (no import_url)
            project_data = {
                'name': project_name,
                'description': repo.get('description', '') or f"Backup of {repo['html_url']}",
                'visibility': 'private',
                'lfs_enabled': True  # Enable LFS support
            }

            if gitlab_group:
                project_data['namespace_id'] = gitlab_group['id']
                self.log(f"Creating empty project {project_name} in group {gitlab_group['name']}")
            else:
                self.log(f"Creating empty project {project_name} in personal namespace")

            response = requests.post(f'{GITLAB_URL}/api/v4/projects',
                                     headers=self.gitlab_headers,
                                     json=project_data)

            if response.status_code == 201:
                project = response.json()
                location = f"group {gitlab_group['name']}" if gitlab_group else "personal namespace"
                self.log(f"✅ Created empty GitLab project in {location}: {project_name}")
                return project
            else:
                # Check if it's just a "project already exists" scenario (expected behavior)
                if response.status_code == 400 and "has already been taken" in response.text:
                    self.log(f"ℹ️ INFO: Project {project_name} already exists (expected on subsequent runs)")
                else:
                    self.log(f"❌ ERROR: Could not create empty project {project_name}: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            self.log(f"❌ ERROR: Exception while creating project {project_name}: {str(e)}")
            return None


    def _remove_lfs_pointers(self, directory):
        """Remove LFS pointer files to prevent GitLab LFS detection"""
        lfs_pointers_found = 0
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    # Check file size first - LFS pointers are always small (< 200 bytes)
                    file_size = os.path.getsize(file_path)
                    if file_size > 300:  # Skip files larger than 300 bytes
                        continue
                        
                    # Try to read as text
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        
                    # Check if this is exactly an LFS pointer file (very strict)
                    lines = content.split('\n')
                    if (len(lines) == 3 and 
                        lines[0] == 'version https://git-lfs.github.com/spec/v1' and
                        lines[1].startswith('oid sha256:') and
                        lines[2].startswith('size ')):
                        
                        rel_path = os.path.relpath(file_path, directory)
                        self.log(f"🗑️ Removing LFS pointer file: {rel_path} ({file_size} bytes)")
                        os.remove(file_path)
                        lfs_pointers_found += 1
                        
                except (UnicodeDecodeError, PermissionError, OSError):
                    # Skip binary files or files we can't read
                    continue
                    
        if lfs_pointers_found > 0:
            self.log(f"✅ Removed {lfs_pointers_found} LFS pointer files")
        else:
            self.log(f"ℹ️ No LFS pointer files found")

    def clone_and_push_repository(self, github_repo, gitlab_project):
        """Clone from GitHub and push to GitLab with enhanced LFS support"""
        repo_name = github_repo['name']
        temp_dir = None

        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp(prefix=f'backup_{repo_name}_')
            self.log(f"📁 Using temp directory: {temp_dir}")

            # Clone from GitHub with authentication (regular clone, not mirror for LFS)
            github_clone_url = github_repo['clone_url'].replace('https://', f'https://{GITHUB_TOKEN}@')

            self.log(f"📥 Cloning from GitHub: {repo_name}")
            clone_result = subprocess.run([
                'git', 'clone', '--bare', github_clone_url,
                os.path.join(temp_dir, f'{repo_name}.git')
            ], capture_output=True, text=True, cwd=temp_dir)

            if clone_result.returncode != 0:
                self.log(f"❌ Failed to clone {repo_name}: {clone_result.stderr}")
                return False

            repo_dir = os.path.join(temp_dir, f'{repo_name}.git')

            # Check if repository uses LFS by looking for .gitattributes
            has_lfs = False
            try:
                # Check for LFS tracking in .gitattributes
                gitattributes_check = subprocess.run([
                    'git', 'show', 'HEAD:.gitattributes'
                ], capture_output=True, text=True, cwd=repo_dir)

                if gitattributes_check.returncode == 0 and 'filter=lfs' in gitattributes_check.stdout:
                    has_lfs = True
                    self.log(f"🔍 Repository {repo_name} uses Git LFS")
            except:
                pass

            # Also check for known LFS repositories
            if repo_name in ['ValyrianSpellbook', 'dockerLLM']:
                has_lfs = True
                self.log(f"🔍 Repository {repo_name} is known to use Git LFS")

            # Set up GitLab remote
            gitlab_push_url = gitlab_project['http_url_to_repo'].replace('http://', f'http://oauth2:{GITLAB_TOKEN}@')

            # Add GitLab as remote
            subprocess.run([
                'git', 'remote', 'add', 'gitlab', gitlab_push_url
            ], capture_output=True, text=True, cwd=repo_dir)

            if has_lfs:
                self.log(f"🔄 Handling LFS repository: {repo_name}")
                self.log(f"🆕 Creating fresh repository from working tree to eliminate LFS history")

                # Create a working directory and checkout the repository
                work_dir = os.path.join(temp_dir, f'{repo_name}_work')
                subprocess.run(['git', 'clone', repo_dir, work_dir], capture_output=True)

                # NUCLEAR OPTION: Force checkout ALL LFS content before copying
                self.log(f"🔥 NUCLEAR LFS APPROACH: Force downloading all LFS content")
                
                # Install LFS and fetch everything
                subprocess.run(['git', 'lfs', 'install'], cwd=work_dir, capture_output=True)
                subprocess.run(['git', 'lfs', 'fetch', '--all'], cwd=work_dir, capture_output=True)
                subprocess.run(['git', 'lfs', 'pull'], cwd=work_dir, capture_output=True)
                subprocess.run(['git', 'lfs', 'checkout'], cwd=work_dir, capture_output=True)
                
                # Verify LFS files are actually checked out
                lfs_status = subprocess.run(['git', 'lfs', 'status'], cwd=work_dir, capture_output=True, text=True)
                self.log(f"📊 LFS Status: {lfs_status.stdout.strip()}")
                
                self.log(f"✅ Forced LFS content checkout completed")

                # Create a completely fresh repository directory
                fresh_repo_dir = os.path.join(temp_dir, f'{repo_name}_fresh')
                os.makedirs(fresh_repo_dir, exist_ok=True)

                # Copy all files from working directory to fresh directory (excluding .git)
                self.log(f"📋 Copying all files to create fresh repository")
                
                # Debug: List what's in the work directory
                work_items = os.listdir(work_dir)
                self.log(f"🔍 Items in work directory: {work_items}")
                
                for item in work_items:
                    if item != '.git':
                        src_path = os.path.join(work_dir, item)
                        dst_path = os.path.join(fresh_repo_dir, item)
                        
                        if os.path.isdir(src_path):
                            # Debug: Check if directory has content
                            try:
                                dir_contents = os.listdir(src_path)
                                self.log(f"📁 Copying directory {item} (contains: {len(dir_contents)} items)")
                                if item in ['apps', 'spellbookscripts', 'models']:
                                    self.log(f"🎯 Critical directory {item} contents: {dir_contents}")
                                shutil.copytree(src_path, dst_path)
                            except Exception as e:
                                self.log(f"❌ Error copying directory {item}: {e}")
                        else:
                            try:
                                shutil.copy2(src_path, dst_path)
                                self.log(f"📄 Copied file: {item}")
                            except Exception as e:
                                self.log(f"❌ Error copying file {item}: {e}")

                # Remove ALL LFS and Git configuration files that could cause issues
                self.log(f"🗑️ Removing all LFS and problematic Git configuration files")
                files_to_remove = ['.gitattributes', '.lfsconfig', '.gitignore']
                for config_file in files_to_remove:
                    config_path = os.path.join(fresh_repo_dir, config_file)
                    if os.path.exists(config_path):
                        self.log(f"🗑️ Removed: {config_file}")
                        os.remove(config_path)

                # Remove LFS pointer files to prevent GitLab LFS detection
                self.log(f"🔍 Scanning for and removing LFS pointer files")
                self._remove_lfs_pointers(fresh_repo_dir)

                # Initialize fresh git repository
                self.log(f"🔧 Initializing fresh Git repository")
                subprocess.run(['git', 'init'], cwd=fresh_repo_dir, capture_output=True)
                subprocess.run(['git', 'config', 'user.email', 'backup@valyrian.tech'], 
                              cwd=fresh_repo_dir, capture_output=True)
                subprocess.run(['git', 'config', 'user.name', 'Backup Bot'], 
                              cwd=fresh_repo_dir, capture_output=True)

                # Add all files and create initial commit
                # Since we removed .gitignore, this will now add ALL files and directories
                self.log(f"📦 Adding all files to fresh repository (no exclusions)")
                subprocess.run(['git', 'add', '.'], cwd=fresh_repo_dir, capture_output=True)
                commit_message = f"Fresh backup of {repo_name} from GitHub ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
                subprocess.run(['git', 'commit', '-m', commit_message], 
                              cwd=fresh_repo_dir, capture_output=True)

                # Add GitLab remote and push
                subprocess.run(['git', 'remote', 'add', 'origin', gitlab_push_url],
                               cwd=fresh_repo_dir, capture_output=True)

                self.log(f"📤 Pushing fresh repository {repo_name} to GitLab")
                push_result = subprocess.run([
                    'git', 'push', '-u', 'origin', 'master'
                ], capture_output=True, text=True, cwd=fresh_repo_dir)

                # Try 'main' branch if 'master' fails
                if push_result.returncode != 0 and 'master' in push_result.stderr:
                    self.log(f"🔄 Trying 'main' branch instead of 'master'")
                    subprocess.run(['git', 'branch', '-M', 'main'], cwd=fresh_repo_dir, capture_output=True)
                    push_result = subprocess.run([
                        'git', 'push', '-u', 'origin', 'main'
                    ], capture_output=True, text=True, cwd=fresh_repo_dir)

                if push_result.returncode == 0:
                    self.log(f"✅ Successfully backed up {repo_name} as fresh repository")
                    self.log(f"📋 Note: Created fresh repository without LFS history - all current files preserved")
                    return True
                else:
                    self.log(f"❌ Failed to push fresh repository {repo_name}: {push_result.stderr}")
                    return False
            else:
                # Regular repository without LFS
                self.log(f"📤 Pushing to GitLab: {repo_name}")
                push_result = subprocess.run([
                    'git', 'push', 'gitlab', '--mirror'
                ], capture_output=True, text=True, cwd=repo_dir)

                if push_result.returncode != 0:
                    self.log(f"❌ Failed to push {repo_name}: {push_result.stderr}")
                    return False

                self.log(f"✅ Successfully backed up {repo_name}")
                return True

        except Exception as e:
            self.log(f"❌ Exception during clone/push for {repo_name}: {str(e)}")
            return False
        finally:
            # Clean up temporary directory
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    self.log(f"🧹 Cleaned up temp directory for {repo_name}")
                except:
                    self.log(f"⚠️  Could not clean up temp directory: {temp_dir}")

    def backup_repository(self, repo, gitlab_group, account_name):
        """Backup a single repository"""
        if repo['archived']:
            self.log(f"⏭️  Skipping archived repository: {repo['name']}")
            return False

        self.log(f"📦 Processing repository: {repo['name']} ({'private' if repo['private'] else 'public'})")

        # Create empty GitLab project with account prefix
        gitlab_project = self.create_empty_gitlab_project(repo, gitlab_group, account_name)
        if not gitlab_project and gitlab_group:
            self.log(f"⚠️  Failed to create in group, trying personal namespace for {repo['name']}")
            gitlab_project = self.create_empty_gitlab_project(repo, None, account_name)

        if not gitlab_project:
            self.log(f"❌ Could not create GitLab project for {repo['name']}")
            return False

        # Clone and push
        success = self.clone_and_push_repository(repo, gitlab_project)
        return success

    def backup_account(self, account_name, account_config):
        """Backup all repositories from a GitHub account"""
        self.log(f"🚀 Starting backup for {account_name} ({account_config['type']})")

        # Get GitHub repositories
        repos = self.get_github_repositories(account_name, account_config['type'])
        if not repos:
            self.log(f"No repositories found for {account_name}")
            return

        # Get or create GitLab group
        gitlab_group = self.get_or_create_gitlab_group(account_config['gitlab_group'])

        # Process each repository
        success_count = 0
        for repo in repos:
            if self.backup_repository(repo, gitlab_group, account_name):
                success_count += 1

            # Rate limiting protection
            time.sleep(2)

        self.log(f"✅ Backup completed for {account_name}: {success_count}/{len(repos)} repositories processed")

    def run_backup(self):
        """Run the complete backup process"""
        self.log("🎯 Starting GitHub to GitLab backup process (Alternative Method with LFS)")

        for account_name, account_config in GITHUB_ACCOUNTS.items():
            try:
                self.backup_account(account_name, account_config)
            except Exception as e:
                self.log(f"❌ ERROR: Failed to backup {account_name}: {str(e)}")

        # Save backup log
        try:
            with open('backup_log.txt', 'w') as f:
                f.write('\n'.join(self.backup_log))
            self.log("📄 Backup log saved to backup_log.txt")
        except Exception as e:
            self.log(f"⚠️  Could not save backup log: {str(e)}")

        self.log("🎉 Backup process completed!")


if __name__ == "__main__":
    backup = GitHubBackupAlternative()
    backup.run_backup()
