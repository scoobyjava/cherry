import os
import requests
import base64
from dotenv import load_dotenv

# Load GitHub token from .env
load_dotenv()
GITHUB_TOKEN = os.getenv('CHERRY_GH_TOKEN')
REPO_OWNER = 'scoobyjava'
REPO_NAME = 'ai-cherry'

headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

def create_branch(new_branch, source_branch='main'):
    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/ref/heads/{source_branch}'
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f'Error fetching source branch: {response.json()}')

    sha = response.json()['object']['sha']

    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/refs'
    response = requests.post(url, json={
        'ref': f'refs/heads/{new_branch}',
        'sha': sha
    }, headers=headers)

    if response.status_code != 201:
        raise Exception(f'Error creating branch: {response.json()}')

    print(f'Branch {new_branch} created successfully.')

def commit_file(branch_name, file_path, file_content, commit_message='Automated commit via ChatGPT plugin'):
    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_path}'

    response = requests.get(url, headers=headers)
    sha = response.json().get('sha') if response.status_code == 200 else None

    encoded_content = base64.b64encode(file_content.encode()).decode()

    data = {
        'message': commit_message,
        'content': encoded_content,
        'branch': branch_name
    }

    if sha:
        data['sha'] = sha

    response = requests.put(url, headers=headers, json=data)

    if response.status_code not in [200, 201]:
        raise Exception(f'Error committing file: {response.json()}')

    print(f'File {file_path} committed successfully on branch {branch_name}.')

if __name__ == '__main__':
    new_branch = 'feature/chatgpt-plugin'
    create_branch(new_branch)
    commit_file(
        branch_name=new_branch,
        file_path='scripts/example.py',
        file_content='print("Hello, GitHub via ChatGPT!")'
    )
