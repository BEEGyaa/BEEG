import argparse
import json
from pathlib import Path
import sys

# Define default configuration directory
DEFAULT_CONFIG_DIR = Path("path/to/default/config")

def parse_arguments():
    """
    Parses command-line arguments for configuration management.
    """
    parser = argparse.ArgumentParser(description="Load configuration files for the system.")
    parser.add_argument('-f', '--config-folder', nargs='?', const=DEFAULT_CONFIG_DIR, default=None, help='Path to the configuration folder, defaults to the default folder if no path is specified.')
    parser.add_argument('-t', '--top-priority', help='Specify a top-priority configuration file.', required=False)
    parser.add_argument('-p', '--priority-list', nargs='*', help='List of configuration files in order of priority within the specified folder.', required=False)
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output for detailed information during configuration loading.')
    return parser.parse_args()

def merge_configs(existing_configs, new_config, verbose=False):
    """
    Merges new configurations into the existing configuration dictionary.
    """
    for key, value in new_config.items():
        if key in existing_configs:
            if verbose:
                print(f"Conflict for '{key}'. Existing value: {existing_configs[key]}, New value: {value}")
            # Rest of the conflict resolution logic...
        else:
            if verbose:
                print(f"Adding new configuration '{key}': {value}")
            existing_configs[key] = value

    return existing_configs

def load_configs_from_folder(folder_path, verbose=False):
    """
    Recursively loads all JSON configuration files from the specified folder and its subdirectories.
    """
    configs = {}
    folder = Path(folder_path)

    if verbose:
        print(f"Loading configurations from folder: {folder_path}")

    if not folder.is_dir():
        raise ValueError(f"The path {folder_path} is not a valid directory.")

    for file in sorted(folder.rglob("*.json")):
        if verbose:
            print(f"Loading configuration file: {file}")
        with open(file, 'r') as f:
            config = json.load(f)
            configs = merge_configs(configs, config, verbose=verbose)

    return configs

def load_configs_with_priority(folder_path, priority_list, verbose=False):
    """
    Loads configuration files from a specified folder with a given priority list.
    """
    configs = {}
    folder = Path(folder_path)

    # Load priority configs
    for file_name in priority_list:
        file_path = folder / f"{file_name}.json"
        if file_path.is_file():
            if verbose:
                print(f"Loading priority configuration file: {file_name}")
            with open(file_path, 'r') as f:
                config = json.load(f)
                configs = merge_configs(configs, config, verbose)

    # Load remaining configs with lower priority
    return load_configs_from_folder(folder, verbose, exclude=priority_list)

def load_default_or_prompt(verbose=False):
    """
    Attempts to load configurations from the default directory. If not found, prompts the user for an alternative folder.
    """
    if DEFAULT_CONFIG_DIR.exists() and DEFAULT_CONFIG_DIR.is_dir():
        return load_configs_from_folder(DEFAULT_CONFIG_DIR, verbose)
    else:
        print("Default configuration not found.")
        while True:
            user_input = input("Enter a path to the configuration folder, or type 'exit' to quit: ")
            if user_input.lower() == 'exit':
                print("Exiting. Please ensure the default configuration is located at 'path/to/default/config'.")
                sys.exit(1)
            elif Path(user_input).is_dir():
                return load_configs_from_folder(user_input, verbose)
            else:
                print("Invalid path. Please try again or type 'exit' to quit.")

def main():
    """
    Main function to orchestrate the configuration loading process.
    """
    args = parse_arguments()

    if args.config_folder is not None:
        if args.top_priority or args.priority_list:
            priority_list = [args.top_priority] if args.top_priority else []
            priority_list.extend(args.priority_list or [])
            configs = load_configs_with_priority(args.config_folder, priority_list, args.verbose)
        else:
            configs = load_configs_from_folder(args.config_folder, args.verbose)
    else:
        configs = load_default_or_prompt(args.verbose)

    print(configs)  # For demonstration purposes

if __name__ == "__main__":
    main()
