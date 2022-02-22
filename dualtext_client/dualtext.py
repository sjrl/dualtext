import click
import keyring
import json
import sys

from session import Session
from project import Project
from settings import API_URL


@click.group()
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)
    access_token = keyring.get_password('dualtext', 'token')
    if access_token:
        s = Session()
        s.set_token(access_token)
        token_valid = s.validate_token()
        if not token_valid:
            keyring.delete_password('dualtext', 'token')
            access_token = None

    if access_token is None:
        s = Session()
        username = click.prompt('Please enter your username')
        pw = click.prompt('Password', hide_input=True)
        click.echo(f'connecting to dualtext at {API_URL}', err=True)
        s.login(username, pw)
        click.echo('login successful', err=True)
        access_token = s.get_token()
        keyring.set_password('dualtext', 'token', access_token)
    ctx.obj['Token'] = access_token


@click.group()
@click.pass_context
def project(ctx):
    pass

@project.command('create')
@click.option('--search/--no-search', default=False)
@click.option(
    '--project-file',
    help='File containing project data.',
    type=click.File('r'),
    default=sys.stdin
)
@click.option(
    '--task-size',
    '-t',
    help='Sets the number of documents for a task. Default is 20.',
    type=click.INT,
    default=20
)
@click.pass_context
def create(ctx, project_file, search, task_size):
    click.echo('Starting to create a project...', err=True)

    # create session
    token = ctx.obj['Token']
    s = Session()
    s = s.set_token(token)
    p = Project(s)

    with project_file:
        data = json.loads(project_file.read())
    if (search):
        proj = p.create_from_documents(data, task_size=task_size)
    else:
        proj = p.create_from_scratch(data, task_size=task_size)

    click.echo('Finished creating the project. Project id is {}'.format(proj['id']), err=True)


@project.command('download')
@click.option(
    '--project-id',
    '-p',
    help='Id of project that you would like to download from.',
    type=click.INT,
    default=sys.stdin
)
@click.option('--action', '-a', type=str)
@click.option('--finished', 'status', flag_value=True)
@click.option('--notfinished', 'status', flag_value=False)
@click.option('--label', '-l', type=str, multiple=True)
@click.option(
    "--out",
    help="File to write the Output to, omit to display on screen.",
    type=click.File("w"),
    default=sys.stdout,
)
@click.pass_context
def download_project(ctx, project_id, out, action=None, label=None, status=None):
    task_params = {}
    annotation_params = {}
    if action is not None:
        task_params['action'] = action
    if status is not None:
        task_params['is_finished'] = status
    if label is not None:
        annotation_params['label_name'] = list(label)
    token = ctx.obj['Token']
    s = Session()
    s = s.set_token(token)
    p = Project(s)
    click.echo(json.dumps(p.get_annotations(project_id, task_params=task_params, annotation_params=annotation_params)), file=out)


cli.add_command(project)





