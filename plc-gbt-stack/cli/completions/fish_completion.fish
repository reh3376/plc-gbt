# PLC-GBT Memory System - Fish Completion Script
# Provides context-aware completions for all plc-memory commands and subcommands
# Supports dynamic completion for schema names, instance names, templates, and PLC tags

# Helper functions for dynamic completions
function __plc_memory_schemas
    plc-memory schema list --format=names 2>/dev/null
end

function __plc_memory_instances
    plc-memory instance list --format=names 2>/dev/null
end

function __plc_memory_batch_jobs
    plc-memory batch list --format=names 2>/dev/null
end

function __plc_memory_plc_tags
    plc-memory plc list-tags --format=names 2>/dev/null
end

function __plc_memory_templates
    echo -e "basic\npid-control\ndata-acquisition\nalarm-management\nindustrial-iot"
end

function __plc_memory_databases
    echo -e "redis\nneo4j\npostgresql\nqdrant\nall"
end

function __plc_memory_formats
    echo -e "table\njson\nyaml"
end

function __plc_memory_environments
    echo -e "development\nstaging\nproduction"
end

function __plc_memory_log_levels
    echo -e "debug\ninfo\nwarn\nerror"
end

function __plc_memory_job_statuses
    echo -e "pending\nrunning\ncompleted\nfailed"
end

function __plc_memory_instance_statuses
    echo -e "running\nstopped\nerror"
end

function __plc_memory_priorities
    echo -e "low\nnormal\nhigh"
end

function __plc_memory_data_types
    echo -e "BOOL\nINT\nDINT\nREAL\nSTRING"
end

function __plc_memory_search_types
    echo -e "semantic\nkeyword"
end

function __plc_memory_data_clear_types
    echo -e "cache\ntemp\nall"
end

# Check if we're in a specific subcommand context
function __plc_memory_using_subcommand
    set -l cmd (commandline -xpc)
    if test (count $cmd) -ge 2
        if test $cmd[2] = $argv[1]
            return 0
        end
    end
    return 1
end

function __plc_memory_using_subsubcommand
    set -l cmd (commandline -xpc)
    if test (count $cmd) -ge 3
        if test $cmd[2] = $argv[1]; and test $cmd[3] = $argv[2]
            return 0
        end
    end
    return 1
end

# Main command completions
complete -c plc-memory -f

# Top-level commands
complete -c plc-memory -n "not __fish_seen_subcommand_from schema instance batch plc memory interactive validate monitor backup restore" -a "schema" -d "Schema management operations"
complete -c plc-memory -n "not __fish_seen_subcommand_from schema instance batch plc memory interactive validate monitor backup restore" -a "instance" -d "Instance management operations"
complete -c plc-memory -n "not __fish_seen_subcommand_from schema instance batch plc memory interactive validate monitor backup restore" -a "batch" -d "Batch processing operations"
complete -c plc-memory -n "not __fish_seen_subcommand_from schema instance batch plc memory interactive validate monitor backup restore" -a "plc" -d "PLC integration and control"
complete -c plc-memory -n "not __fish_seen_subcommand_from schema instance batch plc memory interactive validate monitor backup restore" -a "memory" -d "Memory system operations"
complete -c plc-memory -n "not __fish_seen_subcommand_from schema instance batch plc memory interactive validate monitor backup restore" -a "interactive" -d "Interactive REPL mode"
complete -c plc-memory -n "not __fish_seen_subcommand_from schema instance batch plc memory interactive validate monitor backup restore" -a "validate" -d "Validation and testing"
complete -c plc-memory -n "not __fish_seen_subcommand_from schema instance batch plc memory interactive validate monitor backup restore" -a "monitor" -d "System monitoring"
complete -c plc-memory -n "not __fish_seen_subcommand_from schema instance batch plc memory interactive validate monitor backup restore" -a "backup" -d "Data backup operations"
complete -c plc-memory -n "not __fish_seen_subcommand_from schema instance batch plc memory interactive validate monitor backup restore" -a "restore" -d "Data restoration operations"

# Schema subcommands
complete -c plc-memory -n "__plc_memory_using_subcommand schema; and not __fish_seen_subcommand_from create list update delete show validate export import" -a "create" -d "Create a new schema"
complete -c plc-memory -n "__plc_memory_using_subcommand schema; and not __fish_seen_subcommand_from create list update delete show validate export import" -a "list" -d "List all schemas"
complete -c plc-memory -n "__plc_memory_using_subcommand schema; and not __fish_seen_subcommand_from create list update delete show validate export import" -a "update" -d "Update existing schema"
complete -c plc-memory -n "__plc_memory_using_subcommand schema; and not __fish_seen_subcommand_from create list update delete show validate export import" -a "delete" -d "Delete a schema"
complete -c plc-memory -n "__plc_memory_using_subcommand schema; and not __fish_seen_subcommand_from create list update delete show validate export import" -a "show" -d "Show schema details"
complete -c plc-memory -n "__plc_memory_using_subcommand schema; and not __fish_seen_subcommand_from create list update delete show validate export import" -a "validate" -d "Validate schema"
complete -c plc-memory -n "__plc_memory_using_subcommand schema; and not __fish_seen_subcommand_from create list update delete show validate export import" -a "export" -d "Export schema"
complete -c plc-memory -n "__plc_memory_using_subcommand schema; and not __fish_seen_subcommand_from create list update delete show validate export import" -a "import" -d "Import schema"

# Schema create options
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema create" -l name -d "Schema name" -r
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema create" -l description -d "Schema description" -r
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema create" -l template -d "Use template" -xa "(__plc_memory_templates)"
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema create" -l author -d "Author name" -r
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema create" -l version -d "Version" -r
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema create" -l validate -d "Validate after creation"
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema create" -l force -d "Force creation if exists"
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema create" -l help -d "Show help"

# Schema list options
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema list" -l format -d "Output format" -xa "(__plc_memory_formats)"
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema list" -l filter -d "Filter criteria" -r
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema list" -l sort -d "Sort field" -xa "name created_at version"
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema list" -l limit -d "Limit results" -r
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema list" -l help -d "Show help"

# Schema update options
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema update" -a "(__plc_memory_schemas)" -d "Schema name"
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema update" -l description -d "New description" -r
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema update" -l version -d "New version" -r
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema update" -l author -d "New author" -r
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema update" -l validate -d "Validate after update"
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema update" -l help -d "Show help"

# Schema delete options
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema delete" -a "(__plc_memory_schemas)" -d "Schema name"
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema delete" -l force -d "Force deletion"
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema delete" -l cascade -d "Delete dependent instances"
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema delete" -l help -d "Show help"

# Schema show options
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema show" -a "(__plc_memory_schemas)" -d "Schema name"
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema show" -l format -d "Output format" -xa "(__plc_memory_formats)"
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema show" -l detailed -d "Show detailed information"
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema show" -l help -d "Show help"

# Schema validate options
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema validate" -a "(__plc_memory_schemas)" -d "Schema name"
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema validate" -l strict -d "Use strict validation"
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema validate" -l report -d "Generate validation report"
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema validate" -l help -d "Show help"

# Schema export options
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema export" -a "(__plc_memory_schemas)" -d "Schema name"
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema export" -l output -d "Output file" -r
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema export" -l format -d "Export format" -xa "json yaml"
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema export" -l help -d "Show help"

# Schema import options
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema import" -l validate -d "Validate during import"
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema import" -l force -d "Force import if exists"
complete -c plc-memory -n "__plc_memory_using_subsubcommand schema import" -l help -d "Show help"

# Instance subcommands
complete -c plc-memory -n "__plc_memory_using_subcommand instance; and not __fish_seen_subcommand_from create list start stop restart status logs delete" -a "create" -d "Create a new instance"
complete -c plc-memory -n "__plc_memory_using_subcommand instance; and not __fish_seen_subcommand_from create list start stop restart status logs delete" -a "list" -d "List all instances"
complete -c plc-memory -n "__plc_memory_using_subcommand instance; and not __fish_seen_subcommand_from create list start stop restart status logs delete" -a "start" -d "Start an instance"
complete -c plc-memory -n "__plc_memory_using_subcommand instance; and not __fish_seen_subcommand_from create list start stop restart status logs delete" -a "stop" -d "Stop an instance"
complete -c plc-memory -n "__plc_memory_using_subcommand instance; and not __fish_seen_subcommand_from create list start stop restart status logs delete" -a "restart" -d "Restart an instance"
complete -c plc-memory -n "__plc_memory_using_subcommand instance; and not __fish_seen_subcommand_from create list start stop restart status logs delete" -a "status" -d "Show instance status"
complete -c plc-memory -n "__plc_memory_using_subcommand instance; and not __fish_seen_subcommand_from create list start stop restart status logs delete" -a "logs" -d "Show instance logs"
complete -c plc-memory -n "__plc_memory_using_subcommand instance; and not __fish_seen_subcommand_from create list start stop restart status logs delete" -a "delete" -d "Delete an instance"

# Instance create options
complete -c plc-memory -n "__plc_memory_using_subsubcommand instance create" -l name -d "Instance name" -r
complete -c plc-memory -n "__plc_memory_using_subsubcommand instance create" -l schema -d "Schema to use" -xa "(__plc_memory_schemas)"
complete -c plc-memory -n "__plc_memory_using_subsubcommand instance create" -l description -d "Instance description" -r
complete -c plc-memory -n "__plc_memory_using_subsubcommand instance create" -l environment -d "Environment" -xa "(__plc_memory_environments)"
complete -c plc-memory -n "__plc_memory_using_subsubcommand instance create" -l config -d "Configuration file" -r
complete -c plc-memory -n "__plc_memory_using_subsubcommand instance create" -l validate -d "Validate after creation"
complete -c plc-memory -n "__plc_memory_using_subsubcommand instance create" -l start -d "Start instance after creation"
complete -c plc-memory -n "__plc_memory_using_subsubcommand instance create" -l help -d "Show help"

# Instance list options
complete -c plc-memory -n "__plc_memory_using_subsubcommand instance list" -l format -d "Output format" -xa "(__plc_memory_formats)"
complete -c plc-memory -n "__plc_memory_using_subsubcommand instance list" -l filter -d "Filter criteria" -r
complete -c plc-memory -n "__plc_memory_using_subsubcommand instance list" -l status -d "Filter by status" -xa "(__plc_memory_instance_statuses)"
complete -c plc-memory -n "__plc_memory_using_subsubcommand instance list" -l environment -d "Filter by environment" -xa "(__plc_memory_environments)"
complete -c plc-memory -n "__plc_memory_using_subsubcommand instance list" -l help -d "Show help"

# Instance management options
complete -c plc-memory -n "__plc_memory_using_subsubcommand instance start" -a "(__plc_memory_instances)" -d "Instance name"
complete -c plc-memory -n "__plc_memory_using_subsubcommand instance start" -l timeout -d "Startup timeout" -r
complete -c plc-memory -n "__plc_memory_using_subsubcommand instance start" -l force -d "Force start"
complete -c plc-memory -n "__plc_memory_using_subsubcommand instance start" -l help -d "Show help"

complete -c plc-memory -n "__plc_memory_using_subsubcommand instance stop" -a "(__plc_memory_instances)" -d "Instance name"
complete -c plc-memory -n "__plc_memory_using_subsubcommand instance stop" -l timeout -d "Shutdown timeout" -r
complete -c plc-memory -n "__plc_memory_using_subsubcommand instance stop" -l force -d "Force stop"
complete -c plc-memory -n "__plc_memory_using_subsubcommand instance stop" -l help -d "Show help"

complete -c plc-memory -n "__plc_memory_using_subsubcommand instance restart" -a "(__plc_memory_instances)" -d "Instance name"
complete -c plc-memory -n "__plc_memory_using_subsubcommand instance restart" -l timeout -d "Restart timeout" -r
complete -c plc-memory -n "__plc_memory_using_subsubcommand instance restart" -l help -d "Show help"

complete -c plc-memory -n "__plc_memory_using_subsubcommand instance status" -a "(__plc_memory_instances)" -d "Instance name"
complete -c plc-memory -n "__plc_memory_using_subsubcommand instance status" -l detailed -d "Show detailed status"
complete -c plc-memory -n "__plc_memory_using_subsubcommand instance status" -l monitor -d "Continuous monitoring"
complete -c plc-memory -n "__plc_memory_using_subsubcommand instance status" -l help -d "Show help"

complete -c plc-memory -n "__plc_memory_using_subsubcommand instance logs" -a "(__plc_memory_instances)" -d "Instance name"
complete -c plc-memory -n "__plc_memory_using_subsubcommand instance logs" -l lines -d "Number of lines" -r
complete -c plc-memory -n "__plc_memory_using_subsubcommand instance logs" -l follow -d "Follow log output"
complete -c plc-memory -n "__plc_memory_using_subsubcommand instance logs" -l level -d "Log level" -xa "(__plc_memory_log_levels)"
complete -c plc-memory -n "__plc_memory_using_subsubcommand instance logs" -l help -d "Show help"

complete -c plc-memory -n "__plc_memory_using_subsubcommand instance delete" -a "(__plc_memory_instances)" -d "Instance name"
complete -c plc-memory -n "__plc_memory_using_subsubcommand instance delete" -l force -d "Force deletion"
complete -c plc-memory -n "__plc_memory_using_subsubcommand instance delete" -l purge -d "Purge all data"
complete -c plc-memory -n "__plc_memory_using_subsubcommand instance delete" -l help -d "Show help"

# Batch subcommands
complete -c plc-memory -n "__plc_memory_using_subcommand batch; and not __fish_seen_subcommand_from create run list status cancel logs" -a "create" -d "Create a batch job"
complete -c plc-memory -n "__plc_memory_using_subcommand batch; and not __fish_seen_subcommand_from create run list status cancel logs" -a "run" -d "Run a batch job"
complete -c plc-memory -n "__plc_memory_using_subcommand batch; and not __fish_seen_subcommand_from create run list status cancel logs" -a "list" -d "List batch jobs"
complete -c plc-memory -n "__plc_memory_using_subcommand batch; and not __fish_seen_subcommand_from create run list status cancel logs" -a "status" -d "Show job status"
complete -c plc-memory -n "__plc_memory_using_subcommand batch; and not __fish_seen_subcommand_from create run list status cancel logs" -a "cancel" -d "Cancel a job"
complete -c plc-memory -n "__plc_memory_using_subcommand batch; and not __fish_seen_subcommand_from create run list status cancel logs" -a "logs" -d "Show job logs"

# Batch create options
complete -c plc-memory -n "__plc_memory_using_subsubcommand batch create" -l name -d "Batch job name" -r
complete -c plc-memory -n "__plc_memory_using_subsubcommand batch create" -l script -d "Batch script file" -r
complete -c plc-memory -n "__plc_memory_using_subsubcommand batch create" -l config -d "Configuration file" -r
complete -c plc-memory -n "__plc_memory_using_subsubcommand batch create" -l schedule -d "Schedule expression" -r
complete -c plc-memory -n "__plc_memory_using_subsubcommand batch create" -l priority -d "Job priority" -xa "(__plc_memory_priorities)"
complete -c plc-memory -n "__plc_memory_using_subsubcommand batch create" -l help -d "Show help"

# Batch run options
complete -c plc-memory -n "__plc_memory_using_subsubcommand batch run" -a "(__plc_memory_batch_jobs)" -d "Job name"
complete -c plc-memory -n "__plc_memory_using_subsubcommand batch run" -l async -d "Run asynchronously"
complete -c plc-memory -n "__plc_memory_using_subsubcommand batch run" -l timeout -d "Job timeout" -r
complete -c plc-memory -n "__plc_memory_using_subsubcommand batch run" -l help -d "Show help"

# Batch list options
complete -c plc-memory -n "__plc_memory_using_subsubcommand batch list" -l status -d "Filter by status" -xa "(__plc_memory_job_statuses)"
complete -c plc-memory -n "__plc_memory_using_subsubcommand batch list" -l format -d "Output format" -xa "(__plc_memory_formats)"
complete -c plc-memory -n "__plc_memory_using_subsubcommand batch list" -l help -d "Show help"

# Batch status/cancel/logs options
complete -c plc-memory -n "__plc_memory_using_subsubcommand batch status" -a "(__plc_memory_batch_jobs)" -d "Job name"
complete -c plc-memory -n "__plc_memory_using_subsubcommand batch status" -l detailed -d "Show detailed status"
complete -c plc-memory -n "__plc_memory_using_subsubcommand batch status" -l help -d "Show help"

complete -c plc-memory -n "__plc_memory_using_subsubcommand batch cancel" -a "(__plc_memory_batch_jobs)" -d "Job name"
complete -c plc-memory -n "__plc_memory_using_subsubcommand batch cancel" -l force -d "Force cancellation"
complete -c plc-memory -n "__plc_memory_using_subsubcommand batch cancel" -l help -d "Show help"

complete -c plc-memory -n "__plc_memory_using_subsubcommand batch logs" -a "(__plc_memory_batch_jobs)" -d "Job name"
complete -c plc-memory -n "__plc_memory_using_subsubcommand batch logs" -l follow -d "Follow log output"
complete -c plc-memory -n "__plc_memory_using_subsubcommand batch logs" -l lines -d "Number of lines" -r
complete -c plc-memory -n "__plc_memory_using_subsubcommand batch logs" -l help -d "Show help"

# PLC subcommands
complete -c plc-memory -n "__plc_memory_using_subcommand plc; and not __fish_seen_subcommand_from connect read monitor discover status disconnect" -a "connect" -d "Connect to PLC"
complete -c plc-memory -n "__plc_memory_using_subcommand plc; and not __fish_seen_subcommand_from connect read monitor discover status disconnect" -a "read" -d "Read PLC tag values"
complete -c plc-memory -n "__plc_memory_using_subcommand plc; and not __fish_seen_subcommand_from connect read monitor discover status disconnect" -a "monitor" -d "Monitor PLC tags"
complete -c plc-memory -n "__plc_memory_using_subcommand plc; and not __fish_seen_subcommand_from connect read monitor discover status disconnect" -a "discover" -d "Discover PLCs on network"
complete -c plc-memory -n "__plc_memory_using_subcommand plc; and not __fish_seen_subcommand_from connect read monitor discover status disconnect" -a "status" -d "Show PLC connection status"
complete -c plc-memory -n "__plc_memory_using_subcommand plc; and not __fish_seen_subcommand_from connect read monitor discover status disconnect" -a "disconnect" -d "Disconnect from PLC"

# PLC connect options
complete -c plc-memory -n "__plc_memory_using_subsubcommand plc connect" -l host -d "PLC IP address" -r
complete -c plc-memory -n "__plc_memory_using_subsubcommand plc connect" -l slot -d "PLC slot number" -r
complete -c plc-memory -n "__plc_memory_using_subsubcommand plc connect" -l timeout -d "Connection timeout" -r
complete -c plc-memory -n "__plc_memory_using_subsubcommand plc connect" -l readonly -d "Read-only connection"
complete -c plc-memory -n "__plc_memory_using_subsubcommand plc connect" -l help -d "Show help"

# PLC read options
complete -c plc-memory -n "__plc_memory_using_subsubcommand plc read" -l tag -d "Tag name" -xa "(__plc_memory_plc_tags)"
complete -c plc-memory -n "__plc_memory_using_subsubcommand plc read" -l type -d "Data type" -xa "(__plc_memory_data_types)"
complete -c plc-memory -n "__plc_memory_using_subsubcommand plc read" -l format -d "Output format" -xa "value json"
complete -c plc-memory -n "__plc_memory_using_subsubcommand plc read" -l help -d "Show help"

# PLC monitor options
complete -c plc-memory -n "__plc_memory_using_subsubcommand plc monitor" -l tags -d "Tag names" -xa "(__plc_memory_plc_tags)"
complete -c plc-memory -n "__plc_memory_using_subsubcommand plc monitor" -l interval -d "Monitoring interval" -r
complete -c plc-memory -n "__plc_memory_using_subsubcommand plc monitor" -l duration -d "Monitoring duration" -r
complete -c plc-memory -n "__plc_memory_using_subsubcommand plc monitor" -l output -d "Output file" -r
complete -c plc-memory -n "__plc_memory_using_subsubcommand plc monitor" -l help -d "Show help"

# PLC discover options
complete -c plc-memory -n "__plc_memory_using_subsubcommand plc discover" -l subnet -d "Network subnet" -r
complete -c plc-memory -n "__plc_memory_using_subsubcommand plc discover" -l timeout -d "Discovery timeout" -r
complete -c plc-memory -n "__plc_memory_using_subsubcommand plc discover" -l help -d "Show help"

# PLC status options
complete -c plc-memory -n "__plc_memory_using_subsubcommand plc status" -l detailed -d "Show detailed status"
complete -c plc-memory -n "__plc_memory_using_subsubcommand plc status" -l help -d "Show help"

# PLC disconnect options
complete -c plc-memory -n "__plc_memory_using_subsubcommand plc disconnect" -l help -d "Show help"

# Memory subcommands
complete -c plc-memory -n "__plc_memory_using_subcommand memory; and not __fish_seen_subcommand_from status search optimize stats clear" -a "status" -d "Show memory system status"
complete -c plc-memory -n "__plc_memory_using_subcommand memory; and not __fish_seen_subcommand_from status search optimize stats clear" -a "search" -d "Search memory contents"
complete -c plc-memory -n "__plc_memory_using_subcommand memory; and not __fish_seen_subcommand_from status search optimize stats clear" -a "optimize" -d "Optimize memory usage"
complete -c plc-memory -n "__plc_memory_using_subcommand memory; and not __fish_seen_subcommand_from status search optimize stats clear" -a "stats" -d "Show memory statistics"
complete -c plc-memory -n "__plc_memory_using_subcommand memory; and not __fish_seen_subcommand_from status search optimize stats clear" -a "clear" -d "Clear memory data"

# Memory status options
complete -c plc-memory -n "__plc_memory_using_subsubcommand memory status" -l detailed -d "Show detailed status"
complete -c plc-memory -n "__plc_memory_using_subsubcommand memory status" -l format -d "Output format" -xa "(__plc_memory_formats)"
complete -c plc-memory -n "__plc_memory_using_subsubcommand memory status" -l help -d "Show help"

# Memory search options
complete -c plc-memory -n "__plc_memory_using_subsubcommand memory search" -l limit -d "Limit results" -r
complete -c plc-memory -n "__plc_memory_using_subsubcommand memory search" -l type -d "Search type" -xa "(__plc_memory_search_types)"
complete -c plc-memory -n "__plc_memory_using_subsubcommand memory search" -l database -d "Target database" -xa "(__plc_memory_databases)"
complete -c plc-memory -n "__plc_memory_using_subsubcommand memory search" -l help -d "Show help"

# Memory optimize options
complete -c plc-memory -n "__plc_memory_using_subsubcommand memory optimize" -l database -d "Target database" -xa "(__plc_memory_databases)"
complete -c plc-memory -n "__plc_memory_using_subsubcommand memory optimize" -l aggressive -d "Aggressive optimization"
complete -c plc-memory -n "__plc_memory_using_subsubcommand memory optimize" -l help -d "Show help"

# Memory stats options
complete -c plc-memory -n "__plc_memory_using_subsubcommand memory stats" -l database -d "Target database" -xa "(__plc_memory_databases)"
complete -c plc-memory -n "__plc_memory_using_subsubcommand memory stats" -l detailed -d "Show detailed statistics"
complete -c plc-memory -n "__plc_memory_using_subsubcommand memory stats" -l help -d "Show help"

# Memory clear options
complete -c plc-memory -n "__plc_memory_using_subsubcommand memory clear" -l database -d "Target database" -xa "(__plc_memory_databases)"
complete -c plc-memory -n "__plc_memory_using_subsubcommand memory clear" -l type -d "Data type" -xa "(__plc_memory_data_clear_types)"
complete -c plc-memory -n "__plc_memory_using_subsubcommand memory clear" -l force -d "Force clearing"
complete -c plc-memory -n "__plc_memory_using_subsubcommand memory clear" -l help -d "Show help"

# Interactive options
complete -c plc-memory -n "__plc_memory_using_subcommand interactive" -l config -d "Configuration file" -r
complete -c plc-memory -n "__plc_memory_using_subcommand interactive" -l history -d "History file" -r
complete -c plc-memory -n "__plc_memory_using_subcommand interactive" -l no-banner -d "Disable startup banner"
complete -c plc-memory -n "__plc_memory_using_subcommand interactive" -l help -d "Show help"

# Validate subcommands
complete -c plc-memory -n "__plc_memory_using_subcommand validate; and not __fish_seen_subcommand_from system schema instance config" -a "system" -d "Validate entire system"
complete -c plc-memory -n "__plc_memory_using_subcommand validate; and not __fish_seen_subcommand_from system schema instance config" -a "schema" -d "Validate specific schema"
complete -c plc-memory -n "__plc_memory_using_subcommand validate; and not __fish_seen_subcommand_from system schema instance config" -a "instance" -d "Validate specific instance"
complete -c plc-memory -n "__plc_memory_using_subcommand validate; and not __fish_seen_subcommand_from system schema instance config" -a "config" -d "Validate configuration"

# Validate system options
complete -c plc-memory -n "__plc_memory_using_subsubcommand validate system" -l quick -d "Quick validation"
complete -c plc-memory -n "__plc_memory_using_subsubcommand validate system" -l detailed -d "Detailed validation"
complete -c plc-memory -n "__plc_memory_using_subsubcommand validate system" -l report -d "Generate report" -r
complete -c plc-memory -n "__plc_memory_using_subsubcommand validate system" -l help -d "Show help"

# Validate schema options
complete -c plc-memory -n "__plc_memory_using_subsubcommand validate schema" -a "(__plc_memory_schemas)" -d "Schema name"
complete -c plc-memory -n "__plc_memory_using_subsubcommand validate schema" -l strict -d "Strict validation"
complete -c plc-memory -n "__plc_memory_using_subsubcommand validate schema" -l help -d "Show help"

# Validate instance options
complete -c plc-memory -n "__plc_memory_using_subsubcommand validate instance" -a "(__plc_memory_instances)" -d "Instance name"
complete -c plc-memory -n "__plc_memory_using_subsubcommand validate instance" -l deep -d "Deep validation"
complete -c plc-memory -n "__plc_memory_using_subsubcommand validate instance" -l help -d "Show help"

# Validate config options
complete -c plc-memory -n "__plc_memory_using_subsubcommand validate config" -l help -d "Show help"

# Monitor options
complete -c plc-memory -n "__plc_memory_using_subcommand monitor" -l interval -d "Monitoring interval" -r
complete -c plc-memory -n "__plc_memory_using_subcommand monitor" -l duration -d "Monitoring duration" -r
complete -c plc-memory -n "__plc_memory_using_subcommand monitor" -l output -d "Output file" -r
complete -c plc-memory -n "__plc_memory_using_subcommand monitor" -l format -d "Output format" -xa "table json"
complete -c plc-memory -n "__plc_memory_using_subcommand monitor" -l alerts -d "Enable alerts"
complete -c plc-memory -n "__plc_memory_using_subcommand monitor" -l help -d "Show help"

# Backup options
complete -c plc-memory -n "__plc_memory_using_subcommand backup" -l output -d "Backup directory" -r
complete -c plc-memory -n "__plc_memory_using_subcommand backup" -l database -d "Target database" -xa "(__plc_memory_databases)"
complete -c plc-memory -n "__plc_memory_using_subcommand backup" -l compress -d "Compress backup"
complete -c plc-memory -n "__plc_memory_using_subcommand backup" -l incremental -d "Incremental backup"
complete -c plc-memory -n "__plc_memory_using_subcommand backup" -l help -d "Show help"

# Restore options
complete -c plc-memory -n "__plc_memory_using_subcommand restore" -l database -d "Target database" -xa "(__plc_memory_databases)"
complete -c plc-memory -n "__plc_memory_using_subcommand restore" -l force -d "Force restore"
complete -c plc-memory -n "__plc_memory_using_subcommand restore" -l verify -d "Verify after restore"
complete -c plc-memory -n "__plc_memory_using_subcommand restore" -l help -d "Show help"

# Global options (available for all commands)
complete -c plc-memory -l help -d "Show help"
complete -c plc-memory -l version -d "Show version"
complete -c plc-memory -l verbose -d "Verbose output"
complete -c plc-memory -l quiet -d "Quiet output"
complete -c plc-memory -l config -d "Configuration file" -r 