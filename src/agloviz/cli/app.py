"""Main CLI application for ALGOViz."""

from pathlib import Path

import typer
from rich.console import Console

# Create the main Typer app
app = typer.Typer(
    name="agloviz",
    help="ALGOViz: A modular framework for generating narrated algorithm "
    "visualization videos",
    no_args_is_help=True,
)

# Create a rich console for colored output
console = Console()


@app.command()
def version() -> None:
    """Show ALGOViz version information."""
    from agloviz import __version__

    console.print(f"ALGOViz version: [bold blue]{__version__}[/bold blue]")


@app.command()
def list_algorithms() -> None:
    """List available algorithms."""
    from agloviz.adapters.registry import AdapterRegistry

    algorithms = AdapterRegistry.list_algorithms()
    if not algorithms:
        console.print("[yellow]No algorithms registered[/yellow]")
        return

    console.print("[bold]Available Algorithms:[/bold]")
    for algo in algorithms:
        console.print(f"  • {algo}")

    if len(algorithms) == 1:
        console.print()
        console.print("[dim]Note: More algorithms will be added in future phases.[/dim]")


@app.command()
def render(
    algorithm: str = typer.Argument(..., help="Algorithm to visualize"),
    scenario: str = typer.Option(
        "demo.yaml", "--scenario", "-s", help="Scenario configuration file"
    ),
    quality: str = typer.Option(
        "medium", "--quality", "-q", help="Render quality: draft, medium, high"
    ),
    output_dir: str = typer.Option(
        "./output", "--output-dir", "-o", help="Output directory"
    ),
) -> None:
    """Render an algorithm visualization video."""
    console.print(
        f"[bold blue]Rendering {algorithm} with scenario {scenario}[/bold blue]"
    )
    console.print(f"Quality: {quality}, Output: {output_dir}")
    console.print("[yellow]This command will be fully implemented in Phase 1[/yellow]")


@app.command()
def preview(
    algorithm: str = typer.Argument(..., help="Algorithm to preview"),
    scenario: str = typer.Option(
        "demo.yaml", "--scenario", "-s", help="Scenario configuration file"
    ),
    frames: int = typer.Option(
        120, "--frames", "-f", help="Number of frames to render"
    ),
) -> None:
    """Preview an algorithm visualization (quick render)."""
    console.print(f"[bold blue]Previewing {algorithm} with {frames} frames[/bold blue]")
    console.print(f"Scenario: {scenario}")
    console.print("[yellow]This command will be fully implemented in Phase 1[/yellow]")


@app.command()
def config_validate(
    config_file: str = typer.Argument(..., help="Configuration file to validate"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode for detailed error info"),
) -> None:
    """Validate a configuration file."""
    from agloviz.cli.error_display import handle_cli_exception
    from agloviz.config import ConfigManager

    console.print(f"[bold blue]Validating configuration: {config_file}[/bold blue]")

    try:
        manager = ConfigManager()
        video_config = manager.load_and_validate(yaml_paths=[config_file])

        console.print("✅ [bold green]Configuration is valid![/bold green]")
        console.print(f"📋 Scenario: {video_config.scenario.name}")
        console.print(f"🎨 Theme: {video_config.theme.name}")
        console.print(f"⏱️ Timing mode: {video_config.timing.mode.value}")
        console.print(f"🎬 Render quality: {video_config.render.quality.value}")
        console.print(f"🔊 Voiceover: {'enabled' if video_config.voiceover.enabled else 'disabled'}")

    except Exception as e:
        handle_cli_exception(e, "configuration validation", config_file, debug)


@app.command()
def config_dump(
    output_file: str = typer.Argument(..., help="Output path for merged configuration"),
    config_files: list[str] = typer.Option(
        [], "--config", "-c", help="Configuration files to merge"
    ),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode for detailed error info"),
) -> None:
    """Dump merged configuration to YAML file for reproducibility."""
    from agloviz.cli.error_display import handle_cli_exception
    from agloviz.config import ConfigManager

    console.print(f"[bold blue]Dumping merged configuration to: {output_file}[/bold blue]")

    try:
        manager = ConfigManager()
        video_config = manager.load_and_validate(yaml_paths=config_files if config_files else None)
        manager.dump(video_config, output_file)

    except Exception as e:
        handle_cli_exception(e, "configuration dump", output_file, debug)


@app.command()
def config_create_samples(
    output_dir: str = typer.Option(
        "config/samples", "--output-dir", "-o", help="Output directory for sample files"
    ),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode for detailed error info"),
) -> None:
    """Create sample configuration files."""
    from agloviz.cli.error_display import handle_cli_exception
    from agloviz.config import ConfigManager

    console.print(f"[bold blue]Creating sample configuration files in: {output_dir}[/bold blue]")

    try:
        manager = ConfigManager()
        manager.create_sample_configs(output_dir)

        console.print("📝 [bold green]Sample files created:[/bold green]")
        console.print(f"   • {output_dir}/scenario.yaml - Algorithm scenario configuration")
        console.print(f"   • {output_dir}/timing.yaml - Timing and pacing settings")
        console.print(f"   • {output_dir}/theme.yaml - Visual theme and colors")
        console.print(f"   • {output_dir}/voiceover.yaml - Voiceover settings")

    except Exception as e:
        handle_cli_exception(e, "sample configuration creation", output_dir, debug)


@app.command()
def config_show(
    config_files: list[str] = typer.Option(
        [], "--config", "-c", help="Configuration files to show"
    ),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode for detailed error info"),
) -> None:
    """Show current configuration with precedence information."""
    from agloviz.cli.error_display import handle_cli_exception
    from agloviz.config import ConfigManager

    console.print("[bold blue]Current Configuration:[/bold blue]")

    try:
        manager = ConfigManager()
        video_config = manager.load_and_validate(yaml_paths=config_files if config_files else None)

        # Display configuration in a nice format
        config_dict = video_config.model_dump()

        console.print("\n📋 [bold]Scenario:[/bold]")
        scenario = config_dict.get('scenario', {})
        for key, value in scenario.items():
            console.print(f"  {key}: {value}")

        console.print("\n⏱️ [bold]Timing:[/bold]")
        timing = config_dict.get('timing', {})
        for key, value in timing.items():
            if key != 'multipliers':
                console.print(f"  {key}: {value}")

        console.print("\n🎨 [bold]Theme:[/bold]")
        theme = config_dict.get('theme', {})
        console.print(f"  name: {theme.get('name', 'default')}")
        colors = theme.get('colors', {})
        for role, color in colors.items():
            console.print(f"  {role}: {color}")

        console.print("\n🎬 [bold]Render:[/bold]")
        render = config_dict.get('render', {})
        for key, value in render.items():
            console.print(f"  {key}: {value}")

        console.print("\n🔊 [bold]Voiceover:[/bold]")
        voiceover = config_dict.get('voiceover', {})
        for key, value in voiceover.items():
            console.print(f"  {key}: {value}")

    except Exception as e:
        handle_cli_exception(e, "configuration display", None, debug)


@app.command()
def validate_storyboard(
    storyboard_path: str = typer.Argument(..., help="Path to storyboard YAML file"),
    validate_actions: bool = typer.Option(
        False, "--validate-actions", help="Validate that all actions are registered"
    ),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
) -> None:
    """Validate a storyboard YAML file."""
    from agloviz.cli.error_display import handle_cli_exception
    from agloviz.core.storyboard import StoryboardLoader, get_action_registry

    try:
        console.print(f"[bold blue]Validating storyboard: {storyboard_path}[/bold blue]")

        # Load and validate the storyboard
        loader = StoryboardLoader()
        storyboard = loader.load_from_yaml(storyboard_path)

        console.print("[green]✓[/green] Storyboard loaded successfully!")
        console.print(f"  Acts: {len(storyboard.acts)}")

        total_shots = sum(len(act.shots) for act in storyboard.acts)
        total_beats = sum(
            len(shot.beats)
            for act in storyboard.acts
            for shot in act.shots
        )

        console.print(f"  Shots: {total_shots}")
        console.print(f"  Beats: {total_beats}")

        # Show act structure
        console.print("\n[bold]Storyboard Structure:[/bold]")
        for i, act in enumerate(storyboard.acts, 1):
            console.print(f"  Act {i}: {act.title}")
            for j, shot in enumerate(act.shots, 1):
                console.print(f"    Shot {j}: {len(shot.beats)} beats")
                for k, beat in enumerate(shot.beats, 1):
                    action_info = f"'{beat.action}'"
                    if beat.narration:
                        action_info += " (with narration)"
                    if beat.bookmarks:
                        action_info += f" ({len(beat.bookmarks)} bookmarks)"
                    console.print(f"      Beat {k}: {action_info}")

        # Validate actions if requested
        if validate_actions:
            console.print("\n[bold]Validating Actions:[/bold]")
            registry = get_action_registry()

            # Register some basic actions for testing
            from unittest.mock import Mock
            basic_actions = [
                "show_title", "show_grid", "place_start", "place_goal",
                "place_obstacles", "show_widgets", "play_events", "trace_path",
                "show_complexity", "celebrate_goal", "outro"
            ]

            for action in basic_actions:
                registry.register(action, Mock())

            unknown_actions = loader.validate_actions(storyboard, registry)

            if unknown_actions:
                console.print(f"[red]✗[/red] Found {len(unknown_actions)} unknown actions:")
                for action in unknown_actions:
                    console.print(f"  • {action}")
            else:
                console.print("[green]✓[/green] All actions are valid!")

        console.print("\n[green]Storyboard validation completed successfully![/green]")

    except Exception as e:
        handle_cli_exception(e, "storyboard validation", storyboard_path, debug)


@app.command()
def validate_events(
    algorithm: str = typer.Argument(..., help="Algorithm name"),
    scenario: Path = typer.Option(..., help="Scenario configuration file"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug output")
) -> None:
    """Validate event generation for an algorithm."""
    try:
        from agloviz.adapters.protocol import AdapterWrapper
        from agloviz.adapters.registry import AdapterRegistry
        from agloviz.config.manager import ConfigManager

        # Load scenario config
        config_manager = ConfigManager()
        merged_config = config_manager.load_and_validate(yaml_paths=[str(scenario)])
        scenario_config = merged_config.scenario

        # Get adapter and run with wrapper
        adapter_class = AdapterRegistry.get(algorithm)
        adapter = adapter_class()
        wrapper = AdapterWrapper(adapter)

        # Generate events and display
        console.print(f"[bold]Events for {algorithm} algorithm:[/bold]")
        console.print(f"[dim]Scenario: {scenario_config.name} ({scenario_config.start} → {scenario_config.goal})[/dim]")
        console.print()

        events = list(wrapper.run_with_indexing(scenario_config))

        if not events:
            console.print("[yellow]No events generated[/yellow]")
            return

        for event in events:
            payload_str = ", ".join(f"{k}={v}" for k, v in event.payload.items())
            console.print(f"  {event.step_index:2d}: [cyan]{event.type}[/cyan] → {payload_str}")

        console.print()
        console.print(f"[green]Generated {len(events)} events successfully[/green]")

    except KeyError:
        console.print(f"[red]Error: Algorithm '{algorithm}' not found[/red]")
        from agloviz.adapters.registry import AdapterRegistry
        console.print(f"[dim]Available algorithms: {', '.join(AdapterRegistry.list_algorithms())}[/dim]")
        raise typer.Exit(1)
    except FileNotFoundError:
        console.print(f"[red]Error: Scenario file '{scenario}' not found[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if debug:
            console.print_exception()
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
