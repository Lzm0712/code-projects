import typer
import click

app = typer.Typer()

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    log_file: str = typer.Argument(None),
    log_level: str = typer.Option('INFO', '--log-level'),
):
    print(f'Callback: log_file={log_file}, log_level={log_level}')
    print(f'  invoked={ctx.invoked_subcommand}')

@app.command('filter')
def filter_cmd():
    print('filter called')

if __name__ == '__main__':
    app()
