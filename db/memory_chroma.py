import os
import requests
import base64
from dotenv import load_dotenv

# Load GitHub token securely from .env
load_dotenv()
GITHUB_TOKEN = os.getenv('CHERRY_GH_TOKEN')
REPO_OWNER = 'ai-cherry'
REPO_NAME = 'cherry'

# Validate GitHub token immediately
if not GITHUB_TOKEN:
    raise EnvironmentError('GitHub token (CHERRY_GH_TOKEN) not found. Check your .env file.')

# GitHub API headers
headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}


def create_branch(new_branch, source_branch='main'):
    print(f'Creating branch "{new_branch}" from "{source_branch}".')

    source_branch_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/refs/heads/{source_branch}'
    response = requests.get(source_branch_url, headers=headers)

    if response.status_code == 404:
        raise ValueError(f'Source branch "{source_branch}" not found.')
    elif not response.ok:
        raise RuntimeError(f'Failed to retrieve source branch: {response.json()}')

    sha = response.json()['object']['sha']

    create_branch_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/refs'
    response = requests.post(create_branch_url, json={
        'ref': f'refs/heads/{new_branch}',
        'sha': sha
    }, headers=headers)

    if response.status_code != 201:
        raise RuntimeError(f'Error creating branch: {response.json()}')

    print(f'Branch "{new_branch}" created successfully.')


def commit_file(branch_name, file_path, file_content, commit_message='Automated commit via ChatGPT plugin'):
    file_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_path}'
    response = requests.get(file_url, params={'ref': branch_name}, headers=headers)

    sha = response.json().get('sha') if response.ok else None

    encoded_content = base64.b64encode(file_content.encode('utf-8')).decode('utf-8')

    data = {
        'message': commit_message,
        'content': encoded_content,
        'branch': branch_name
    }

    if sha:
        data['sha'] = sha

    response = requests.put(file_url, headers=headers, json=data)

    if response.status_code not in [200, 201]:
        raise RuntimeError(f'Error committing file: {response.json()}')

    print(f'File "{file_path}" committed successfully to branch "{branch_name}".')


if __name__ == '__main__':
    test_branch = 'feature/chatgpt-plugin'
    create_branch(test_branch)
    commit_file(
        branch_name=test_branch,
        file_path='scripts/example.py',
        file_content='print("Hello, GitHub via ChatGPT!")'
    )
