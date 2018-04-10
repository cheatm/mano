import click
from mano.commands.check_log import notice


group = click.Group(
    "mail",
    {"notice": notice}
)


if __name__ == '__main__':
    group()