""" build frappe / erpnext translation """

import json
import requests
from git import Repo
import os, subprocess
from datetime import datetime, date, timedelta
from requests.auth import HTTPBasicAuth

github_user_id = "mbauskar"
github_password = "mak@github42"

apps = ['frappe', 'erpnext']
update_bench_path = "/home/frappe/frappe-bench"
release_bench_path = "/home/frappe/release-bench"

def update_benches():
	"""
		update the both frappe-bench and release-bench
	"""

	try:
		for bench_path in [update_bench_path, release_bench_path]:
			cmd = ['bench update']
			exec_cmd(bench_path, cmd)
	except Exception as e:
		raise e

def build_translation():
	"""
 		- import unstranslated strings and translate them using google translate
 		- sent the PR for frappe and erpnext
	"""

	try:

		# import source messages
		cmd = ['bench translator import-source-messages']
		exec_cmd(update_bench_path, cmd)

		# translate unstranslated messages
		cmd = ['bench translator translate-untranslated-all']
		exec_cmd(update_bench_path, cmd)

		# write csv
		cmd = ['bench --site translate.erpnext.com execute "translator.data.write_csv_for_all_languages"']
		exec_cmd(update_bench_path, cmd)

		branch_name = "translations-{0}".format(now_date(format='%Y.%m.%d'))
		for app in apps:
			path = os.path.join(release_bench_path, app)

			checkout_branch(path, branch_name, create_new=True)

			# copy translation to release bench
			source = "{path}/{app}-*.csv".format(
				path=os.path.join(update_bench_path, 'sites', 'translate.erpnext.com', 'public', 'files'),
				app=app
			)
			target = os.path.join(release_bench_path, "apps", app, app, 'translations')
			cmd = ['cp {0} {1}'.format(source, target)]

			path = os.path.join(release_bench_path, 'apps', app)
			commit_msg = "[translation] translation updates for - {app} on {date}".format(
				app=app,
				date=now_date()
			)

			args = [
				'{branch}:{branch}'.format(branch=branch_name),
			]

			commit_and_push(app, path, args, commit_msg)
			args = {
				"title": "[translate] translation update",
				"body": "This is system generated pull-request<br>Updated the translation for {}".format(app),
				"head": "{github_user_id}:{branch}".format(
					github_user_id=github_user_id,
					branch=branch_name
				),
				"base": "develop"
			}
			create_pull_request(app, args, github_user_id, github_password)

			checkout_branch(path, "develop", delete_branch_after_checkout=True, delete_branch_name=branch_name)
	except Exception as e:
		import traceback
		print traceback.print_exc()
		pass

def build_docs():
	"""
		- build documentation for erpnext and frappe
		- sent the PR for documentation for frappe and erpnext
	"""
	try:
		docs_path = os.path.join(release_bench_path, 'docs')
		if not os.path.isdir(docs_path):
			# create docs directory in frappe-bench
			os.makedirs(docs_path)

		repo_path = ""
		branch_name = "docs-{0}".format(now_date(format='%Y.%m.%d'))

		for app in apps:
			repo_path = os.path.join(docs_path, app)
			if not os.path.exists(repo_path):
				continue

			checkout_branch(repo_path, branch_name, create_new=True)

			cmd = ['bench --site buildserver.erpnext.dev build-docs {0}'.format(app)]
			exec_cmd(release_bench_path, cmd)

			commit_msg = "[docs] documentation updates for - {app} on {date}".format(
				app=app,
				date=now_date()
			)

			# pushing changes to gh-pages branch
			args = [
				'{branch}:{branch}'.format(branch=branch_name),
			]
			commit_and_push(app, repo_path, args, commit_msg)
			args = {
				"title": "[docs] documentation update",
				"body": "This is system generated pull-request<br>Updated the documentation for {}".format(app),
				"head": "{github_user_id}:{branch}".format(
					github_user_id=github_user_id,
					branch=branch_name
				),
				"base": "gh-pages"
			}
			create_pull_request(app, args, github_user_id, github_password)

			checkout_branch(path, "develop", delete_branch_after_checkout=True, delete_branch_name=branch_name)
	except Exception as e:
		print e

def commit_and_push(app, repo_path, args, commit_msg):
	if not all([app, repo_path, args, commit_msg]):
		return

	try:
		repo = Repo(repo_path)

		repo.git.add('--all')
		repo.index.commit(commit_msg)

		# push the changes
		repo.git.push('origin', *args)

		print "pushed the changes to repo with commit message\n{}".format(commit_msg)
	except Exception as e:
		raise e

def create_pull_request(repo_name, args, gh_username, gh_password):
	owner = 'frappe'
	try:
		r = requests.post('https://api.github.com/repos/{owner}/{repo_name}/pulls'.format(
			owner=owner, repo_name=repo_name),
			auth=HTTPBasicAuth(gh_username, gh_password), data=json.dumps(args))
		r.raise_for_status()
		print "created pull request for {}".format(repo_name)
	except requests.exceptions.HTTPError:
		import traceback
		print traceback.print_exc()
		print 'request failed'

def checkout_branch(path, branch, create_new=False, delete_branch_after_checkout=False, delete_branch_name=None):
	try:
		# git checkout to `branch name`
		cmd = "git checkout {0} {1}".format("-b" if create_new else "", branch_name)
		exec_cmd(path, [cmd])
		if delete_branch_after_checkout and delete_branch_name:
			exec_cmd(path, ['git branch -D {0}'.format(delete_branch_name)])

	except Exception as e:
		raise e

def now_date(format="%Y-%m-%d"):
	now_datetime = datetime.now()
	return now_datetime.strftime("%Y-%m-%d")

def exec_cmd(cwd, cmd):
	"""execute commands"""
	try:
		process = subprocess.Popen(cmd, cwd=cwd, shell=True, stdout=None, stderr=None)
		return_code = process.wait()

		if return_code > 0:
			raise Exception("{} command failed".format(cmd))
	except Exception as e:
		print "error", e

if __name__ == "__main__":
	update_benches()
	build_docs()
	build_translation()