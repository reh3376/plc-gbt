#!/bin/bash
# ⚡ Phase 21.5: Bash Shell Completion for PLC Control Loop CLI
#
# AI Task Orchestrator Implementation
# =====================================
# Task Classification: MODERATE (Shell completion framework)
# Context Management: Dynamic completion with command context awareness
# Methodology Source: AI_TASK_ORCHESTRATOR_GUIDE.md
#
# Phase 21.5 Objectives:
# - Context-aware command completion
# - Schema and instance name completion
# - Option and argument completion
# - Installation and setup automation
#
# Author: AI Task Orchestrator
# Created: 2025-01-18
# Phase: 21.5.3 - Shell Completions
# Dependencies: bash-completion package

# Main completion function for plc-cl
_plc_cl_completion() {
    local cur prev words cword opts
    _init_completion || return

    # Get the CLI command path
    local cli_cmd="${COMP_WORDS[0]}"
    
    # Handle global options first
    case "$prev" in
        --config-dir)
            _filedir -d
            return 0
            ;;
        --format)
            COMPREPLY=($(compgen -W "table json yaml csv" -- "$cur"))
            return 0
            ;;
        --log-file)
            _filedir
            return 0
            ;;
    esac

    # Parse command structure
    local command=""
    local subcommand=""
    local i=1
    
    while [[ $i -lt $cword ]]; do
        case "${words[$i]}" in
            -*)
                # Skip options and their values
                case "${words[$i]}" in
                    --config-dir|--format|--log-file)
                        ((i++))  # Skip option value
                        ;;
                esac
                ;;
            *)
                if [[ -z "$command" ]]; then
                    command="${words[$i]}"
                elif [[ -z "$subcommand" ]]; then
                    subcommand="${words[$i]}"
                    break
                fi
                ;;
        esac
        ((i++))
    done

    # Global options
    local global_opts="--version --help --config-dir --verbose --quiet --format --no-color --log-file --debug"

    # Main commands
    local main_commands="status config help schema instance batch repl"

    # If no command yet, complete main commands and global options
    if [[ -z "$command" ]]; then
        COMPREPLY=($(compgen -W "$main_commands $global_opts" -- "$cur"))
        return 0
    fi

    # Command-specific completions
    case "$command" in
        schema)
            _plc_cl_schema_completion
            ;;
        instance)
            _plc_cl_instance_completion
            ;;
        batch)
            _plc_cl_batch_completion
            ;;
        config)
            _plc_cl_config_completion
            ;;
        repl)
            _plc_cl_repl_completion
            ;;
        status)
            _plc_cl_status_completion
            ;;
        help)
            COMPREPLY=($(compgen -W "$main_commands" -- "$cur"))
            ;;
    esac
}

# Schema command completions
_plc_cl_schema_completion() {
    local subcommands="list info create modify validate test wizard"
    
    if [[ -z "$subcommand" ]]; then
        COMPREPLY=($(compgen -W "$subcommands --help" -- "$cur"))
        return 0
    fi

    case "$subcommand" in
        list)
            case "$prev" in
                --type)
                    COMPREPLY=($(compgen -W "basic_pid cascade adaptive mpc custom" -- "$cur"))
                    ;;
                --status)
                    COMPREPLY=($(compgen -W "active deprecated draft" -- "$cur"))
                    ;;
                --sort-by)
                    COMPREPLY=($(compgen -W "name type version modified" -- "$cur"))
                    ;;
                *)
                    local opts="--type --status --search --sort-by --reverse --detailed --limit --offset"
                    COMPREPLY=($(compgen -W "$opts" -- "$cur"))
                    ;;
            esac
            ;;
        info|modify|validate|test)
            if [[ "$prev" == "$subcommand" ]]; then
                # Complete schema names
                _plc_cl_complete_schema_names
            else
                case "$subcommand" in
                    info)
                        local opts="--show-properties --show-validation --show-examples --export --output-file"
                        ;;
                    modify)
                        local opts="--description --add-property --remove-property --update-validation --increment-version --validate"
                        ;;
                    validate)
                        local opts="--strict --report-file --fix-issues"
                        ;;
                    test)
                        local opts="--instance-file --generate-examples --example-count"
                        ;;
                esac
                case "$prev" in
                    --export)
                        COMPREPLY=($(compgen -W "json yaml" -- "$cur"))
                        ;;
                    --increment-version)
                        COMPREPLY=($(compgen -W "major minor patch" -- "$cur"))
                        ;;
                    --output-file|--report-file|--instance-file)
                        _filedir
                        ;;
                    *)
                        COMPREPLY=($(compgen -W "$opts" -- "$cur"))
                        ;;
                esac
            fi
            ;;
        create)
            case "$prev" in
                --type)
                    COMPREPLY=($(compgen -W "basic_pid cascade adaptive mpc custom" -- "$cur"))
                    ;;
                --template)
                    _plc_cl_complete_template_names
                    ;;
                --properties-file)
                    _filedir
                    ;;
                *)
                    local opts="--name --type --description --version --author --template --interactive --properties-file --validate"
                    COMPREPLY=($(compgen -W "$opts" -- "$cur"))
                    ;;
            esac
            ;;
        wizard)
            local opts="--interactive"
            COMPREPLY=($(compgen -W "$opts" -- "$cur"))
            ;;
    esac
}

# Instance command completions
_plc_cl_instance_completion() {
    local subcommands="list info create edit validate simulate export import convert plc"
    
    if [[ -z "$subcommand" ]]; then
        COMPREPLY=($(compgen -W "$subcommands --help" -- "$cur"))
        return 0
    fi

    case "$subcommand" in
        list)
            case "$prev" in
                --schema)
                    _plc_cl_complete_schema_names
                    ;;
                --status)
                    COMPREPLY=($(compgen -W "active inactive error" -- "$cur"))
                    ;;
                --group-by)
                    COMPREPLY=($(compgen -W "schema status created" -- "$cur"))
                    ;;
                *)
                    local opts="--schema --status --group-by --show-config --show-status"
                    COMPREPLY=($(compgen -W "$opts" -- "$cur"))
                    ;;
            esac
            ;;
        info|edit|validate|simulate|export)
            if [[ "$prev" == "$subcommand" ]]; then
                _plc_cl_complete_instance_names
            else
                case "$subcommand" in
                    info)
                        local opts="--show-config --show-history --show-validation"
                        ;;
                    edit)
                        local opts="--interactive --config-file --validate --kp --ki --kd --setpoint"
                        ;;
                    validate)
                        local opts="--strict --plc-verify --plc-host"
                        ;;
                    simulate)
                        local opts="--duration --input-file --output-file --real-time"
                        ;;
                    export)
                        local opts="--format --output-file"
                        ;;
                esac
                case "$prev" in
                    --format)
                        COMPREPLY=($(compgen -W "json yaml csv" -- "$cur"))
                        ;;
                    --config-file|--input-file|--output-file)
                        _filedir
                        ;;
                    *)
                        COMPREPLY=($(compgen -W "$opts" -- "$cur"))
                        ;;
                esac
            fi
            ;;
        create)
            case "$prev" in
                --schema)
                    _plc_cl_complete_schema_names
                    ;;
                --config-file)
                    _filedir
                    ;;
                *)
                    local opts="--schema --name --description --config-file --wizard --validate --kp --ki --kd --setpoint --output-min --output-max"
                    COMPREPLY=($(compgen -W "$opts" -- "$cur"))
                    ;;
            esac
            ;;
        import|convert)
            if [[ "$prev" == "$subcommand" ]]; then
                _filedir
            else
                case "$prev" in
                    --output-format)
                        COMPREPLY=($(compgen -W "json yaml csv" -- "$cur"))
                        ;;
                    --output-file)
                        _filedir
                        ;;
                    *)
                        local opts="--output-format --output-file --validate"
                        COMPREPLY=($(compgen -W "$opts" -- "$cur"))
                        ;;
                esac
            fi
            ;;
        plc)
            _plc_cl_plc_completion
            ;;
    esac
}

# PLC command completions
_plc_cl_plc_completion() {
    local plc_subcommands="connect disconnect status browse read read-batch monitor tag-info"
    
    # Get PLC subcommand
    local plc_subcommand=""
    local j=$((cword - 1))
    while [[ $j -gt 0 ]]; do
        if [[ "${words[$j]}" == "plc" ]]; then
            if [[ $((j + 1)) -lt $cword ]]; then
                plc_subcommand="${words[$((j + 1))]}"
            fi
            break
        fi
        ((j--))
    done

    if [[ -z "$plc_subcommand" ]]; then
        COMPREPLY=($(compgen -W "$plc_subcommands" -- "$cur"))
        return 0
    fi

    case "$plc_subcommand" in
        connect)
            case "$prev" in
                --host)
                    # Could add known PLC IPs here
                    COMPREPLY=()
                    ;;
                --slot)
                    COMPREPLY=($(compgen -W "0 1 2 3" -- "$cur"))
                    ;;
                *)
                    local opts="--host --slot --timeout --verify"
                    COMPREPLY=($(compgen -W "$opts" -- "$cur"))
                    ;;
            esac
            ;;
        browse)
            case "$prev" in
                --type)
                    COMPREPLY=($(compgen -W "BOOL SINT INT DINT REAL STRING" -- "$cur"))
                    ;;
                *)
                    local opts="--filter --type --program --limit --tree-view"
                    COMPREPLY=($(compgen -W "$opts" -- "$cur"))
                    ;;
            esac
            ;;
        read|tag-info)
            if [[ "$prev" == "$plc_subcommand" ]]; then
                # Complete PLC tag names (would require PLC connection)
                COMPREPLY=()
            else
                case "$prev" in
                    --format)
                        COMPREPLY=($(compgen -W "value detailed json" -- "$cur"))
                        ;;
                    *)
                        local opts="--format --timestamp --quality"
                        COMPREPLY=($(compgen -W "$opts" -- "$cur"))
                        ;;
                esac
            fi
            ;;
        read-batch)
            case "$prev" in
                --tags|--output-file)
                    _filedir
                    ;;
                *)
                    local opts="--tags --tag-list --output-file --interval --count"
                    COMPREPLY=($(compgen -W "$opts" -- "$cur"))
                    ;;
            esac
            ;;
        monitor)
            if [[ "$prev" == "$plc_subcommand" ]]; then
                # Complete PLC tag names
                COMPREPLY=()
            else
                case "$prev" in
                    --output-file)
                        _filedir
                        ;;
                    *)
                        local opts="--interval --duration --output-file --alarm-high --alarm-low"
                        COMPREPLY=($(compgen -W "$opts" -- "$cur"))
                        ;;
                esac
            fi
            ;;
        status|disconnect)
            COMPREPLY=()
            ;;
    esac
}

# Batch command completions
_plc_cl_batch_completion() {
    local subcommands="create validate export import convert"
    
    if [[ -z "$subcommand" ]]; then
        COMPREPLY=($(compgen -W "$subcommands --help" -- "$cur"))
        return 0
    fi

    case "$subcommand" in
        create)
            case "$prev" in
                --from-csv|--from-json)
                    _filedir
                    ;;
                --template)
                    _plc_cl_complete_template_names
                    ;;
                *)
                    local opts="--from-csv --from-json --template --count --prefix --parallel --continue-on-error --dry-run"
                    COMPREPLY=($(compgen -W "$opts" -- "$cur"))
                    ;;
            esac
            ;;
        validate)
            case "$prev" in
                --directory)
                    _filedir -d
                    ;;
                --report-file)
                    _filedir
                    ;;
                --report-format)
                    COMPREPLY=($(compgen -W "json html csv" -- "$cur"))
                    ;;
                *)
                    local opts="--pattern --directory --files --report-file --report-format"
                    COMPREPLY=($(compgen -W "$opts" -- "$cur"))
                    ;;
            esac
            ;;
        export)
            case "$prev" in
                --schema)
                    _plc_cl_complete_schema_names
                    ;;
                --output-dir)
                    _filedir -d
                    ;;
                --output-format)
                    COMPREPLY=($(compgen -W "json yaml csv" -- "$cur"))
                    ;;
                *)
                    local opts="--all --pattern --schema --output-dir --output-format --compress"
                    COMPREPLY=($(compgen -W "$opts" -- "$cur"))
                    ;;
            esac
            ;;
        import)
            case "$prev" in
                --input-dir)
                    _filedir -d
                    ;;
                *)
                    local opts="--input-dir --overwrite-existing --validate --parallel"
                    COMPREPLY=($(compgen -W "$opts" -- "$cur"))
                    ;;
            esac
            ;;
        convert)
            case "$prev" in
                --output-format)
                    COMPREPLY=($(compgen -W "json yaml csv" -- "$cur"))
                    ;;
                --output-dir)
                    _filedir -d
                    ;;
                *)
                    local opts="--pattern --output-format --output-dir --parallel"
                    COMPREPLY=($(compgen -W "$opts" -- "$cur"))
                    ;;
            esac
            ;;
    esac
}

# Config command completions
_plc_cl_config_completion() {
    local subcommands="show set reset export import"
    
    if [[ -z "$subcommand" ]]; then
        COMPREPLY=($(compgen -W "$subcommands --help" -- "$cur"))
        return 0
    fi

    case "$subcommand" in
        show)
            local opts="--section --format"
            case "$prev" in
                --section)
                    COMPREPLY=($(compgen -W "cli schema instance plc memory batch auth" -- "$cur"))
                    ;;
                --format)
                    COMPREPLY=($(compgen -W "table json yaml" -- "$cur"))
                    ;;
                *)
                    COMPREPLY=($(compgen -W "$opts" -- "$cur"))
                    ;;
            esac
            ;;
        set)
            if [[ $cword -eq $((${#words[@]} - 2)) ]]; then
                # Complete configuration keys
                local config_keys="output_format color_output verbose schema_registry instance_directory plc_timeout memory_enabled"
                COMPREPLY=($(compgen -W "$config_keys" -- "$cur"))
            elif [[ $cword -eq $((${#words[@]} - 1)) ]]; then
                # Complete values based on previous key
                case "$prev" in
                    output_format)
                        COMPREPLY=($(compgen -W "table json yaml csv" -- "$cur"))
                        ;;
                    color_output|verbose|memory_enabled)
                        COMPREPLY=($(compgen -W "true false" -- "$cur"))
                        ;;
                    schema_registry|instance_directory)
                        _filedir -d
                        ;;
                    *)
                        COMPREPLY=()
                        ;;
                esac
            fi
            ;;
        reset)
            case "$prev" in
                --section)
                    COMPREPLY=($(compgen -W "cli schema instance plc memory batch auth" -- "$cur"))
                    ;;
                *)
                    local opts="--section --confirm"
                    COMPREPLY=($(compgen -W "$opts" -- "$cur"))
                    ;;
            esac
            ;;
        export|import)
            case "$prev" in
                --file)
                    _filedir
                    ;;
                *)
                    local opts="--file"
                    COMPREPLY=($(compgen -W "$opts" -- "$cur"))
                    ;;
            esac
            ;;
    esac
}

# REPL command completions
_plc_cl_repl_completion() {
    local opts="--verbose --save-session --load-session"
    
    case "$prev" in
        --load-session)
            _filedir
            ;;
        *)
            COMPREPLY=($(compgen -W "$opts" -- "$cur"))
            ;;
    esac
}

# Status command completions
_plc_cl_status_completion() {
    local opts="--detailed --format"
    
    case "$prev" in
        --format)
            COMPREPLY=($(compgen -W "table json" -- "$cur"))
            ;;
        *)
            COMPREPLY=($(compgen -W "$opts" -- "$cur"))
            ;;
    esac
}

# Helper functions for dynamic completions
_plc_cl_complete_schema_names() {
    local schemas
    if command -v "$cli_cmd" >/dev/null 2>&1; then
        schemas=$("$cli_cmd" schema list --format=json 2>/dev/null | grep -o '"schema_id": "[^"]*"' | cut -d'"' -f4)
        COMPREPLY=($(compgen -W "$schemas" -- "$cur"))
    else
        COMPREPLY=()
    fi
}

_plc_cl_complete_instance_names() {
    local instances
    if command -v "$cli_cmd" >/dev/null 2>&1; then
        instances=$("$cli_cmd" instance list --format=json 2>/dev/null | grep -o '"name": "[^"]*"' | cut -d'"' -f4)
        COMPREPLY=($(compgen -W "$instances" -- "$cur"))
    else
        COMPREPLY=()
    fi
}

_plc_cl_complete_template_names() {
    # Complete template names (would need template registry)
    local templates="standard-pid cascade-basic adaptive-simple mpc-basic"
    COMPREPLY=($(compgen -W "$templates" -- "$cur"))
}

# Register the completion function
complete -F _plc_cl_completion plc-cl

# Also register for common variations
complete -F _plc_cl_completion ./plc-cl
complete -F _plc_cl_completion /usr/local/bin/plc-cl 