#!/usr/bin/env python

from yaml import load, Loader
from ghapi.core import GhApi
from ghapi.page import pages
import click

def _fetch_releases(api):
    things = api.repos.list_releases(per_page=100)
    last_page = api.last_page()
    if last_page > 0:
        things = pages(api.repos.list_releases(last_page)).concat()
    return things


@click.command('make-release-pages')
@click.argument('config', type=click.File())
@click.argument('tokenfile', type=click.File())
@click.argument('outdir', type=click.Path(dir_okay=True, file_okay=False, exists=True))
def run(config, tokenfile, outdir):
    cfg = load(config, Loader=Loader)
    token = tokenfile.read().strip()

    org = cfg['github_org']
    repo = cfg['repo']

    api = GhApi(owner=org, repo=repo, token=token)
    releases = _fetch_releases(api)

    fm = open(f"{outdir}/releases.md", 'w')

    fm.write("# Releases\n\n")
    for release in releases:
        fm.write(f"## {release.name}\n")
        fm.write(f"{release.body}\n\n")

        fm.write(f"[More info](release_{release.tag_name}.html)\n\n")

        rm = open(f"{outdir}/release_{release.tag_name}.md", 'w')
        rm.write(f"# {release.name}\n")
        rm.write(f"{release.body}\n\n")
        rm.write(f"Release artefacts:\n\n")
        base_url = f"https://github.com/{org}/{repo}/blob/{release.tag_name}"
        for artefact in cfg['release_artefacts']:
            if artefact.startswith('custom-'):
                display_name = artefact[7:]
                file_name = artefact[7:]
            else:
                display_name = artefact
                file_name = f"{cfg['id']}-{artefact}"
            rm.write(f"## {display_name}\n")
            for format in cfg['export_formats']:
                rm.write(f" - [{display_name}.{format}]({base_url}/{file_name}.{format})\n")
        rm.close()

    fm.close()

if __name__ == '__main__':
    run()
