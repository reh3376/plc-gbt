#compdef plc-memory

# PLC-GBT Memory System - Zsh Completion Script
# Provides context-aware completions for all plc-memory commands and subcommands
# Supports dynamic completion for schema names, instance names, templates, and PLC tags

# Main completion function
_plc_memory() {
    local context state state_descr line
    typeset -A opt_args

    # Define the main command structure
    _arguments -C \
        '1: :_plc_memory_commands' \
        '*::arg:->args' && return 0

    case $state in
        args)
            case $words[1] in
                schema)
                    _plc_memory_schema_commands
                    ;;
                instance)
                    _plc_memory_instance_commands
                    ;;
                batch)
                    _plc_memory_batch_commands
                    ;;
                plc)
                    _plc_memory_plc_commands
                    ;;
                memory)
                    _plc_memory_memory_commands
                    ;;
                interactive)
                    _plc_memory_interactive_commands
                    ;;
                validate)
                    _plc_memory_validate_commands
                    ;;
                monitor)
                    _plc_memory_monitor_commands
                    ;;
                backup)
                    _plc_memory_backup_commands
                    ;;
                restore)
                    _plc_memory_restore_commands
                    ;;
            esac
            ;;
    esac
}

# Main commands
_plc_memory_commands() {
    local commands=(
        'schema:Schema management operations'
        'instance:Instance management operations'
        'batch:Batch processing operations'
        'plc:PLC integration and control'
        'memory:Memory system operations'
        'interactive:Interactive REPL mode'
        'validate:Validation and testing'
        'monitor:System monitoring'
        'backup:Data backup operations'
        'restore:Data restoration operations'
    )
    _describe 'commands' commands
}

# Schema management completions
_plc_memory_schema_commands() {
    local context state state_descr line
    typeset -A opt_args

    _arguments -C \
        '1: :_plc_memory_schema_subcommands' \
        '*::arg:->args' && return 0

    case $state in
        args)
            case $words[1] in
                create)
                    _arguments \
                        '--name=[Schema name]:name:' \
                        '--description=[Schema description]:description:' \
                        '--template=[Use template]:template:_plc_memory_templates' \
                        '--author=[Author name]:author:' \
                        '--version=[Version]:version:' \
                        '--validate[Validate after creation]' \
                        '--force[Force creation if exists]' \
                        '--help[Show help]'
                    ;;
                list)
                    _arguments \
                        '--format=[Output format]:format:(table json yaml)' \
                        '--filter=[Filter criteria]:filter:' \
                        '--sort=[Sort field]:sort:(name created_at version)' \
                        '--limit=[Limit results]:limit:' \
                        '--help[Show help]'
                    ;;
                update)
                    _arguments \
                        '2:schema:_plc_memory_schemas' \
                        '--description=[New description]:description:' \
                        '--version=[New version]:version:' \
                        '--author=[New author]:author:' \
                        '--validate[Validate after update]' \
                        '--help[Show help]'
                    ;;
                delete)
                    _arguments \
                        '2:schema:_plc_memory_schemas' \
                        '--force[Force deletion]' \
                        '--cascade[Delete dependent instances]' \
                        '--help[Show help]'
                    ;;
                show)
                    _arguments \
                        '2:schema:_plc_memory_schemas' \
                        '--format=[Output format]:format:(table json yaml)' \
                        '--detailed[Show detailed information]' \
                        '--help[Show help]'
                    ;;
                validate)
                    _arguments \
                        '2:schema:_plc_memory_schemas' \
                        '--strict[Use strict validation]' \
                        '--report[Generate validation report]' \
                        '--help[Show help]'
                    ;;
                export)
                    _arguments \
                        '2:schema:_plc_memory_schemas' \
                        '--output=[Output file]:output:_files' \
                        '--format=[Export format]:format:(json yaml)' \
                        '--help[Show help]'
                    ;;
                import)
                    _arguments \
                        '2:file:_files' \
                        '--validate[Validate during import]' \
                        '--force[Force import if exists]' \
                        '--help[Show help]'
                    ;;
            esac
            ;;
    esac
}

_plc_memory_schema_subcommands() {
    local subcommands=(
        'create:Create a new schema'
        'list:List all schemas'
        'update:Update existing schema'
        'delete:Delete a schema'
        'show:Show schema details'
        'validate:Validate schema'
        'export:Export schema'
        'import:Import schema'
    )
    _describe 'schema subcommands' subcommands
}

# Instance management completions
_plc_memory_instance_commands() {
    local context state state_descr line
    typeset -A opt_args

    _arguments -C \
        '1: :_plc_memory_instance_subcommands' \
        '*::arg:->args' && return 0

    case $state in
        args)
            case $words[1] in
                create)
                    _arguments \
                        '--name=[Instance name]:name:' \
                        '--schema=[Schema to use]:schema:_plc_memory_schemas' \
                        '--description=[Instance description]:description:' \
                        '--environment=[Environment]:environment:(development staging production)' \
                        '--config=[Configuration file]:config:_files' \
                        '--validate[Validate after creation]' \
                        '--start[Start instance after creation]' \
                        '--help[Show help]'
                    ;;
                list)
                    _arguments \
                        '--format=[Output format]:format:(table json yaml)' \
                        '--filter=[Filter criteria]:filter:' \
                        '--status=[Filter by status]:status:(running stopped error)' \
                        '--environment=[Filter by environment]:environment:(development staging production)' \
                        '--help[Show help]'
                    ;;
                start)
                    _arguments \
                        '2:instance:_plc_memory_instances' \
                        '--timeout=[Startup timeout]:timeout:' \
                        '--force[Force start]' \
                        '--help[Show help]'
                    ;;
                stop)
                    _arguments \
                        '2:instance:_plc_memory_instances' \
                        '--timeout=[Shutdown timeout]:timeout:' \
                        '--force[Force stop]' \
                        '--help[Show help]'
                    ;;
                restart)
                    _arguments \
                        '2:instance:_plc_memory_instances' \
                        '--timeout=[Restart timeout]:timeout:' \
                        '--help[Show help]'
                    ;;
                status)
                    _arguments \
                        '2:instance:_plc_memory_instances' \
                        '--detailed[Show detailed status]' \
                        '--monitor[Continuous monitoring]' \
                        '--help[Show help]'
                    ;;
                logs)
                    _arguments \
                        '2:instance:_plc_memory_instances' \
                        '--lines=[Number of lines]:lines:' \
                        '--follow[Follow log output]' \
                        '--level=[Log level]:level:(debug info warn error)' \
                        '--help[Show help]'
                    ;;
                delete)
                    _arguments \
                        '2:instance:_plc_memory_instances' \
                        '--force[Force deletion]' \
                        '--purge[Purge all data]' \
                        '--help[Show help]'
                    ;;
            esac
            ;;
    esac
}

_plc_memory_instance_subcommands() {
    local subcommands=(
        'create:Create a new instance'
        'list:List all instances'
        'start:Start an instance'
        'stop:Stop an instance'
        'restart:Restart an instance'
        'status:Show instance status'
        'logs:Show instance logs'
        'delete:Delete an instance'
    )
    _describe 'instance subcommands' subcommands
}

# Batch operations completions
_plc_memory_batch_commands() {
    local context state state_descr line
    typeset -A opt_args

    _arguments -C \
        '1: :_plc_memory_batch_subcommands' \
        '*::arg:->args' && return 0

    case $state in
        args)
            case $words[1] in
                create)
                    _arguments \
                        '--name=[Batch job name]:name:' \
                        '--script=[Batch script file]:script:_files' \
                        '--config=[Configuration file]:config:_files' \
                        '--schedule=[Schedule expression]:schedule:' \
                        '--priority=[Job priority]:priority:(low normal high)' \
                        '--help[Show help]'
                    ;;
                run)
                    _arguments \
                        '2:job:_plc_memory_batch_jobs' \
                        '--async[Run asynchronously]' \
                        '--timeout=[Job timeout]:timeout:' \
                        '--help[Show help]'
                    ;;
                list)
                    _arguments \
                        '--status=[Filter by status]:status:(pending running completed failed)' \
                        '--format=[Output format]:format:(table json yaml)' \
                        '--help[Show help]'
                    ;;
                status)
                    _arguments \
                        '2:job:_plc_memory_batch_jobs' \
                        '--detailed[Show detailed status]' \
                        '--help[Show help]'
                    ;;
                cancel)
                    _arguments \
                        '2:job:_plc_memory_batch_jobs' \
                        '--force[Force cancellation]' \
                        '--help[Show help]'
                    ;;
                logs)
                    _arguments \
                        '2:job:_plc_memory_batch_jobs' \
                        '--follow[Follow log output]' \
                        '--lines=[Number of lines]:lines:' \
                        '--help[Show help]'
                    ;;
            esac
            ;;
    esac
}

_plc_memory_batch_subcommands() {
    local subcommands=(
        'create:Create a batch job'
        'run:Run a batch job'
        'list:List batch jobs'
        'status:Show job status'
        'cancel:Cancel a job'
        'logs:Show job logs'
    )
    _describe 'batch subcommands' subcommands
}

# PLC operations completions
_plc_memory_plc_commands() {
    local context state state_descr line
    typeset -A opt_args

    _arguments -C \
        '1: :_plc_memory_plc_subcommands' \
        '*::arg:->args' && return 0

    case $state in
        args)
            case $words[1] in
                connect)
                    _arguments \
                        '--host=[PLC IP address]:host:' \
                        '--slot=[PLC slot number]:slot:' \
                        '--timeout=[Connection timeout]:timeout:' \
                        '--readonly[Read-only connection]' \
                        '--help[Show help]'
                    ;;
                read)
                    _arguments \
                        '--tag=[Tag name]:tag:_plc_memory_plc_tags' \
                        '--type=[Data type]:type:(BOOL INT DINT REAL STRING)' \
                        '--format=[Output format]:format:(value json)' \
                        '--help[Show help]'
                    ;;
                monitor)
                    _arguments \
                        '--tags=[Tag names]:tags:_plc_memory_plc_tags' \
                        '--interval=[Monitoring interval]:interval:' \
                        '--duration=[Monitoring duration]:duration:' \
                        '--output=[Output file]:output:_files' \
                        '--help[Show help]'
                    ;;
                discover)
                    _arguments \
                        '--subnet=[Network subnet]:subnet:' \
                        '--timeout=[Discovery timeout]:timeout:' \
                        '--help[Show help]'
                    ;;
                status)
                    _arguments \
                        '--detailed[Show detailed status]' \
                        '--help[Show help]'
                    ;;
                disconnect)
                    _arguments \
                        '--help[Show help]'
                    ;;
            esac
            ;;
    esac
}

_plc_memory_plc_subcommands() {
    local subcommands=(
        'connect:Connect to PLC'
        'read:Read PLC tag values'
        'monitor:Monitor PLC tags'
        'discover:Discover PLCs on network'
        'status:Show PLC connection status'
        'disconnect:Disconnect from PLC'
    )
    _describe 'plc subcommands' subcommands
}

# Memory system completions
_plc_memory_memory_commands() {
    local context state state_descr line
    typeset -A opt_args

    _arguments -C \
        '1: :_plc_memory_memory_subcommands' \
        '*::arg:->args' && return 0

    case $state in
        args)
            case $words[1] in
                status)
                    _arguments \
                        '--detailed[Show detailed status]' \
                        '--format=[Output format]:format:(table json yaml)' \
                        '--help[Show help]'
                    ;;
                search)
                    _arguments \
                        '2:query:' \
                        '--limit=[Limit results]:limit:' \
                        '--type=[Search type]:type:(semantic keyword)' \
                        '--database=[Target database]:database:(redis neo4j postgresql qdrant)' \
                        '--help[Show help]'
                    ;;
                optimize)
                    _arguments \
                        '--database=[Target database]:database:(redis neo4j postgresql qdrant all)' \
                        '--aggressive[Aggressive optimization]' \
                        '--help[Show help]'
                    ;;
                stats)
                    _arguments \
                        '--database=[Target database]:database:(redis neo4j postgresql qdrant all)' \
                        '--detailed[Show detailed statistics]' \
                        '--help[Show help]'
                    ;;
                clear)
                    _arguments \
                        '--database=[Target database]:database:(redis neo4j postgresql qdrant all)' \
                        '--type=[Data type]:type:(cache temp all)' \
                        '--force[Force clearing]' \
                        '--help[Show help]'
                    ;;
            esac
            ;;
    esac
}

_plc_memory_memory_subcommands() {
    local subcommands=(
        'status:Show memory system status'
        'search:Search memory contents'
        'optimize:Optimize memory usage'
        'stats:Show memory statistics'
        'clear:Clear memory data'
    )
    _describe 'memory subcommands' subcommands
}

# Interactive mode completions
_plc_memory_interactive_commands() {
    _arguments \
        '--config=[Configuration file]:config:_files' \
        '--history=[History file]:history:_files' \
        '--no-banner[Disable startup banner]' \
        '--help[Show help]'
}

# Validation completions
_plc_memory_validate_commands() {
    local context state state_descr line
    typeset -A opt_args

    _arguments -C \
        '1: :_plc_memory_validate_subcommands' \
        '*::arg:->args' && return 0

    case $state in
        args)
            case $words[1] in
                system)
                    _arguments \
                        '--quick[Quick validation]' \
                        '--detailed[Detailed validation]' \
                        '--report=[Generate report]:report:_files' \
                        '--help[Show help]'
                    ;;
                schema)
                    _arguments \
                        '2:schema:_plc_memory_schemas' \
                        '--strict[Strict validation]' \
                        '--help[Show help]'
                    ;;
                instance)
                    _arguments \
                        '2:instance:_plc_memory_instances' \
                        '--deep[Deep validation]' \
                        '--help[Show help]'
                    ;;
                config)
                    _arguments \
                        '2:config:_files' \
                        '--help[Show help]'
                    ;;
            esac
            ;;
    esac
}

_plc_memory_validate_subcommands() {
    local subcommands=(
        'system:Validate entire system'
        'schema:Validate specific schema'
        'instance:Validate specific instance'
        'config:Validate configuration'
    )
    _describe 'validate subcommands' subcommands
}

# Monitor completions
_plc_memory_monitor_commands() {
    _arguments \
        '--interval=[Monitoring interval]:interval:' \
        '--duration=[Monitoring duration]:duration:' \
        '--output=[Output file]:output:_files' \
        '--format=[Output format]:format:(table json)' \
        '--alerts[Enable alerts]' \
        '--help[Show help]'
}

# Backup completions
_plc_memory_backup_commands() {
    _arguments \
        '--output=[Backup directory]:output:_directories' \
        '--database=[Target database]:database:(redis neo4j postgresql qdrant all)' \
        '--compress[Compress backup]' \
        '--incremental[Incremental backup]' \
        '--help[Show help]'
}

# Restore completions
_plc_memory_restore_commands() {
    _arguments \
        '1:backup:_files' \
        '--database=[Target database]:database:(redis neo4j postgresql qdrant all)' \
        '--force[Force restore]' \
        '--verify[Verify after restore]' \
        '--help[Show help]'
}

# Dynamic completion functions for context-aware completions
_plc_memory_schemas() {
    local schemas
    schemas=($(plc-memory schema list --format=names 2>/dev/null || echo ""))
    if [[ ${#schemas[@]} -gt 0 ]]; then
        _describe 'schemas' schemas
    else
        _message "No schemas available"
    fi
}

_plc_memory_instances() {
    local instances
    instances=($(plc-memory instance list --format=names 2>/dev/null || echo ""))
    if [[ ${#instances[@]} -gt 0 ]]; then
        _describe 'instances' instances
    else
        _message "No instances available"
    fi
}

_plc_memory_templates() {
    local templates=(
        'basic:Basic schema template'
        'pid-control:PID control schema'
        'data-acquisition:Data acquisition schema'
        'alarm-management:Alarm management schema'
        'industrial-iot:Industrial IoT schema'
    )
    _describe 'templates' templates
}

_plc_memory_batch_jobs() {
    local jobs
    jobs=($(plc-memory batch list --format=names 2>/dev/null || echo ""))
    if [[ ${#jobs[@]} -gt 0 ]]; then
        _describe 'batch jobs' jobs
    else
        _message "No batch jobs available"
    fi
}

_plc_memory_plc_tags() {
    local tags
    tags=($(plc-memory plc list-tags --format=names 2>/dev/null || echo ""))
    if [[ ${#tags[@]} -gt 0 ]]; then
        _describe 'PLC tags' tags
    else
        _message "No PLC tags available (not connected?)"
    fi
}

# Directory completion function
_directories() {
    _path_files -/
}

# Initialize completion
_plc_memory "$@" 