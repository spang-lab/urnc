#!/usr/bin/env python3
import click

from urnc.version import version


@click.group()
@click.option("-f", "--config-file", "config")
def main(config):
    pass


main.add_command(version)
