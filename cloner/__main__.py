# Solana program cloner CLI

import click
from .chart import chart_profiled_slots as do_chart_profiled_slots
from .clone import clone as do_clone
from .profile import profile_slots as do_profile_slots
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

@click.command()
@click.argument("profile_name", type=str)
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
def profile_slots(profile_name, url, rate_limit_buffer):
    """
    Profile all Solana Loader V3 programs based on their deployment slot, using
    the provided RPC URL.
    """
    do_profile_slots(profile_name, url, rate_limit_buffer)

@click.command()
@click.argument("profile_name", type=str)
def chart_profiled_slots(profile_name):
    """
    Create a scatter plot of deployment slots for each program ID.
    """
    do_chart_profiled_slots(profile_name)

cli.add_command(clone)
cli.add_command(sort)
cli.add_command(profile_slots)
cli.add_command(chart_profiled_slots)

if __name__ == "__main__":
    cli()