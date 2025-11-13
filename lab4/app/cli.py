import click
from flask import current_app
from .extensions import db

@click.command('init-db')
def init_db_command():
    with current_app.open_resource('schema.sql') as f:
        connection = db.connect()
        with connection.cursor() as cursor:
            # for _ in cursor.execute(f.read().decode('utf8'), multi=True):
            #     pass
            sql_script = f.read().decode('utf8')
            for statement in sql_script.split(';'):
                if statement.strip():
                    cursor.execute(statement)
        connection.commit()
    click.echo('Initialized the database.')
