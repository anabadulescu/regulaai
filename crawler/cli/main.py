#!/usr/bin/env python3
"""
RegulaAI CLI - Command Line Interface for GDPR Compliance Scanning
"""

import typer
import json
import os
import sys
from pathlib import Path
from typing import Optional, List
import requests
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text
import yaml

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import get_db, User, Organisation, ApiKey
from sqlalchemy.orm import Session

app = typer.Typer(
    name="regulaai",
    help="RegulaAI CLI - GDPR Compliance Scanning Tool",
    add_completion=False,
    rich_markup_mode="rich"
)

console = Console()

# Configuration
CONFIG_DIR = Path.home() / ".regulaai"
CONFIG_FILE = CONFIG_DIR / "config.json"
API_BASE_URL = os.getenv("REGULAAI_API_URL", "http://localhost:8000")

def get_config():
    """Load configuration from file"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {"api_key": None, "base_url": API_BASE_URL}

def save_config(config):
    """Save configuration to file"""
    CONFIG_DIR.mkdir(exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def get_api_client():
    """Get configured API client"""
    config = get_config()
    api_key = config.get("api_key")
    base_url = config.get("base_url", API_BASE_URL)
    
    if not api_key:
        console.print("[red]No API key configured. Run 'regulaai auth' first.[/red]")
        raise typer.Exit(1)
    
    return base_url, api_key

def make_request(method: str, endpoint: str, data: dict = None, params: dict = None):
    """Make API request with authentication"""
    base_url, api_key = get_api_client()
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key
    }
    
    url = f"{base_url}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        console.print(f"[red]API request failed: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def auth(
    api_key: str = typer.Option(..., "--api-key", "-k", help="Your RegulaAI API key"),
    base_url: str = typer.Option(API_BASE_URL, "--base-url", "-u", help="API base URL")
):
    """Configure authentication for RegulaAI CLI"""
    config = get_config()
    config["api_key"] = api_key
    config["base_url"] = base_url
    save_config(config)
    
    console.print(f"[green]✓ Authentication configured successfully![/green]")
    console.print(f"API Key: {api_key[:8]}...{api_key[-4:]}")
    console.print(f"Base URL: {base_url}")

@app.command()
def scan(
    url: str = typer.Argument(..., help="URL to scan for GDPR compliance"),
    persona: Optional[str] = typer.Option(None, "--persona", "-p", help="Persona to use for scanning"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file (JSON/YAML)"),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, json, yaml")
):
    """Scan a website for GDPR compliance"""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Scanning website...", total=None)
        
        try:
            result = make_request("POST", "/scan", {
                "url": url,
                "persona": persona
            })
            
            progress.update(task, description="Scan completed!")
            
            # Display results
            if format == "table":
                display_scan_results_table(result)
            elif format == "json":
                if output:
                    with open(output, 'w') as f:
                        json.dump(result, f, indent=2)
                    console.print(f"[green]Results saved to {output}[/green]")
                else:
                    console.print_json(data=result)
            elif format == "yaml":
                if output:
                    with open(output, 'w') as f:
                        yaml.dump(result, f, default_flow_style=False)
                    console.print(f"[green]Results saved to {output}[/green]")
                else:
                    console.print(yaml.dump(result, default_flow_style=False))
            
        except Exception as e:
            progress.update(task, description="Scan failed!")
            console.print(f"[red]Scan failed: {e}[/red]")
            raise typer.Exit(1)

def display_scan_results_table(result):
    """Display scan results in a formatted table"""
    # Main results
    main_table = Table(title=f"GDPR Compliance Scan Results - {result['url']}")
    main_table.add_column("Metric", style="cyan")
    main_table.add_column("Value", style="white")
    
    main_table.add_row("Compliance Score", f"{result['score']}%")
    main_table.add_row("Cookie Banner Detected", str(result['cookie_banner_detected']))
    main_table.add_row("Scan Time", f"{result['scan_time_ms']}ms")
    main_table.add_row("Cookies Found", str(len(result['cookies'])))
    main_table.add_row("Violations", str(len(result['violations'])))
    
    console.print(main_table)
    
    # Violations table
    if result['violations']:
        violations_table = Table(title="Violations Found")
        violations_table.add_column("Severity", style="red")
        violations_table.add_column("Title", style="white")
        violations_table.add_column("Description", style="dim")
        
        for violation in result['violations']:
            severity_color = {
                "critical": "red",
                "high": "orange",
                "medium": "yellow",
                "low": "green"
            }.get(violation['severity'], "white")
            
            violations_table.add_row(
                f"[{severity_color}]{violation['severity'].upper()}[/{severity_color}]",
                violation['title'],
                violation['description'][:100] + "..." if len(violation['description']) > 100 else violation['description']
            )
        
        console.print(violations_table)
    
    # Cookies table
    if result['cookies']:
        cookies_table = Table(title="Cookies Found")
        cookies_table.add_column("Name", style="cyan")
        cookies_table.add_column("Domain", style="white")
        cookies_table.add_column("Path", style="dim")
        
        for cookie in result['cookies'][:10]:  # Show first 10 cookies
            cookies_table.add_row(
                cookie['name'],
                cookie['domain'],
                cookie['path']
            )
        
        if len(result['cookies']) > 10:
            cookies_table.add_row("...", f"+{len(result['cookies']) - 10} more", "")
        
        console.print(cookies_table)

@app.command()
def rules(
    command: str = typer.Argument(..., help="Command: list, add"),
    rule_file: Optional[str] = typer.Argument(None, help="Rule file path (for add command)")
):
    """Manage compliance rules"""
    
    if command == "list":
        list_rules()
    elif command == "add":
        if not rule_file:
            console.print("[red]Rule file path is required for 'add' command[/red]")
            raise typer.Exit(1)
        add_rule(rule_file)
    else:
        console.print(f"[red]Unknown command: {command}[/red]")
        raise typer.Exit(1)

def list_rules():
    """List available compliance rules"""
    rules_dir = Path(__file__).parent.parent / "rule_packs"
    
    if not rules_dir.exists():
        console.print("[red]Rules directory not found[/red]")
        raise typer.Exit(1)
    
    table = Table(title="Available Rule Packs")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Rules", style="green")
    
    for rule_file in rules_dir.glob("*.json"):
        if rule_file.name != "schema.json":
            try:
                with open(rule_file, 'r') as f:
                    rules_data = json.load(f)
                
                name = rule_file.stem
                description = rules_data.get("description", "No description")
                rule_count = len(rules_data.get("rules", []))
                
                table.add_row(name, description, str(rule_count))
            except Exception as e:
                table.add_row(rule_file.name, f"Error loading: {e}", "0")
    
    console.print(table)

def add_rule(rule_file: str):
    """Add a new rule pack"""
    rule_path = Path(rule_file)
    
    if not rule_path.exists():
        console.print(f"[red]Rule file not found: {rule_file}[/red]")
        raise typer.Exit(1)
    
    try:
        with open(rule_path, 'r') as f:
            rule_data = json.load(f)
        
        # Validate rule format
        if "rules" not in rule_data:
            console.print("[red]Invalid rule format: missing 'rules' field[/red]")
            raise typer.Exit(1)
        
        # Copy to rule_packs directory
        rules_dir = Path(__file__).parent.parent / "rule_packs"
        rules_dir.mkdir(exist_ok=True)
        
        target_file = rules_dir / f"{rule_path.stem}.json"
        with open(target_file, 'w') as f:
            json.dump(rule_data, f, indent=2)
        
        console.print(f"[green]✓ Rule pack added successfully: {target_file}[/green]")
        console.print(f"Rules: {len(rule_data['rules'])}")
        
    except json.JSONDecodeError:
        console.print("[red]Invalid JSON format[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error adding rule: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def badge(
    site_id: str = typer.Argument(..., help="Site identifier for the badge"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    format: str = typer.Option("svg", "--format", "-f", help="Badge format: svg, png")
):
    """Generate compliance badge for a website"""
    
    try:
        response = requests.get(f"{API_BASE_URL}/badge/{site_id}")
        response.raise_for_status()
        
        badge_content = response.text
        
        if output:
            with open(output, 'w') as f:
                f.write(badge_content)
            console.print(f"[green]✓ Badge saved to {output}[/green]")
        else:
            console.print(badge_content)
            
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Failed to generate badge: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def status():
    """Show CLI status and configuration"""
    config = get_config()
    
    table = Table(title="RegulaAI CLI Status")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")
    
    api_key = config.get("api_key")
    if api_key:
        table.add_row("API Key", f"{api_key[:8]}...{api_key[-4:]}")
    else:
        table.add_row("API Key", "[red]Not configured[/red]")
    
    table.add_row("Base URL", config.get("base_url", API_BASE_URL))
    table.add_row("Config File", str(CONFIG_FILE))
    
    console.print(table)
    
    if not api_key:
        console.print("\n[yellow]To configure authentication, run:[/yellow]")
        console.print("regulaai auth --api-key YOUR_API_KEY")

@app.command()
def version():
    """Show CLI version"""
    from . import __version__
    console.print(f"RegulaAI CLI v{__version__}")

if __name__ == "__main__":
    app() 