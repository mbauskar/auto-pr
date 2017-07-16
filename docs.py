import os
from utils import exec_cmd, now_date, pull, push, pull_request, checkout

def build_docs(apps, _pull=False):
	""" build frappe app's documentation """
	from utils import config

	release_bench = config.get("release_bench")
	release_bench_sitename = config.get("release_bench_sitename")
	commit_msg = config.get("docs_commit_msg") or "[docs] documentation update"

	docs_path = os.path.join(release_bench, 'docs')
	if not os.path.isdir(docs_path):
		print "release bench is not configured to build documentation"
		return

	branch = "docs-{0}".format(now_date(format='%Y.%m.%d'))
	for app in apps:
		try:
			apps_path = os.path.join(release_bench, 'apps', app)
			if not apps_path:
				print "app is not installed"

			repo_path = os.path.join(docs_path, app)
			if not os.path.isdir(repo_path):
				print "release bench is not configured to build {0}'s documentation".format(repo_path)
				continue

			# rebase the gh-pages branch from upstream
			pull(repo_path, "upstream", "gh-pages")
			if _pull:
				pull(apps_path, "upstream", "develop")

			checkout(repo_path, branch, create_new=True)

			# build docs
			exec_cmd(release_bench, \
				['bench --site {0} build-docs {1}'.format(release_bench_sitename, app)])
			# pushing changes to gh-pages branch
			push(app, repo_path, branch, commit_msg, commit=True)
			pull_request(app, commit_msg, branch, base="gh-pages")
			checkout(repo_path, "gh-pages", delete_branch_after_checkout=True, delete_branch_name=branch)
		except Exception as e:
			print e