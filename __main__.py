import click

from docs import build_docs
from error import handle_error
from update import update_benches
from translation import build_translation
from utils import config, get_config, validate_and_return_apps

@click.group()
def cli():
	config = get_config()
	if not config:
		handle_error("cli", "invalid config")

@cli.command()
@click.option('--app', default="all", help='build translation for app, \
	if not specified then translation will be build for apps defined in config')
@click.option('--pull', is_flag=True, help="pull changes in app before building documentatation")
def translation(app="all", pull=False):
	""" build the translation """
	apps = validate_and_return_apps(app)
	build_translation(apps, _pull=pull)

@cli.command()
@click.option('--app', default="all", help='build documentation for app, \
	if not specified then translation will be build for apps defined in config')
@click.option('--pull', is_flag=True, help="pull changes in app before building documentatation")
def docs(app="all", pull=False):
	""" build the documentation """
	apps = validate_and_return_apps(app)
	build_docs(apps, _pull=pull)

@cli.command()
@click.option('--app', default="all", help='build documentation and translation for app, \
	if not specified then translation will be build for apps defined in config')
def build(app=None):
	"""update the benches and build documentations / translation"""
	apps = validate_and_return_apps(app)
	update_benches()

	# build documentation & translation
	build_docs(apps, _pull=False)
	build_translation(apps, _pull=False)

if __name__=='__main__':
	cli()