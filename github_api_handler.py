import json
import urllib3
import base64
import os
from urllib.parse import quote
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_available_tools():
    """Return all available GitHub tools in Bedrock-compatible format"""
    return {
        "success": True,
        "service": "github",
        "tools": [
            {
                "name": "create_or_update_github_file",
                "description": "Creates a new file or updates an existing file in a GitHub repository. This commits the changes directly to the specified branch.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "Must be 'create_or_update_file'"
                        },
                        "owner": {
                            "type": "string",
                            "description": "The GitHub username or organization name"
                        },
                        "repo": {
                            "type": "string",
                            "description": "The repository name"
                        },
                        "path": {
                            "type": "string",
                            "description": "The file path (e.g., 'src/main.py')"
                        },
                        "content": {
                            "type": "string",
                            "description": "The complete file content (not base64 encoded)"
                        },
                        "message": {
                            "type": "string",
                            "description": "Commit message. Defaults to 'Update file via API'"
                        },
                        "branch": {
                            "type": "string",
                            "description": "Target branch name. Defaults to 'main'"
                        },
                        "sha": {
                            "type": "string",
                            "description": "The blob SHA of the file being replaced (required for updates, omit for new files)"
                        }
                    },
                    "required": ["action", "owner", "repo", "path", "content"]
                }
            },
            {
                "name": "create_github_branch",
                "description": "Creates a new branch in a GitHub repository from an existing branch.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "Must be 'create_branch'"
                        },
                        "owner": {
                            "type": "string",
                            "description": "The GitHub username or organization name"
                        },
                        "repo": {
                            "type": "string",
                            "description": "The repository name"
                        },
                        "branch": {
                            "type": "string",
                            "description": "The name for the new branch"
                        },
                        "from_branch": {
                            "type": "string",
                            "description": "The source branch to create from. Defaults to 'main'"
                        }
                    },
                    "required": ["action", "owner", "repo", "branch"]
                }
            },
            {
                "name": "get_github_file",
                "description": "Retrieves the contents of a specific file from a GitHub repository. Use this to read code, documentation, configuration files, or any text-based file from a repository.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "Must be 'get_file'"
                        },
                        "owner": {
                            "type": "string",
                            "description": "The GitHub username or organization name that owns the repository"
                        },
                        "repo": {
                            "type": "string",
                            "description": "The name of the repository"
                        },
                        "path": {
                            "type": "string",
                            "description": "The file path within the repository (e.g., 'src/main.py', 'README.md', 'config/settings.json')"
                        },
                        "branch": {
                            "type": "string",
                            "description": "The branch name to read from. Defaults to 'main' if not specified"
                        }
                    },
                    "required": ["action", "owner", "repo", "path"]
                }
            },
            {
                "name": "list_github_repos",
                "description": "Lists all repositories for a GitHub user or organization. Use this to discover what repositories are available before performing other operations.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "Must be 'list_repos'"
                        },
                        "owner": {
                            "type": "string",
                            "description": "The GitHub username or organization name"
                        },
                        "type": {
                            "type": "string",
                            "description": "Filter repositories by type: 'all' (default), 'owner', or 'member'"
                        }
                    },
                    "required": ["action", "owner"]
                }
            },
            {
                "name": "create_github_pull_request",
                "description": "Creates a new pull request in a GitHub repository. The source branch (head) must already exist and contain commits that differ from the target branch (base).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "Must be 'create_pull_request'"
                        },
                        "owner": {
                            "type": "string",
                            "description": "The GitHub username or organization name that owns the repository"
                        },
                        "repo": {
                            "type": "string",
                            "description": "The name of the repository"
                        },
                        "title": {
                            "type": "string",
                            "description": "The title of the pull request"
                        },
                        "head": {
                            "type": "string",
                            "description": "The name of the branch where your changes are implemented (source branch)"
                        },
                        "base": {
                            "type": "string",
                            "description": "The name of the branch you want to merge changes into (target branch). Defaults to 'main' if not specified"
                        },
                        "body": {
                            "type": "string",
                            "description": "The description/body text of the pull request explaining the changes"
                        }
                    },
                    "required": ["action", "owner", "repo", "title", "head"]
                }
            },
            {
                "name": "list_github_pull_requests",
                "description": "Lists pull requests in a GitHub repository. Can filter by state to show open, closed, or all pull requests.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "Must be 'list_pull_requests'"
                        },
                        "owner": {
                            "type": "string",
                            "description": "The GitHub username or organization name that owns the repository"
                        },
                        "repo": {
                            "type": "string",
                            "description": "The name of the repository"
                        },
                        "state": {
                            "type": "string",
                            "description": "Filter by PR state: 'open' (default), 'closed', or 'all'"
                        }
                    },
                    "required": ["action", "owner", "repo"]
                }
            },
            {
                "name": "list_github_branches",
                "description": "Lists branches in a GitHub repository. Can filter by protected status and supports pagination.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "Must be 'list_branches'"
                        },
                        "owner": {
                            "type": "string",
                            "description": "The GitHub username or organization name that owns the repository"
                        },
                        "repo": {
                            "type": "string",
                            "description": "The name of the repository"
                        },
                        "protected": {
                            "type": "boolean",
                            "description": "Optional: If provided, filters branches by protected status"
                        },
                        "per_page": {
                            "type": "integer",
                            "description": "Results per page (max 100). Defaults to 100"
                        },
                        "page": {
                            "type": "integer",
                            "description": "Page number for pagination. Defaults to 1"
                        }
                    },
                    "required": ["action", "owner", "repo"]
                }
            },
            {
                "name": "commit_github_file",
                "description": "Commits a single file change to a specified branch. If the branch does not exist, it can be created from a base branch.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "Must be 'commit_file'"},
                        "owner": {"type": "string", "description": "The GitHub username or organization name"},
                        "repo": {"type": "string", "description": "The repository name"},
                        "path": {"type": "string", "description": "The file path to commit (e.g., 'src/main.py')"},
                        "content": {"type": "string", "description": "The complete file content (UTF-8)"},
                        "message": {"type": "string", "description": "Commit message"},
                        "branch": {"type": "string", "description": "Target branch name"},
                        "from_branch": {"type": "string", "description": "If target branch doesn't exist, create it from this base branch (default 'main')"}
                    },
                    "required": ["action", "owner", "repo", "path", "content", "message", "branch"]
                }
            },
            {
                "name": "open_github_pull_request_from_changes",
                "description": "Creates a new branch from a base branch, commits multiple file changes in a single commit, and opens a pull request.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "Must be 'open_pr_from_changes'"},
                        "owner": {"type": "string", "description": "The GitHub username or organization name"},
                        "repo": {"type": "string", "description": "The repository name"},
                        "title": {"type": "string", "description": "PR title"},
                        "base": {"type": "string", "description": "Base branch to create from and target for PR (default 'main')"},
                        "branch": {"type": "string", "description": "New branch name to create; if omitted, a name will be generated"},
                        "body": {"type": "string", "description": "PR description/body"},
                        "commit_message": {"type": "string", "description": "Commit message for the changes (default 'Apply changes via API')"},
                        "files": {
                            "type": "array",
                            "description": "List of files to commit",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "path": {"type": "string", "description": "File path"},
                                    "content": {"type": "string", "description": "File content (UTF-8)"}
                                },
                                "required": ["path", "content"]
                            }
                        }
                    },
                    "required": ["action", "owner", "repo", "title", "files"]
                }
            },
            {
                "name": "search_github_code",
                "description": "Searches for code across GitHub repositories using GitHub's code search syntax. Supports filters like language, filename, path, user, and repo. Note: Only searches indexed repositories (may take 30+ minutes for new repos to be indexed).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "Must be 'search_code'"
                        },
                        "query": {
                            "type": "string",
                            "description": "GitHub code search query. Examples: 'function language:python', 'user:username', 'repo:owner/repo', 'class User language:java', 'import React filename:App.js'"
                        },
                        "repo": {
                            "type": "string",
                            "description": "Optional: Limit search to a specific repository in format 'owner/repo'"
                        }
                    },
                    "required": ["action", "query"]
                }
            }
        ]
    }

def create_or_update_file(http, headers, body):
    """Create or update a file in GitHub repository"""
    try:
        owner = body.get('owner')
        repo = body.get('repo')
        path = body.get('path')
        content = body.get('content')
        message = body.get('message', 'Update file via API')
        branch = body.get('branch', 'main')
        sha = body.get('sha')  # Required for updates, optional for creates
        
        if not all([owner, repo, path, content]):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'message': 'owner, repo, path, and content are required'
                })
            }
        
        # Encode content to base64
        content_bytes = content.encode('utf-8')
        content_base64 = base64.b64encode(content_bytes).decode('utf-8')
        
        # Prepare request data
        file_data = {
            "message": message,
            "content": content_base64,
            "branch": branch
        }
        
        # Add SHA if provided (for updates)
        if sha:
            file_data["sha"] = sha
        
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        response = http.request(
            'PUT',
            url,
            headers=headers,
            body=json.dumps(file_data)
        )
        
        if response.status in [200, 201]:
            data = json.loads(response.data.decode('utf-8'))
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'success': True,
                    'message': 'File created/updated successfully',
                    'path': path,
                    'sha': data['content']['sha'],
                    'url': data['content']['html_url'],
                    'commit': {
                        'sha': data['commit']['sha'],
                        'url': data['commit']['html_url']
                    }
                })
            }
        else:
            error_data = response.data.decode('utf-8')
            return {
                'statusCode': response.status,
                'body': json.dumps({
                    'success': False,
                    'message': f'Failed to create/update file: {response.status}',
                    'details': error_data
                })
            }
    
    except Exception as e:
        import traceback
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False, 
                'message': f'Error: {str(e)}',
                'traceback': traceback.format_exc()
            })
        }

def create_branch(http, headers, body):
    """Create a new branch from an existing branch"""
    try:
        owner = body.get('owner')
        repo = body.get('repo')
        branch = body.get('branch')
        from_branch = body.get('from_branch', 'main')
        
        if not all([owner, repo, branch]):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'message': 'owner, repo, and branch are required'
                })
            }
        
        # Step 1: Get the SHA of the source branch
        ref_url = f"https://api.github.com/repos/{owner}/{repo}/git/refs/heads/{from_branch}"
        ref_response = http.request('GET', ref_url, headers=headers)
        
        if ref_response.status != 200:
            return {
                'statusCode': ref_response.status,
                'body': json.dumps({
                    'success': False,
                    'message': f'Failed to get source branch: {from_branch}',
                    'details': ref_response.data.decode('utf-8')
                })
            }
        
        ref_data = json.loads(ref_response.data.decode('utf-8'))
        sha = ref_data['object']['sha']
        
        # Step 2: Create new branch
        create_data = {
            "ref": f"refs/heads/{branch}",
            "sha": sha
        }
        
        create_url = f"https://api.github.com/repos/{owner}/{repo}/git/refs"
        create_response = http.request(
            'POST',
            create_url,
            headers=headers,
            body=json.dumps(create_data)
        )
        
        if create_response.status in [200, 201]:
            data = json.loads(create_response.data.decode('utf-8'))
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'success': True,
                    'message': f'Branch {branch} created successfully',
                    'branch': branch,
                    'sha': data['object']['sha'],
                    'ref': data['ref']
                })
            }
        else:
            error_data = create_response.data.decode('utf-8')
            return {
                'statusCode': create_response.status,
                'body': json.dumps({
                    'success': False,
                    'message': f'Failed to create branch: {create_response.status}',
                    'details': error_data
                })
            }
    
    except Exception as e:
        import traceback
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False, 
                'message': f'Error: {str(e)}',
                'traceback': traceback.format_exc()
            })
        }

def get_file(http, headers, body):
    """Get file contents from GitHub repository"""
    try:
        owner = body.get('owner')
        repo = body.get('repo')
        path = body.get('path')
        branch = body.get('branch', 'main')
        
        if not all([owner, repo, path]):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'message': 'owner, repo, and path are required'
                })
            }
        
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"
        response = http.request('GET', url, headers=headers)
        
        if response.status == 200:
            data = json.loads(response.data.decode('utf-8'))
            
            # Decode base64 content
            if data.get('encoding') == 'base64':
                content = base64.b64decode(data['content']).decode('utf-8')
            else:
                content = data.get('content', '')
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'success': True,
                    'path': path,
                    'content': content,
                    'sha': data.get('sha'),
                    'size': data.get('size'),
                    'url': data.get('html_url')
                })
            }
        elif response.status == 404:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'success': False,
                    'message': f'File not found: {path} in {owner}/{repo} (branch: {branch})'
                })
            }
        else:
            error_data = response.data.decode('utf-8')
            return {
                'statusCode': response.status,
                'body': json.dumps({
                    'success': False,
                    'message': f'Failed to get file: {response.status}',
                    'details': error_data
                })
            }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'success': False, 'message': f'Error: {str(e)}'})
        }

def create_pull_request(http, headers, body):
    """Create a pull request"""
    try:
        owner = body.get('owner')
        repo = body.get('repo')
        title = body.get('title')
        head = body.get('head')
        base = body.get('base', 'main')
        pr_body = body.get('body', '')
        
        if not all([owner, repo, title, head]):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'message': 'owner, repo, title, and head are required'
                })
            }
        
        pr_data = {
            "title": title,
            "head": head,
            "base": base,
            "body": pr_body
        }
        
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        response = http.request(
            'POST',
            url,
            headers=headers,
            body=json.dumps(pr_data)
        )
        
        if response.status in [200, 201]:
            data = json.loads(response.data.decode('utf-8'))
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'success': True,
                    'pr_number': data.get('number'),
                    'pr_url': data.get('html_url'),
                    'state': data.get('state'),
                    'created_at': data.get('created_at')
                })
            }
        else:
            error_data = response.data.decode('utf-8')
            return {
                'statusCode': response.status,
                'body': json.dumps({
                    'success': False,
                    'message': f'Failed to create PR: {response.status}',
                    'details': error_data
                })
            }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'success': False, 'message': f'Error: {str(e)}'})
        }

def list_pull_requests(http, headers, body):
    """List pull requests"""
    try:
        owner = body.get('owner')
        repo = body.get('repo')
        state = body.get('state', 'open')
        
        if not all([owner, repo]):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'message': 'owner and repo are required'
                })
            }
        
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state={state}"
        response = http.request('GET', url, headers=headers)
        
        if response.status == 200:
            prs = json.loads(response.data.decode('utf-8'))
            pr_list = [
                {
                    'number': pr['number'],
                    'title': pr['title'],
                    'state': pr['state'],
                    'url': pr['html_url'],
                    'created_at': pr['created_at'],
                    'user': pr['user']['login']
                }
                for pr in prs
            ]
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'success': True,
                    'count': len(pr_list),
                    'pull_requests': pr_list
                })
            }
        else:
            error_data = response.data.decode('utf-8')
            return {
                'statusCode': response.status,
                'body': json.dumps({
                    'success': False,
                    'message': f'Failed to list PRs: {response.status}',
                    'details': error_data
                })
            }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'success': False, 'message': f'Error: {str(e)}'})
        }

def list_branches(http, headers, body):
    """List branches for a repository"""
    try:
        owner = body.get('owner')
        repo = body.get('repo')
        per_page = int(body.get('per_page', 100))
        page = int(body.get('page', 1))
        protected_filter = body.get('protected', None)

        if not all([owner, repo]):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'message': 'owner and repo are required'
                })
            }

        # Build query parameters
        params = [f"per_page={per_page}", f"page={page}"]
        if protected_filter is not None:
            prot_val = 'true' if str(protected_filter).lower() in ['1', 'true', 'yes'] else 'false'
            params.append(f"protected={prot_val}")

        query = "&".join(params)
        url = f"https://api.github.com/repos/{owner}/{repo}/branches?{query}"

        response = http.request('GET', url, headers=headers)

        if response.status == 200:
            branches = json.loads(response.data.decode('utf-8'))
            branch_list = [
                {
                    'name': br.get('name'),
                    'commit_sha': br.get('commit', {}).get('sha'),
                    'commit_api_url': br.get('commit', {}).get('url'),
                    'protected': br.get('protected', False)
                }
                for br in branches
            ]

            return {
                'statusCode': 200,
                'body': json.dumps({
                    'success': True,
                    'count': len(branch_list),
                    'branches': branch_list,
                    'pagination': {
                        'per_page': per_page,
                        'page': page
                    }
                })
            }
        else:
            error_data = response.data.decode('utf-8')
            return {
                'statusCode': response.status,
                'body': json.dumps({
                    'success': False,
                    'message': f'Failed to list branches: {response.status}',
                    'details': error_data
                })
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'success': False, 'message': f'Error: {str(e)}'})
        }

def search_code(http, headers, body):
    """Search code in GitHub"""
    try:
        query = body.get('query')
        
        if not query:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'message': 'query is required'
                })
            }
        
        # Add repo filter if provided
        if body.get('repo'):
            query += f" repo:{body['repo']}"
        
        # URL encode the query
        encoded_query = quote(query)
        url = f"https://api.github.com/search/code?q={encoded_query}"
        response = http.request('GET', url, headers=headers)
        
        if response.status == 200:
            data = json.loads(response.data.decode('utf-8'))
            results = [
                {
                    'path': item['path'],
                    'repository': item['repository']['full_name'],
                    'url': item['html_url']
                }
                for item in data.get('items', [])
            ]
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'success': True,
                    'total_count': data.get('total_count', 0),
                    'results': results[:10]
                })
            }
        else:
            error_data = response.data.decode('utf-8')
            return {
                'statusCode': response.status,
                'body': json.dumps({
                    'success': False,
                    'message': f'Search failed: {response.status}',
                    'details': error_data
                })
            }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'success': False, 'message': f'Error: {str(e)}'})
        }

def list_repos(http, headers, body):
    """List repositories for a user or organization"""
    try:
        owner = body.get('owner')
        repo_type = body.get('type', 'all')  # all, owner, member
        
        if not owner:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'message': 'owner is required'
                })
            }
        
        url = f"https://api.github.com/users/{owner}/repos?type={repo_type}&sort=updated&per_page=30"
        response = http.request('GET', url, headers=headers)
        
        if response.status == 200:
            repos = json.loads(response.data.decode('utf-8'))
            repo_list = [
                {
                    'name': repo['name'],
                    'full_name': repo['full_name'],
                    'description': repo['description'],
                    'url': repo['html_url'],
                    'private': repo['private'],
                    'updated_at': repo['updated_at']
                }
                for repo in repos
            ]
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'success': True,
                    'count': len(repo_list),
                    'repositories': repo_list
                })
            }
        else:
            error_data = response.data.decode('utf-8')
            return {
                'statusCode': response.status,
                'body': json.dumps({
                    'success': False,
                    'message': f'Failed to list repos: {response.status}',
                    'details': error_data
                })
            }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'success': False, 'message': f'Error: {str(e)}'})
        }

# Helper functions for Git Data API workflows
def _get_ref_sha(http, headers, owner, repo, branch):
    url = f"https://api.github.com/repos/{owner}/{repo}/git/refs/heads/{branch}"
    resp = http.request('GET', url, headers=headers)
    if resp.status == 200:
        data = json.loads(resp.data.decode('utf-8'))
        return data['object']['sha'], None
    return None, resp

def _create_branch_from(http, headers, owner, repo, new_branch, from_sha):
    create_url = f"https://api.github.com/repos/{owner}/{repo}/git/refs"
    payload = {"ref": f"refs/heads/{new_branch}", "sha": from_sha}
    return http.request('POST', create_url, headers=headers, body=json.dumps(payload))

def _get_commit_and_tree(http, headers, owner, repo, commit_sha):
    url = f"https://api.github.com/repos/{owner}/{repo}/git/commits/{commit_sha}"
    resp = http.request('GET', url, headers=headers)
    if resp.status != 200:
        return None, None, resp
    data = json.loads(resp.data.decode('utf-8'))
    return data.get('sha'), data.get('tree', {}).get('sha'), None

def _create_blob(http, headers, owner, repo, content):
    url = f"https://api.github.com/repos/{owner}/{repo}/git/blobs"
    payload = {"content": content, "encoding": "utf-8"}
    return http.request('POST', url, headers=headers, body=json.dumps(payload))

def _create_tree(http, headers, owner, repo, base_tree_sha, tree_entries):
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees"
    payload = {"base_tree": base_tree_sha, "tree": tree_entries}
    return http.request('POST', url, headers=headers, body=json.dumps(payload))

def _create_commit(http, headers, owner, repo, message, tree_sha, parent_sha):
    url = f"https://api.github.com/repos/{owner}/{repo}/git/commits"
    payload = {"message": message, "tree": tree_sha, "parents": [parent_sha]}
    return http.request('POST', url, headers=headers, body=json.dumps(payload))

def _update_branch_ref(http, headers, owner, repo, branch, commit_sha):
    url = f"https://api.github.com/repos/{owner}/{repo}/git/refs/heads/{branch}"
    payload = {"sha": commit_sha, "force": False}
    return http.request('PATCH', url, headers=headers, body=json.dumps(payload))

def _ensure_branch_and_get_base(http, headers, owner, repo, branch, from_branch='main'):
    # Try target branch
    branch_sha, resp = _get_ref_sha(http, headers, owner, repo, branch)
    if branch_sha:
        return branch_sha, branch, None

    if resp and resp.status != 404:
        return None, None, resp  # Unexpected error

    # If not exists, get base branch sha
    base_sha, base_resp = _get_ref_sha(http, headers, owner, repo, from_branch)
    if not base_sha:
        return None, None, base_resp

    # Create new branch from base_sha
    create_resp = _create_branch_from(http, headers, owner, repo, branch, base_sha)
    if create_resp.status not in [200, 201]:
        return None, None, create_resp

    # Confirm new branch head sha
    new_sha, _ = _get_ref_sha(http, headers, owner, repo, branch)
    return new_sha, branch, None

def commit_file(http, headers, body):
    """Commit a single file change to a branch (creates branch if needed)"""
    try:
        owner = body.get('owner')
        repo = body.get('repo')
        path = body.get('path')
        content = body.get('content')
        message = body.get('message')
        branch = body.get('branch')
        from_branch = body.get('from_branch', 'main')

        if not all([owner, repo, path, content, message, branch]):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'message': 'owner, repo, path, content, message, and branch are required'
                })
            }

        # Ensure target branch exists and get base commit sha
        base_commit_sha, target_branch, err_resp = _ensure_branch_and_get_base(http, headers, owner, repo, branch, from_branch)
        if not base_commit_sha:
            return {
                'statusCode': err_resp.status if err_resp else 500,
                'body': json.dumps({
                    'success': False,
                    'message': 'Failed to ensure target branch exists',
                    'details': err_resp.data.decode('utf-8') if err_resp else 'Unknown error'
                })
            }

        # Get base tree
        commit_sha, base_tree_sha, commit_resp_err = _get_commit_and_tree(http, headers, owner, repo, base_commit_sha)
        if not base_tree_sha:
            return {
                'statusCode': commit_resp_err.status if commit_resp_err else 500,
                'body': json.dumps({
                    'success': False,
                    'message': 'Failed to get base commit/tree',
                    'details': commit_resp_err.data.decode('utf-8') if commit_resp_err else 'Unknown error'
                })
            }

        # Create blob for file content
        blob_resp = _create_blob(http, headers, owner, repo, content)
        if blob_resp.status not in [200, 201]:
            return {
                'statusCode': blob_resp.status,
                'body': json.dumps({
                    'success': False,
                    'message': 'Failed to create blob for file',
                    'details': blob_resp.data.decode('utf-8')
                })
            }
        blob_sha = json.loads(blob_resp.data.decode('utf-8')).get('sha')

        # Create tree with the file
        tree_entries = [{
            "path": path,
            "mode": "100644",
            "type": "blob",
            "sha": blob_sha
        }]
        tree_resp = _create_tree(http, headers, owner, repo, base_tree_sha, tree_entries)
        if tree_resp.status not in [200, 201]:
            return {
                'statusCode': tree_resp.status,
                'body': json.dumps({
                    'success': False,
                    'message': 'Failed to create tree',
                    'details': tree_resp.data.decode('utf-8')
                })
            }
        new_tree_sha = json.loads(tree_resp.data.decode('utf-8')).get('sha')

        # Create commit
        commit_resp = _create_commit(http, headers, owner, repo, message, new_tree_sha, commit_sha)
        if commit_resp.status not in [200, 201]:
            return {
                'statusCode': commit_resp.status,
                'body': json.dumps({
                    'success': False,
                    'message': 'Failed to create commit',
                    'details': commit_resp.data.decode('utf-8')
                })
            }
        new_commit_sha = json.loads(commit_resp.data.decode('utf-8')).get('sha')

        # Update branch ref
        update_resp = _update_branch_ref(http, headers, owner, repo, target_branch, new_commit_sha)
        if update_resp.status not in [200, 201]:
            return {
                'statusCode': update_resp.status,
                'body': json.dumps({
                    'success': False,
                    'message': 'Failed to update branch reference',
                    'details': update_resp.data.decode('utf-8')
                })
            }

        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'message': 'File committed successfully',
                'branch': target_branch,
                'commit_sha': new_commit_sha,
                'files': [path]
            })
        }

    except Exception as e:
        import traceback
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'message': f'Error: {str(e)}',
                'traceback': traceback.format_exc()
            })
        }

def open_pr_from_changes(http, headers, body):
    """Create a branch from base, commit multiple file changes in one commit, and open a PR"""
    try:
        owner = body.get('owner')
        repo = body.get('repo')
        title = body.get('title')
        files = body.get('files', [])
        base = body.get('base', 'main')
        branch = body.get('branch')  # optional
        pr_body = body.get('body', '')
        commit_message = body.get('commit_message', 'Apply changes via API')

        if not all([owner, repo, title]) or not isinstance(files, list) or len(files) == 0:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'message': 'owner, repo, title, and non-empty files array are required'
                })
            }

        # Determine branch name
        if not branch:
            branch = f"changes-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        # Ensure target branch exists (create from base if needed)
        base_commit_sha, target_branch, err_resp = _ensure_branch_and_get_base(http, headers, owner, repo, branch, base)
        if not base_commit_sha:
            return {
                'statusCode': err_resp.status if err_resp else 500,
                'body': json.dumps({
                    'success': False,
                    'message': 'Failed to ensure target branch exists',
                    'details': err_resp.data.decode('utf-8') if err_resp else 'Unknown error'
                })
            }

        # Get base commit/tree
        parent_sha, base_tree_sha, commit_resp_err = _get_commit_and_tree(http, headers, owner, repo, base_commit_sha)
        if not base_tree_sha:
            return {
                'statusCode': commit_resp_err.status if commit_resp_err else 500,
                'body': json.dumps({
                    'success': False,
                    'message': 'Failed to get base commit/tree',
                    'details': commit_resp_err.data.decode('utf-8') if commit_resp_err else 'Unknown error'
                })
            }

        # Create blobs for all files
        tree_entries = []
        for f in files:
            path = f.get('path')
            content = f.get('content')
            if not path or content is None:
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'success': False,
                        'message': 'Each file must include path and content'
                    })
                }
            blob_resp = _create_blob(http, headers, owner, repo, content)
            if blob_resp.status not in [200, 201]:
                return {
                    'statusCode': blob_resp.status,
                    'body': json.dumps({
                        'success': False,
                        'message': f'Failed to create blob for {path}',
                        'details': blob_resp.data.decode('utf-8')
                    })
                }
            blob_sha = json.loads(blob_resp.data.decode('utf-8')).get('sha')
            tree_entries.append({
                "path": path,
                "mode": "100644",
                "type": "blob",
                "sha": blob_sha
            })

        # Create a new tree
        tree_resp = _create_tree(http, headers, owner, repo, base_tree_sha, tree_entries)
        if tree_resp.status not in [200, 201]:
            return {
                'statusCode': tree_resp.status,
                'body': json.dumps({
                    'success': False,
                    'message': 'Failed to create tree',
                    'details': tree_resp.data.decode('utf-8')
                })
            }
        new_tree_sha = json.loads(tree_resp.data.decode('utf-8')).get('sha')

        # Create a commit
        commit_resp = _create_commit(http, headers, owner, repo, commit_message, new_tree_sha, parent_sha)
        if commit_resp.status not in [200, 201]:
            return {
                'statusCode': commit_resp.status,
                'body': json.dumps({
                    'success': False,
                    'message': 'Failed to create commit',
                    'details': commit_resp.data.decode('utf-8')
                })
            }
        new_commit_sha = json.loads(commit_resp.data.decode('utf-8')).get('sha')

        # Update branch ref to point to the new commit
        update_resp = _update_branch_ref(http, headers, owner, repo, target_branch, new_commit_sha)
        if update_resp.status not in [200, 201]:
            return {
                'statusCode': update_resp.status,
                'body': json.dumps({
                    'success': False,
                    'message': 'Failed to update branch reference',
                    'details': update_resp.data.decode('utf-8')
                })
            }

        # Open PR
        pr_payload = {
            "title": title,
            "head": target_branch,
            "base": base,
            "body": pr_body
        }
        pr_url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        pr_resp = http.request('POST', pr_url, headers=headers, body=json.dumps(pr_payload))
        if pr_resp.status not in [200, 201]:
            return {
                'statusCode': pr_resp.status,
                'body': json.dumps({
                    'success': False,
                    'message': 'Failed to open pull request',
                    'details': pr_resp.data.decode('utf-8')
                })
            }
        pr_data = json.loads(pr_resp.data.decode('utf-8'))

        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'message': 'Pull request opened successfully',
                'branch': target_branch,
                'commit_sha': new_commit_sha,
                'pr_number': pr_data.get('number'),
                'pr_url': pr_data.get('html_url'),
                'state': pr_data.get('state'),
                'created_at': pr_data.get('created_at')
            })
        }

    except Exception as e:
        import traceback
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'message': f'Error: {str(e)}',
                'traceback': traceback.format_exc()
            })
        }
  
def lambda_handler(event, context):
    """Lambda handler for GitHub API operations"""
    
    # Parse event with better error handling
    try:
        # Handle direct invocation (event is already a dict)
        if isinstance(event, dict) and 'action' in event:
            body = event
        # Handle API Gateway invocation (event has 'body' field)
        elif 'body' in event:
            if isinstance(event['body'], str):
                if not event['body'] or event['body'].strip() == '':
                    return {
                        'statusCode': 400,
                        'body': json.dumps({'success': False, 'message': 'Empty request body'})
                    }
                body = json.loads(event['body'])
            else:
                body = event['body']
        else:
            # Fallback: treat entire event as body
            body = event
            
    except json.JSONDecodeError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'success': False, 
                'message': f'Invalid JSON in request body: {str(e)}',
                'received_body': event.get('body', 'No body field')[:200]
            })
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'success': False, 
                'message': f'Invalid request format: {str(e)}',
                'event_keys': list(event.keys()) if isinstance(event, dict) else 'event is not a dict'
            })
        }
    
    action = body.get('action')
    
    # Check for help request - return in MCP format
    if action in ['help', 'list_tools']:
        tools_data = get_available_tools()
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'content': [
                    {
                        'type': 'text',
                        'text': json.dumps(tools_data)
                    }
                ]
            })
        }
    
    # Validate action exists
    if not action:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'success': False, 
                'message': 'action is required',
                'received_body': body
            })
        }
    
    # Get GitHub token
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
    
    if not GITHUB_TOKEN:
        return {
            'statusCode': 500,
            'body': json.dumps({'success': False, 'message': 'GITHUB_TOKEN not configured'})
        }
    
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'AWS-Lambda-GitHub-Integration'
    }
    
    try:
        http = urllib3.PoolManager()
        
        actions = {
            'get_file': lambda: get_file(http, headers, body),
            'create_pull_request': lambda: create_pull_request(http, headers, body),
            'list_pull_requests': lambda: list_pull_requests(http, headers, body),
            'search_code': lambda: search_code(http, headers, body),
            'list_repos': lambda: list_repos(http, headers, body),
            'create_or_update_file': lambda: create_or_update_file(http, headers, body),
            'create_branch': lambda: create_branch(http, headers, body),
            'list_branches': lambda: list_branches(http, headers, body),
            'commit_file': lambda: commit_file(http, headers, body),
            'open_pr_from_changes': lambda: open_pr_from_changes(http, headers, body)
        }
        
        if action in actions:
            return actions[action]()
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'message': f'Unknown action: {action}',
                    'available_actions': list(actions.keys())
                })
            }
    
    except Exception as e:
        import traceback
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False, 
                'message': f'Error: {str(e)}',
                'traceback': traceback.format_exc()
            })
        }