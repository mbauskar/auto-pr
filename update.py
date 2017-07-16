from utils import exec_cmd

def update_benches():
	"""
		update the both frappe-bench and release-bench
	"""
	from utils import config

	update_bench = config.get("update_bench")
	release_bench = config.get("release_bench")

	for bench in [update_bench, release_bench]:
		exec_cmd(bench, ['bench update --no-backup'])