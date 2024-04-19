# Solana program cloner CLI

import click
from .clone import clone as do_clone
from .sort import sort as do_sort

@click.group()
def cli():
    pass

@click.command()
@click.argument("bundle_name", type=str)
@click.option(
    "--url",
    type=str,
    default="http://localhost:8899",
    help="RPC URL to use for queries.",
)
@click.option(
    "--rate-limit-buffer",
    type=int,
    default=0,
    help="Time delay between RPC query batches to avoid rate limiting.",
)
def clone(bundle_name, url, rate_limit_buffer):
    """
    Download all Solana programs from the provided RPC URL to the provided
    bundle name.
    """
    do_clone(bundle_name, url, rate_limit_buffer)

@click.command()
@click.argument("bundle_name", type=str)
@click.option(
    "--url",
    type=str,
    default="http://localhost:8899",
    help="RPC URL to use for queries.",
)
@click.option(
    "--rate-limit-buffer",
    type=int,
    default=0,
    help="Time delay between RPC query batches to avoid rate limiting.",
)
def sort(bundle_name, url, rate_limit_buffer):
    """
    Sort the downloaded programs by the slot they were last executed, starting
    from the most recent slot.
    """
    do_sort(bundle_name, url, rate_limit_buffer)

cli.add_command(clone)
cli.add_command(sort)

if __name__ == "__main__":
    cli()