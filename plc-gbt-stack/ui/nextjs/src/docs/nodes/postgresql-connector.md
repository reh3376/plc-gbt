# PostgreSQL Connector - Industrial Control Node

**Node Type**: `postgresql-connector`  
**Category**: Data Source Nodes  
**Version**: 2.0.0  
**Last Updated**: 2025-01-15

---

Enterprise-grade PostgreSQL database connector with connection pooling, transaction management, and industrial-strength reliability features

## 🎯 Overview

### Purpose
Enterprise-grade PostgreSQL database connector providing reliable, secure, and high-performance database integration for industrial process data management

### Key Features
- **Connection Pooling**:  Efficient resource management with configurable pool sizes
- **Transaction Management**:  ACID compliance with multiple transaction modes
- **Security**:  SSL/TLS encryption, parameterized queries, and SQL injection protection
- **Reliability**:  Automatic reconnection, health monitoring, and retry policies
- **Performance**:  Query optimization, batch processing, and connection reuse
- **Monitoring**:  Comprehensive logging, performance metrics, and health checks

### When to Use This Node
- **Large-scale Data Storage**:  When handling thousands or millions of data points
- **Complex Queries**:  When advanced SQL capabilities are needed for data analysis
- **ACID Compliance**:  When data integrity and consistency are critical
- **Multi-user Access**:  When multiple systems need concurrent database access
- **Enterprise Integration**:  When integrating with existing enterprise database systems

### Industrial Applications
- Manufacturing Execution Systems (MES): Production data and tracking
- SCADA Systems: Real-time and historical data storage
- Laboratory Information Systems (LIMS): Test results and quality data
- Asset Performance Management: Equipment performance and maintenance data
- Energy Management: Power consumption, demand, and optimization data
- Environmental Monitoring: Emissions, waste, and compliance data

## ⚙️ Configuration Guide

### Quick Start
1. Drag PostgreSQL Connector from data sources palette
2. Configure connection string with database credentials and server information
3. Set up connection pooling for your expected load
4. Define your SQL query or connect dynamic query input
5. Configure SSL encryption if required by security policy
6. Test database connectivity using the built-in connection test
7. Set up health monitoring and retry policies for production use
8. Connect output to downstream nodes for data processing

### Detailed Setup

#### Step 1: Database Connection Setup
Configure secure connection to PostgreSQL database server

**Required Parameters:**
- `connectionString`
- `ssl`
- `connectionPool`

**Example Configuration:**
```json
{
  "connectionString": "postgresql://plc_user:secure_pass@192.168.1.100:5432/process_db",
  "ssl": { "enabled": true, "rejectUnauthorized": true },
  "connectionPool": { "min": 5, "max": 20, "idleTimeout": 60000 }
}
```

#### Step 2: Query Configuration
Define SQL queries and execution parameters

**Required Parameters:**
- `defaultQuery`
- `parameterized`
- `queryTimeout`
- `transactionMode`

**Example Configuration:**
```json
{
  "defaultQuery": "SELECT * FROM process_data WHERE timestamp >= $1",
  "parameterized": true,
  "queryTimeout": 30000,
  "transactionMode": "read-only"
}
```

### Best Practices
- ✅ Always use parameterized queries to prevent SQL injection attacks
- ✅ Configure appropriate connection pool sizes based on expected load
- ✅ Enable SSL encryption for production database connections
- ✅ Use read-only transaction mode when only querying data
- ✅ Implement proper error handling and retry policies
- ✅ Monitor connection pool usage and adjust sizes as needed
- ✅ Use database indexes on frequently queried columns

### Common Mistakes to Avoid
- ❌ Hardcoding credentials in connection strings - use secure credential storage
- ❌ Not using connection pooling - leads to performance problems
- ❌ Ignoring SQL injection risks - always use parameterized queries
- ❌ Setting query timeouts too low - may cause premature failures
- ❌ Not handling connection failures - implement proper retry logic
- ❌ Overlooking SSL requirements - may violate security policies

## 📊 Parameters Reference

### Essential Parameters

| Parameter | Type | Default | Range | Units | Description |
|-----------|------|---------|-------|-------|-------------|
| `connectionString` | string | `"postgresql://username:password@localhost:5432/database"` | - | - | PostgreSQL connection string with credentials and database information |

### Advanced Parameters

| Parameter | Type | Default | Description | Notes |
|-----------|------|---------|-------------|-------|
| `connectionPool` | object | `[object Object]` | Connection pooling configuration for optimal performance and resource management | Advanced parameter |
| `ssl` | object | `[object Object]` | SSL/TLS encryption settings for secure database connections | Advanced parameter |
| `defaultQuery` | string | `"SELECT NOW() as current_time"` | Default SQL query to execute when node is triggered | Advanced parameter |
| `queryTimeout` | number | `30000` | Maximum query execution time in milliseconds | Advanced parameter |
| `transactionMode` | enum | `"auto-commit"` | Transaction handling mode for data consistency | Options: auto-commit, manual, read-only, serializable |
| `resultFormat` | enum | `"json"` | Format for query result data output | Options: json, csv, raw |
| `parameterized` | boolean | `true` | Enable parameterized queries for SQL injection protection | Advanced parameter |
| `batchSize` | number | `1000` | Maximum number of rows to process in a single batch | Advanced parameter |
| `healthCheck` | object | `[object Object]` | Database connection health monitoring configuration | Advanced parameter |
| `retryPolicy` | object | `[object Object]` | Automatic retry configuration for failed operations | Advanced parameter |
| `logging` | object | `[object Object]` | Database operation logging and audit trail configuration | Advanced parameter |

### Parameter Validation Rules
- **ERROR**: Invalid connection string format - must use PostgreSQL URI scheme (Use format: postgresql://username:password@host:port/database)
- **WARNING**: Invalid connection pool configuration - maximum must be greater than minimum (Set maximum pool size greater than minimum pool size)
- **WARNING**: Potentially dangerous SQL operation detected (Use caution with destructive SQL operations - consider read-only mode)

## 💡 Examples

### Example 1: Process Historian Data Retrieval

**Use Case**: Historical data analysis for process optimization

Retrieve time-series process data for trending and analysis

```json
{
  "connectionString": "postgresql://historian:hist_pass@192.168.1.100:5432/plant_data",
  "defaultQuery": "\n          SELECT timestamp, tag_name, value, quality \n          FROM process_data \n          WHERE timestamp >= $1 AND timestamp <= $2 \n          ORDER BY timestamp DESC",
  "connectionPool": {
    "min": 5,
    "max": 20,
    "idleTimeout": 60000
  },
  "transactionMode": "read-only",
  "resultFormat": "json",
  "parameterized": true,
  "batchSize": 5000,
  "healthCheck": {
    "enabled": true,
    "interval": 30000
  }
}
```

**Expected Output:**
```
JSON array of time-series data records
```

**Notes:**
- Use parameterized queries with timestamp range for security
- Configure larger connection pool for high-frequency data retrieval
- Enable performance logging to monitor query execution times

### Example 2: Real-time Alarm Logging

**Use Case**: Industrial alarm and event management system

Log process alarms and events to PostgreSQL database

```json
{
  "connectionString": "postgresql://alarm_user:alarm_pass@db.plant.com:5432/alarms",
  "defaultQuery": "\n          INSERT INTO alarm_events (timestamp, alarm_id, severity, description, acknowledged) \n          VALUES ($1, $2, $3, $4, false)",
  "connectionPool": {
    "min": 2,
    "max": 8,
    "idleTimeout": 30000
  },
  "transactionMode": "auto-commit",
  "parameterized": true,
  "ssl": {
    "enabled": true,
    "rejectUnauthorized": true
  },
  "retryPolicy": {
    "maxRetries": 5,
    "backoffMultiplier": 1.5,
    "initialDelay": 500
  },
  "logging": {
    "level": "info",
    "logQueries": true,
    "logPerformance": false
  }
}
```

**Expected Output:**
```
Confirmation of successful alarm record insertion
```

**Notes:**
- Use SSL encryption for sensitive alarm data
- Configure aggressive retry policy for critical alarm logging
- Enable query logging for audit trail compliance

## 🎯 Best Practices

### Configuration
- ✅ **Validate Input Data**: Always verify input data types and ranges before processing
- ✅ **Set Appropriate Timeouts**: Configure reasonable timeout values for industrial networks
- ✅ **Use Meaningful Names**: Give descriptive names to node instances for easy identification
- ✅ **Document Configuration**: Add comments explaining configuration choices
- ✅ **Test in Staging**: Validate configuration in non-production environment first

### Performance
- ✅ **Optimize Polling Intervals**: Balance data freshness with system performance
- ✅ **Monitor Resource Usage**: Track CPU, memory, and network utilization
- ✅ **Use Connection Pooling**: Reuse connections when possible to reduce overhead
- ✅ **Implement Caching**: Cache frequently accessed data to improve response times

### Security
- ✅ **Secure Credentials**: Use secure credential storage, never hardcode passwords
- ✅ **Enable Encryption**: Use encrypted connections when available (TLS/SSL)
- ✅ **Validate Certificates**: Verify SSL certificates in production environments
- ✅ **Implement Rate Limiting**: Protect against excessive requests and abuse

### Maintenance
- ✅ **Regular Updates**: Keep node configurations current with system changes
- ✅ **Monitor Logs**: Regularly review logs for warnings and errors
- ✅ **Backup Configuration**: Maintain backups of working configurations
- ✅ **Plan for Failure**: Implement graceful degradation and error recovery

## 🔧 Troubleshooting

### Common Issues

#### Issue 1: Connection Failed

**Symptoms:**
- Unable to connect to database
- Authentication errors
- Network timeouts

**Possible Causes:**
- Incorrect connection string
- Database server down
- Network connectivity issues
- Authentication failure

**Solutions:**
1. Verify PostgreSQL server is running and accepting connections
2. Check connection string format and credentials
3. Test network connectivity using ping or telnet
4. Verify firewall and security group settings
5. Check PostgreSQL pg_hba.conf authentication configuration



#### Issue 2: Query Performance Issues

**Symptoms:**
- Slow query execution
- Query timeouts
- High CPU usage

**Possible Causes:**
- Missing indexes
- Complex queries
- Large result sets
- Database locks

**Solutions:**
1. Add indexes on frequently queried columns
2. Optimize SQL queries and reduce complexity
3. Implement result pagination for large datasets
4. Monitor and resolve database lock contention
5. Consider query plan analysis and optimization



### Error Codes

| Code | Severity | Message | Solution |
|------|----------|---------|----------|
| `PG_001` | error | Connection timeout | Check network connectivity and database server status |
| `PG_002` | error | Authentication failed | Verify database credentials and user permissions |
| `PG_003` | error | SQL syntax error | Review and correct SQL query syntax |

### Diagnostic Procedures
1. Test database connectivity using external tools (psql, pgAdmin)
2. Monitor connection pool status and resource usage
3. Analyze slow query logs for performance bottlenecks
4. Check PostgreSQL server logs for error messages
5. Verify database permissions and access rights

### Getting Help
- **Documentation**: Check this guide and related node documentation
- **Connection Testing**: Use the built-in connection test feature
- **Log Analysis**: Review node execution logs for detailed error information
- **Community Support**: Search forums and community resources
- **Technical Support**: Contact technical support with error codes and logs

## 🔗 Related Nodes

### Input Nodes
*Nodes that commonly provide input to this node*

### Output Nodes  
*Nodes that commonly receive output from this node*

### Complementary Nodes
*Nodes that work well in combination with this node*

- **csv-dataset-creator**: [Brief description of relationship]
- **data-cleaner**: [Brief description of relationship]
- **dashboard-generator**: [Brief description of relationship]
- **kpi-calculator**: [Brief description of relationship]
- **alarm-handler**: [Brief description of relationship]
- **redis-connector**: [Brief description of relationship]
- **neo4j-connector**: [Brief description of relationship]

### Integration Patterns
- **Sequential Processing**: Connect output to input of compatible nodes
- **Parallel Processing**: Use multiple instances for load distribution
- **Conditional Logic**: Implement branching logic based on node outputs
- **Feedback Loops**: Create closed-loop control systems

## 🔌 API Reference

### Node Interface
```typescript
interface PostgresqlConnectorConfig {
  connectionString: string; // PostgreSQL connection string with credentials and database information
  connectionPool?: Record<string, unknown>; // Connection pooling configuration for optimal performance and resource management
  ssl?: Record<string, unknown>; // SSL/TLS encryption settings for secure database connections
  defaultQuery?: string; // Default SQL query to execute when node is triggered
  queryTimeout?: number; // Maximum query execution time in milliseconds
  transactionMode?: "auto-commit" | "manual" | "read-only" | "serializable"; // Transaction handling mode for data consistency
  resultFormat?: "json" | "csv" | "raw"; // Format for query result data output
  parameterized?: boolean; // Enable parameterized queries for SQL injection protection
  batchSize?: number; // Maximum number of rows to process in a single batch
  healthCheck?: Record<string, unknown>; // Database connection health monitoring configuration
  retryPolicy?: Record<string, unknown>; // Automatic retry configuration for failed operations
  logging?: Record<string, unknown>; // Database operation logging and audit trail configuration
}

class PostgresqlConnectorNode extends IndustrialControlNode {
  config: PostgresqlConnectorConfig;
  
  async initialize(config: PostgresqlConnectorConfig): Promise<void>;
  async process(input: NodeInput): Promise<NodeOutput>;
  async validate(): Promise<ValidationResult>;
  async cleanup(): Promise<void>;
}
```

### Configuration Schema
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "connectionString": {
      "type": "string",
      "description": "PostgreSQL connection string with credentials and database information",
      "default": "postgresql://username:password@localhost:5432/database"
    },
    "connectionPool": {
      "type": "object",
      "description": "Connection pooling configuration for optimal performance and resource management",
      "default": {"min":2,"max":10,"idleTimeout":30000}
    },
    "ssl": {
      "type": "object",
      "description": "SSL/TLS encryption settings for secure database connections",
      "default": {"enabled":false,"rejectUnauthorized":true}
    },
    "defaultQuery": {
      "type": "string",
      "description": "Default SQL query to execute when node is triggered",
      "default": "SELECT NOW() as current_time"
    },
    "queryTimeout": {
      "type": "number",
      "description": "Maximum query execution time in milliseconds",
      "default": 30000
    },
    "transactionMode": {
      "type": "enum",
      "description": "Transaction handling mode for data consistency",
      "default": "auto-commit",
      "enum": ["auto-commit","manual","read-only","serializable"]
    },
    "resultFormat": {
      "type": "enum",
      "description": "Format for query result data output",
      "default": "json",
      "enum": ["json","csv","raw"]
    },
    "parameterized": {
      "type": "boolean",
      "description": "Enable parameterized queries for SQL injection protection",
      "default": true
    },
    "batchSize": {
      "type": "number",
      "description": "Maximum number of rows to process in a single batch",
      "default": 1000
    },
    "healthCheck": {
      "type": "object",
      "description": "Database connection health monitoring configuration",
      "default": {"enabled":true,"interval":60000,"query":"SELECT 1"}
    },
    "retryPolicy": {
      "type": "object",
      "description": "Automatic retry configuration for failed operations",
      "default": {"maxRetries":3,"backoffMultiplier":2,"initialDelay":1000}
    },
    "logging": {
      "type": "object",
      "description": "Database operation logging and audit trail configuration",
      "default": {"level":"info","logQueries":false,"logPerformance":true}
    }
  },
  "required": ["connectionString"]
}
```

### Events
- **`onInitialize`**: Fired when node is initialized
- **`onProcess`**: Fired when node processes input data
- **`onError`**: Fired when an error occurs
- **`onValidationChange`**: Fired when validation status changes
- **`onConfigurationChange`**: Fired when configuration is modified

## 📚 Additional Resources

### External Documentation
- [PostgreSQL Official Documentation](https://www.postgresql.org/docs/) - Comprehensive PostgreSQL documentation and reference
- [PostgreSQL Connection Pooling with pgbouncer](https://pgbouncer.github.io/) - Connection pooling solution for PostgreSQL
- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization) - Performance optimization guides and best practices

### Standards and Specifications
- **Industry Standards**: Review applicable industry standards for this node type
- **Protocol Documentation**: Consult official protocol documentation where applicable
- **Safety Guidelines**: Follow industrial safety guidelines for control system implementation

### Training and Certification
- **Product Training**: Available through official training programs
- **Certification**: Professional certification programs for industrial automation
- **Continuing Education**: Stay current with industry developments and best practices

---

**Document Version**: 2.0.0  
**Last Updated**: 2025-01-15  
**Applies to PLC-GBT Version**: 2.0+  
**Template Category**: data_sources

*This documentation is automatically generated from the node specification. For updates or corrections, please modify the source specification file.*

---

## 📝 Documentation Metadata

- **Node Type ID**: `postgresql-connector`
- **Category**: Data Source Nodes (`data_sources`)
- **Template Extensions**: database-specifics, connection-strings, query-optimization
- **Generated**: 2025-08-21T14:32:20.878Z
- **Documentation System**: PLC-GBT Node Documentation Generator v1.0

*This document follows the [PLC-GBT Documentation Standards](../documentation-standards.md) and is part of the comprehensive node documentation system.*

## 🗄️ Database Integration

### Connection Configuration
```
protocol://username:password@host:port/database?parameters
```

### Query Optimization
*Database-specific optimization techniques and best practices*

### Performance Considerations
*Guidance for optimal database performance in industrial environments*

- **Connection Pooling**: Use connection pools for high-frequency operations
- **Query Optimization**: Index frequently queried columns
- **Batch Operations**: Group operations for better performance
- **Data Retention**: Implement appropriate data retention policies