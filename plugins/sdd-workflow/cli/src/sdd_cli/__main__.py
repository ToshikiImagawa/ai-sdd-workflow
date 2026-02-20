"""Main CLI entry point for sdd-cli."""

import click
import os
from pathlib import Path
from sdd_cli import get_cache_dir


@click.group()
@click.version_option()
@click.pass_context
def cli(ctx):
    """SDD CLI - AI-SDD Workflow Document Management Tool.

    Provides indexing, search, and visualization features for SDD documents.
    """
    ctx.ensure_object(dict)


@cli.command()
@click.option(
    "--root",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=lambda: Path(os.environ.get("SDD_ROOT", ".sdd")),
    help="SDD root directory (default: $SDD_ROOT or .sdd)",
)
@click.option(
    "--quiet",
    is_flag=True,
    help="Suppress output messages",
)
@click.pass_context
def index(ctx, root, quiet):
    """Build or rebuild the document index.

    Scans all documents in the SDD root directory and creates a full-text
    search index using SQLite FTS5.
    """
    from sdd_cli.commands.index import build_index

    try:
        build_index(root, quiet)
        if not quiet:
            project_root = root.parent if root.name == ".sdd" else root
            cache_dir = get_cache_dir(project_root)
            click.echo(f"✓ Index built successfully at {cache_dir / 'index.db'}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)


@cli.command()
@click.argument("query", required=False)
@click.option(
    "--root",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=lambda: Path(os.environ.get("SDD_ROOT", ".sdd")),
    help="SDD root directory (default: $SDD_ROOT or .sdd)",
)
@click.option(
    "--feature-id",
    help="Filter by feature ID",
)
@click.option(
    "--tag",
    help="Filter by tag",
)
@click.option(
    "--dir",
    "directory",
    type=click.Choice(["requirement", "specification", "task"]),
    help="Filter by directory type",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format (default: text)",
)
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    help="Output file path (default: stdout)",
)
@click.option(
    "--limit",
    type=int,
    default=10,
    help="Maximum number of results (default: 10)",
)
@click.pass_context
def search(ctx, query, root, feature_id, tag, directory, output_format, output, limit):
    """Search SDD documents.

    Performs full-text search across all indexed documents with optional
    filtering by feature ID, tags, or directory type.

    Examples:
        sdd-cli search "ログイン機能"
        sdd-cli search --feature-id user-login
        sdd-cli search "認証" --tag security --dir specification
    """
    from sdd_cli.commands.search import search_documents

    try:
        results = search_documents(
            root=root,
            query=query,
            feature_id=feature_id,
            tag=tag,
            directory=directory,
            output_format=output_format,
            limit=limit,
        )

        if output:
            output.write_text(results)
            if output_format == "text":
                click.echo(f"✓ Results written to {output}")
        else:
            click.echo(results)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)


@cli.command()
@click.option(
    "--root",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=lambda: Path(os.environ.get("SDD_ROOT", ".sdd")),
    help="SDD root directory (default: $SDD_ROOT or .sdd)",
)
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    help="Output file path (default: ~/.cache/sdd-cli/{project-hash}/dependency-graph.json)",
)
@click.option(
    "--filter-dir",
    type=click.Choice(["requirement", "specification", "task"]),
    help="Only visualize documents in specific directory",
)
@click.option(
    "--feature-id",
    help="Only visualize documents related to specific feature",
)
@click.option(
    "--html",
    is_flag=True,
    help="Generate interactive HTML visualization and start local server",
)
@click.pass_context
def visualize(ctx, root, output, filter_dir, feature_id, html):
    """Generate dependency graph visualization.

    Analyzes document dependencies and generates a Mermaid diagram showing
    relationships between requirements, specifications, and designs.

    Examples:
        sdd-cli visualize
        sdd-cli visualize --filter-dir specification
        sdd-cli visualize --feature-id user-login
        sdd-cli visualize --html  # Interactive HTML with server
    """
    from sdd_cli.commands.visualize import generate_visualization

    try:
        if not output:
            project_root = root.parent if root.name == ".sdd" else root
            cache_dir = get_cache_dir(project_root)

            # Generate file name based on filter conditions
            if feature_id:
                filename = f"{feature_id}-graph"
            elif filter_dir:
                filename = f"{filter_dir}-graph"
            else:
                filename = "dependency-graph"

            output = cache_dir / filename

        generate_visualization(
            root=root,
            output=output,
            filter_dir=filter_dir,
            feature_id=feature_id,
            html=html,
            serve=html,  # Auto-start server when --html is used
        )

        if not html:
            click.echo(f"✓ Dependency graph generated at {output}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)


@cli.group()
def cache():
    """Manage cache directories.

    Commands for listing and cleaning cached project indexes.
    """
    pass


@cache.command("list")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format (default: text)",
)
def cache_list(output_format):
    """List all cached projects.

    Shows project name, size, last modified time, and document count.

    Examples:
        sdd-cli cache list
        sdd-cli cache list --format json
    """
    from sdd_cli.commands.cache import list_cache_projects, format_cache_list
    import json

    try:
        projects = list_cache_projects()

        if output_format == "json":
            click.echo(json.dumps(projects, indent=2, ensure_ascii=False))
        else:
            click.echo(format_cache_list(projects))

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cache.command("clean")
@click.option(
    "--project",
    help="Project name pattern to delete (supports wildcards like 'my-project*')",
)
@click.option(
    "--all",
    "all_projects",
    is_flag=True,
    help="Delete all cached projects",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be deleted without actually deleting",
)
@click.pass_context
def cache_clean(ctx, project, all_projects, dry_run):
    """Clean cache directories.

    Delete cached project indexes to free up disk space.

    Examples:
        # List what would be deleted
        sdd-cli cache clean --all --dry-run

        # Delete specific project
        sdd-cli cache clean --project slide-presentation-app

        # Delete all projects matching pattern
        sdd-cli cache clean --project 'test-*'

        # Delete all cached projects
        sdd-cli cache clean --all
    """
    from sdd_cli.commands.cache import clean_cache

    try:
        result = clean_cache(
            project_pattern=project,
            all_projects=all_projects,
            dry_run=dry_run
        )
        click.echo(result)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)


if __name__ == "__main__":
    cli()
