import json
import requests
import os, subprocess
from git import Repo
from datetime import datetime, date, timedelta
from requests.auth import HTTPBasicAuth

config = {}

def get_config():
	global config

	with open('build-server/config.json', 'r') as f:
		config = json.loads(f.read())
	return config

def validate_and_return_apps(app="all"):
	global config

	apps = []

	if app == "all":
		apps = config.get("apps")
	elif app not in config.get("apps"):
		print "{0} invalid app"
		return
	else:
		apps = [app]

	return apps

def now_date(format="%Y-%m-%d"):
	now_datetime = datetime.now()
	return now_datetime.strftime("%Y-%m-%d")

def exec_cmd(cwd, cmd, in_test=True):
	"""execute commands"""

	if not in_test:
		process = subprocess.Popen(cmd, cwd=cwd, shell=True, stdout=None, stderr=None)
		return_code = process.wait()
	else:
		print "running ", cmd, " on", cwd
		return_code = 0

	if return_code > 0:
		raise Exception("{0} command failed".format(cmd))

def pull(repo, remote, branch="develop", rebase=True):
	cmd = "git pull {rebase} {remote} {branch}".format(
			rebase="--rebase" if rebase else "",
			remote=remote or "upstream",
			branch=branch
		)
	exec_cmd(repo, [cmd])

def push(repo_path, branch_name, commit_msg, commit=True):
	if not all([repo_path, branch_name, commit_msg]):
		raise Exception("Invalid arguments")

	repo = Repo(repo_path)
	if commit:
		repo.git.add('--all')
		repo.index.commit(commit_msg)

	args = [
		'{branch}:{branch}'.format(branch=branch_name),
	]
	# push the changes
	repo.git.push('origin', *args)
	print "pushed the changes to repo with commit message\n{0}".format(commit_msg)

def pull_request(app, pr_title, branch, base="develop"):
	global config

	owner = 'frappe'
	github_username = config.get("github_username")
	github_password = config.get("github_password")
	url = 'https://api.github.com/repos/{0}/{1}/pulls'.format(owner, app)

	args = {
		"title": pr_title,
		"body": "This is system generated pull-request",
		"head": "{github_username}:{branch}".format(
			github_username=github_username,
			branch=branch
		),
		"base": base
	}

	r = requests.post(url, auth=HTTPBasicAuth(github_username, github_password),
			data=json.dumps(args))
	r.raise_for_status()
	print "created pull request for {0}".format(app)

def checkout(path, branch, create_new=False, delete_branch_after_checkout=False, delete_branch_name=None):
	# git checkout to `branch name`
	cmd = "git checkout {0} {1}".format("-b" if create_new else "", branch)
	exec_cmd(path, [cmd])
	if delete_branch_after_checkout and delete_branch_name:
		exec_cmd(path, ['git branch -D {0}'.format(delete_branch_name)])