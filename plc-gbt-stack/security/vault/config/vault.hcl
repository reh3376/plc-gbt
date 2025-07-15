ui = true
disable_mlock = true

storage "file" {
  path = "/vault/data"
}

listener "tcp" {
  address = "0.0.0.0:8200"
  tls_disable = 1
}

api_addr = "http://127.0.0.1:8200"
cluster_addr = "http://127.0.0.1:8201"

# Enable audit logging
audit {
  file {
    file_path = "/vault/logs/audit.log"
    log_raw = false
    format = "json"
  }
}

# Default lease TTL
default_lease_ttl = "168h"  # 7 days
max_lease_ttl = "720h"      # 30 days

# Enable secret engines
path "secret/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "database/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "pki/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# System health
path "sys/health" {
  capabilities = ["read"]
}

# Authentication methods
path "auth/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
} 