import os
from utils import exec_cmd, now_date, pull, push, pull_request, checkout

def build_docs(apps, _pull=False):
	""" build frappe app's documentation """
	from utils import config

	release_bench = config.get("release_bench")
	release_bench_site = config.get("release_bench_site")
	commit_msg = config.get("docs_commit_msg")
	target_app_mapper = config.get("docs_target_apps")
	base_branch = config.get("base_branch") or "develop"

	branch = "docs-{0}".format(now_date(format='%Y.%m.%d'))
	for app in apps:
		try:
			apps_path = os.path.join(release_bench, 'apps', app)
			if not apps_path:
				print "app is not installed"

			target = target_app_mapper.get(app, {})
			target_app = target.get("app", None)
			owner = target.get("owner", None)
			if not target_app or not owner:
				print "target app mapping not available"

			target_app_path = os.path.join(release_bench, 'apps', target_app)
			if not target_app_path:
				print "app is not installed"

			if _pull:
				pull(apps_path, "upstream", base_branch)

			checkout(target_app_path, branch, create_new=True)

			# build docs
			exec_cmd(release_bench, \
				['bench --site {0} build-docs --target {1} {2}'.format(release_bench_site, target_app, app)])

			push(app, target_app_path, branch, commit_msg, commit=True)
			pull_request(app, commit_msg, branch, base="master", owner=owner)
			checkout(target_app_path, "master", delete_branch_after_checkout=False, delete_branch=branch)
		except Exception as e:
			print e