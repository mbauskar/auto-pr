import os
from utils import exec_cmd, now_date, pull, push, pull_request, checkout

def build_translation(apps, _pull=False):
	""" build frappe app's translation """
	from utils import config

	config_apps = config.get("apps")
	update_bench = config.get("update_bench")
	release_bench = config.get("release_bench")
	release_bench_site = config.get("release_bench_site")
	update_bench_site = config.get("update_bench_site")
	commit_msg = config.get("translation_commit_msg") or "[docs] Updated translation"
	base_branch = config.get("base_branch") or "develop"

	# import source messages
	exec_cmd(update_bench,
		['bench --site {0} import-source-messages'.format(update_bench_site)])

	# translate unstranslated messages
	exec_cmd(update_bench,
		['bench --site {0} translate-untranslated-all'.format(update_bench_site)])

	# write csv
	exec_cmd(update_bench,
		['bench --site {0} execute "translator.data.write_csv_for_all_languages"'.format(update_bench_site)])

	# download the translation csv to frappe/erpnext app
	exec_cmd(release_bench, ['bench download-translations'])
	branch = "translations-{0}".format(now_date(format='%Y.%m.%d'))
	try:
		for app in config_apps:
			path = os.path.join(release_bench, 'apps', app)
			if app not in apps:
				exec_cmd(path, ['git stash'])

			if not path:
				print "app is not installed"
				continue

			if _pull:
				pull(path, "upstream", base_branch)
			checkout(path, branch, create_new=True)

			args = [
				'{branch}:{branch}'.format(branch=branch),
			]
			push(app, path, branch, commit_msg)
			pull_request(app, commit_msg, branch, base=base_branch)
			checkout(path, base_branch, delete_branch_after_checkout=True, delete_branch=branch)
	except Exception as e:
		print e