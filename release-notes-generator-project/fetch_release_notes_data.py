import os
import yaml
import requests

# Constants
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_REPO = 'trilogy-group/Lithium-RELEASE'  # Example: 'octocat/Hello-World'
API_URL = 'https://api.github.com'

def fetch_prs_between_tags(start_tag, end_tag):
    url = f"{API_URL}/repos/{GITHUB_REPO}/compare/{start_tag}...{end_tag}"
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(url, headers=headers)
    prs = []

    if response.status_code == 200:
        commits = response.json().get('commits', [])
        for commit in commits:
            commit_prs = fetch_prs_from_commit(commit['sha'])
            prs.extend(commit_prs)

    return prs

def fetch_prs_from_commit(commit_sha):
    url = f"{API_URL}/repos/{GITHUB_REPO}/commits/{commit_sha}/pulls"
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.groot-preview+json'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return [pr['number'] for pr in response.json()]
    return []

def fetch_pr_details(pr_number):
    url = f"{API_URL}/repos/{GITHUB_REPO}/pulls/{pr_number}"
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(url, headers=headers)
    pr_details = {}

    if response.status_code == 200:
        pr_data = response.json()
        pr_details['title'] = pr_data.get('title')
        pr_details['body'] = pr_data.get('body')
        pr_details['commits_url'] = pr_data.get('commits_url')
        pr_details['diff'] = fetch_pr_diff(pr_number)

        return pr_details
    else:
        return None

def fetch_pr_diff(pr_number):
    url = f"{API_URL}/repos/{GITHUB_REPO}/pulls/{pr_number}"
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3.diff'  # Request the diff format
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        return None

def fetch_release_notes_data(start_tag, end_tag):
    pr_numbers = fetch_prs_between_tags(start_tag, end_tag)
    release_notes_data = []

    for pr_number in pr_numbers:
        pr_details = fetch_pr_details(pr_number)
        if pr_details:
            release_notes_data.append({
                'PR Number': pr_number,
                'Title': pr_details.get('title'),
                'Body': pr_details.get('body'),
                'Commits URL': pr_details.get('commits_url'),
                'Diff': pr_details.get('diff'),
                # You can fetch commits separately if necessary
            })
    return release_notes_data

