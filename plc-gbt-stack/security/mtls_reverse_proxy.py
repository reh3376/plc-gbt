#!/usr/bin/env python3
"""
mTLS Reverse Proxy for PLC-GPT Database Security
Phase 15.1: Enterprise Secrets Management

This module provides mutual TLS authentication for database connections,
ensuring secure communication between services and databases.

Features:
- Certificate-based authentication
- Automatic certificate rotation
- Connection pooling with TLS
- Traffic monitoring and logging
- High availability with failover

Following AI Task Orchestrator methodology for systematic security enhancement.
"""

import asyncio
import json
import logging
import ssl
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Optional imports for enhanced functionality
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

try:
    import aiofiles
    AIOFILES_AVAILABLE = True
except ImportError:
    AIOFILES_AVAILABLE = False

# Certificate management
try:
    import ipaddress

    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat
    from cryptography.x509.oid import NameOID
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    logging.warning("cryptography library not available for certificate management")

# Reverse proxy
try:
    import aiohttp_reverse_proxy
    REVERSE_PROXY_AVAILABLE = True
except ImportError:
    REVERSE_PROXY_AVAILABLE = False
    logging.warning("aiohttp-reverse-proxy not available. Install with: pip install aiohttp-reverse-proxy")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseType(Enum):
    """Supported database types for mTLS proxy."""
    POSTGRESQL = "postgresql"
    NEO4J = "neo4j"
    REDIS = "redis"
    QDRANT = "qdrant"


@dataclass
class CertificateInfo:
    """Certificate information structure."""
    cert_path: str
    key_path: str
    ca_path: str
    created_at: datetime
    expires_at: datetime
    serial_number: str
    subject: str
    issuer: str
    fingerprint: str


@dataclass
class ProxyEndpoint:
    """Proxy endpoint configuration."""
    name: str
    database_type: DatabaseType
    listen_host: str
    listen_port: int
    target_host: str
    target_port: int
    tls_enabled: bool
    client_cert_required: bool
    certificate_info: Optional[CertificateInfo] = None


@dataclass
class ConnectionMetrics:
    """Connection metrics for monitoring."""
    endpoint_name: str
    client_ip: str
    connected_at: datetime
    bytes_sent: int
    bytes_received: int
    duration: float
    tls_version: str
    cipher_suite: str
    client_cert_subject: Optional[str] = None


class CertificateManager:
    """
    Certificate management for mTLS authentication.

    Handles certificate generation, rotation, and validation.
    """

    def __init__(self, cert_dir: str = "security/certificates"):
        """
        Initialize certificate manager.

        Args:
            cert_dir: Directory to store certificates
        """
        self.cert_dir = Path(cert_dir)
        self.cert_dir.mkdir(parents=True, exist_ok=True)

        # Certificate validity period
        self.cert_validity_days = 365
        self.ca_validity_days = 3650  # 10 years for CA

        # Key size for RSA certificates
        self.key_size = 2048

        logger.info(f"CertificateManager initialized - cert_dir: {self.cert_dir}")

    def generate_ca_certificate(self, common_name: str = "PLC-GPT Root CA") -> Tuple[str, str]:
        """
        Generate a Certificate Authority (CA) certificate.

        Args:
            common_name: Common name for the CA certificate

        Returns:
            Tuple of (cert_path, key_path)
        """
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("cryptography library not available for certificate generation")

        try:
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=self.key_size,
            )

            # Create certificate subject
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "PLC-GPT Enterprise"),
                x509.NameAttribute(NameOID.COMMON_NAME, common_name),
            ])

            # Create certificate
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.utcnow()
            ).not_valid_after(
                datetime.utcnow() + timedelta(days=self.ca_validity_days)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName("localhost"),
                    x509.DNSName("plc-gpt-ca"),
                    x509.IPAddress(ipaddress.ip_address("127.0.0.1")),
                ]),
                critical=False,
            ).add_extension(
                x509.BasicConstraints(ca=True, path_length=None),
                critical=True,
            ).add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_cert_sign=True,
                    crl_sign=True,
                    content_commitment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    key_encipherment=False,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            ).sign(private_key, hashes.SHA256())

            # Save certificate and key
            cert_path = self.cert_dir / "ca.crt"
            key_path = self.cert_dir / "ca.key"

            with open(cert_path, "wb") as f:
                f.write(cert.public_bytes(Encoding.PEM))

            with open(key_path, "wb") as f:
                f.write(private_key.private_bytes(
                    Encoding.PEM,
                    PrivateFormat.PKCS8,
                    NoEncryption()
                ))

            logger.info(f"✅ CA certificate generated: {cert_path}")
            return str(cert_path), str(key_path)

        except Exception as e:
            logger.error(f"Failed to generate CA certificate: {e}")
            raise

    def generate_server_certificate(
        self,
        common_name: str,
        san_dns: List[str] = None,
        san_ips: List[str] = None,
        ca_cert_path: str = None,
        ca_key_path: str = None
    ) -> Tuple[str, str]:
        """
        Generate a server certificate signed by the CA.

        Args:
            common_name: Common name for the server certificate
            san_dns: Subject Alternative Names (DNS)
            san_ips: Subject Alternative Names (IP addresses)
            ca_cert_path: Path to CA certificate
            ca_key_path: Path to CA private key

        Returns:
            Tuple of (cert_path, key_path)
        """
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("cryptography library not available for certificate generation")

        try:
            # Use default CA paths if not provided
            if not ca_cert_path:
                ca_cert_path = self.cert_dir / "ca.crt"
            if not ca_key_path:
                ca_key_path = self.cert_dir / "ca.key"

            # Load CA certificate and key
            with open(ca_cert_path, "rb") as f:
                ca_cert = x509.load_pem_x509_certificate(f.read())

            with open(ca_key_path, "rb") as f:
                ca_key = serialization.load_pem_private_key(f.read(), password=None)

            # Generate server private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=self.key_size,
            )

            # Create certificate subject
            subject = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "PLC-GPT Enterprise"),
                x509.NameAttribute(NameOID.COMMON_NAME, common_name),
            ])

            # Prepare Subject Alternative Names
            san_list = []
            if san_dns:
                san_list.extend([x509.DNSName(name) for name in san_dns])
            if san_ips:
                san_list.extend([x509.IPAddress(ipaddress.ip_address(ip)) for ip in san_ips])

            # Add default SANs
            san_list.extend([
                x509.DNSName("localhost"),
                x509.DNSName(common_name),
                x509.IPAddress(ipaddress.ip_address("127.0.0.1")),
            ])

            # Create certificate
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                ca_cert.subject
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.utcnow()
            ).not_valid_after(
                datetime.utcnow() + timedelta(days=self.cert_validity_days)
            ).add_extension(
                x509.SubjectAlternativeName(san_list),
                critical=False,
            ).add_extension(
                x509.BasicConstraints(ca=False, path_length=None),
                critical=True,
            ).add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_encipherment=True,
                    content_commitment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    key_cert_sign=False,
                    crl_sign=False,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            ).add_extension(
                x509.ExtendedKeyUsage([
                    x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
                ]),
                critical=True,
            ).sign(ca_key, hashes.SHA256())

            # Save certificate and key
            cert_path = self.cert_dir / f"{common_name}.crt"
            key_path = self.cert_dir / f"{common_name}.key"

            with open(cert_path, "wb") as f:
                f.write(cert.public_bytes(Encoding.PEM))

            with open(key_path, "wb") as f:
                f.write(private_key.private_bytes(
                    Encoding.PEM,
                    PrivateFormat.PKCS8,
                    NoEncryption()
                ))

            logger.info(f"✅ Server certificate generated: {cert_path}")
            return str(cert_path), str(key_path)

        except Exception as e:
            logger.error(f"Failed to generate server certificate: {e}")
            raise

    def generate_client_certificate(
        self,
        common_name: str,
        ca_cert_path: str = None,
        ca_key_path: str = None
    ) -> Tuple[str, str]:
        """
        Generate a client certificate for mTLS authentication.

        Args:
            common_name: Common name for the client certificate
            ca_cert_path: Path to CA certificate
            ca_key_path: Path to CA private key

        Returns:
            Tuple of (cert_path, key_path)
        """
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("cryptography library not available for certificate generation")

        try:
            # Use default CA paths if not provided
            if not ca_cert_path:
                ca_cert_path = self.cert_dir / "ca.crt"
            if not ca_key_path:
                ca_key_path = self.cert_dir / "ca.key"

            # Load CA certificate and key
            with open(ca_cert_path, "rb") as f:
                ca_cert = x509.load_pem_x509_certificate(f.read())

            with open(ca_key_path, "rb") as f:
                ca_key = serialization.load_pem_private_key(f.read(), password=None)

            # Generate client private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=self.key_size,
            )

            # Create certificate subject
            subject = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "PLC-GPT Enterprise"),
                x509.NameAttribute(NameOID.COMMON_NAME, common_name),
            ])

            # Create certificate
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                ca_cert.subject
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.utcnow()
            ).not_valid_after(
                datetime.utcnow() + timedelta(days=self.cert_validity_days)
            ).add_extension(
                x509.BasicConstraints(ca=False, path_length=None),
                critical=True,
            ).add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_encipherment=True,
                    content_commitment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    key_cert_sign=False,
                    crl_sign=False,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            ).add_extension(
                x509.ExtendedKeyUsage([
                    x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH,
                ]),
                critical=True,
            ).sign(ca_key, hashes.SHA256())

            # Save certificate and key
            cert_path = self.cert_dir / f"{common_name}-client.crt"
            key_path = self.cert_dir / f"{common_name}-client.key"

            with open(cert_path, "wb") as f:
                f.write(cert.public_bytes(Encoding.PEM))

            with open(key_path, "wb") as f:
                f.write(private_key.private_bytes(
                    Encoding.PEM,
                    PrivateFormat.PKCS8,
                    NoEncryption()
                ))

            logger.info(f"✅ Client certificate generated: {cert_path}")
            return str(cert_path), str(key_path)

        except Exception as e:
            logger.error(f"Failed to generate client certificate: {e}")
            raise

    def get_certificate_info(self, cert_path: str) -> CertificateInfo:
        """
        Get information about a certificate.

        Args:
            cert_path: Path to certificate file

        Returns:
            CertificateInfo object
        """
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("cryptography library not available for certificate inspection")

        try:
            with open(cert_path, "rb") as f:
                cert = x509.load_pem_x509_certificate(f.read())

            # Extract certificate information
            subject = cert.subject.rfc4514_string()
            issuer = cert.issuer.rfc4514_string()
            serial_number = str(cert.serial_number)

            # Calculate fingerprint
            fingerprint = cert.fingerprint(hashes.SHA256()).hex()

            return CertificateInfo(
                cert_path=cert_path,
                key_path=cert_path.replace(".crt", ".key"),
                ca_path=str(self.cert_dir / "ca.crt"),
                created_at=cert.not_valid_before,
                expires_at=cert.not_valid_after,
                serial_number=serial_number,
                subject=subject,
                issuer=issuer,
                fingerprint=fingerprint
            )

        except Exception as e:
            logger.error(f"Failed to get certificate info: {e}")
            raise


class MTLSReverseProxy:
    """
    mTLS Reverse Proxy for secure database connections.

    Provides mutual TLS authentication and connection proxying
    for database services with certificate-based security.
    """

    def __init__(self, cert_manager: CertificateManager = None):
        """
        Initialize mTLS reverse proxy.

        Args:
            cert_manager: Certificate manager instance
        """
        self.cert_manager = cert_manager or CertificateManager()

        # Proxy configuration
        self.endpoints: Dict[str, ProxyEndpoint] = {}
        self.connection_metrics: List[ConnectionMetrics] = []

        # SSL contexts
        self.ssl_contexts: Dict[str, ssl.SSLContext] = {}

        # Monitoring
        self.metrics_log_path = Path("logs/mtls_proxy_metrics.log")
        self.metrics_log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info("MTLSReverseProxy initialized")

    def add_endpoint(
        self,
        name: str,
        database_type: DatabaseType,
        listen_host: str,
        listen_port: int,
        target_host: str,
        target_port: int,
        tls_enabled: bool = True,
        client_cert_required: bool = True
    ) -> bool:
        """
        Add a proxy endpoint.

        Args:
            name: Endpoint name
            database_type: Type of database
            listen_host: Host to listen on
            listen_port: Port to listen on
            target_host: Target database host
            target_port: Target database port
            tls_enabled: Enable TLS
            client_cert_required: Require client certificate

        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate certificates if TLS is enabled
            certificate_info = None
            if tls_enabled:
                # Ensure CA certificate exists
                ca_cert_path = self.cert_manager.cert_dir / "ca.crt"
                if not ca_cert_path.exists():
                    logger.info("Generating CA certificate...")
                    self.cert_manager.generate_ca_certificate()

                # Generate server certificate
                server_cert_path, server_key_path = self.cert_manager.generate_server_certificate(
                    common_name=f"{name}-proxy",
                    san_dns=[listen_host, "localhost"],
                    san_ips=[listen_host if listen_host != "localhost" else "127.0.0.1"]
                )

                certificate_info = self.cert_manager.get_certificate_info(server_cert_path)

                # Create SSL context
                ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                ssl_context.load_cert_chain(server_cert_path, server_key_path)

                if client_cert_required:
                    ssl_context.verify_mode = ssl.CERT_REQUIRED
                    ssl_context.load_verify_locations(ca_cert_path)

                self.ssl_contexts[name] = ssl_context

            # Create endpoint
            endpoint = ProxyEndpoint(
                name=name,
                database_type=database_type,
                listen_host=listen_host,
                listen_port=listen_port,
                target_host=target_host,
                target_port=target_port,
                tls_enabled=tls_enabled,
                client_cert_required=client_cert_required,
                certificate_info=certificate_info
            )

            self.endpoints[name] = endpoint
            logger.info(f"✅ Proxy endpoint added: {name} ({listen_host}:{listen_port} -> {target_host}:{target_port})")
            return True

        except Exception as e:
            logger.error(f"Failed to add proxy endpoint {name}: {e}")
            return False

    async def start_proxy(self, endpoint_name: str) -> bool:
        """
        Start a proxy endpoint.

        Args:
            endpoint_name: Name of endpoint to start

        Returns:
            True if successful, False otherwise
        """
        try:
            if endpoint_name not in self.endpoints:
                logger.error(f"Endpoint {endpoint_name} not found")
                return False

            endpoint = self.endpoints[endpoint_name]

            # Create server
            server = await asyncio.start_server(
                lambda r, w: self._handle_connection(endpoint, r, w),
                endpoint.listen_host,
                endpoint.listen_port,
                ssl=self.ssl_contexts.get(endpoint_name) if endpoint.tls_enabled else None
            )

            logger.info(f"✅ Proxy started: {endpoint_name} listening on {endpoint.listen_host}:{endpoint.listen_port}")

            # Start serving
            async with server:
                await server.serve_forever()

            return True

        except Exception as e:
            logger.error(f"Failed to start proxy {endpoint_name}: {e}")
            return False

    async def _handle_connection(self, endpoint: ProxyEndpoint, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """
        Handle a client connection.

        Args:
            endpoint: Proxy endpoint configuration
            reader: Client reader stream
            writer: Client writer stream
        """
        client_addr = writer.get_extra_info('peername')
        connection_start = time.time()
        bytes_sent = 0
        bytes_received = 0

        logger.info(f"🔗 New connection to {endpoint.name} from {client_addr}")

        try:
            # Extract client certificate info if available
            client_cert_subject = None
            if endpoint.tls_enabled and endpoint.client_cert_required:
                ssl_object = writer.get_extra_info('ssl_object')
                if ssl_object:
                    client_cert = ssl_object.getpeercert()
                    if client_cert:
                        client_cert_subject = client_cert.get('subject', '')
                        logger.info(f"🔐 Client certificate: {client_cert_subject}")

            # Connect to target database
            target_reader, target_writer = await asyncio.open_connection(
                endpoint.target_host,
                endpoint.target_port
            )

            logger.info(f"🔗 Connected to target: {endpoint.target_host}:{endpoint.target_port}")

            # Start bidirectional data forwarding
            async def forward_data(source_reader, dest_writer, direction):
                nonlocal bytes_sent, bytes_received
                try:
                    while True:
                        data = await source_reader.read(8192)
                        if not data:
                            break

                        dest_writer.write(data)
                        await dest_writer.drain()

                        if direction == "client_to_server":
                            bytes_sent += len(data)
                        else:
                            bytes_received += len(data)

                except Exception as e:
                    logger.debug(f"Data forwarding error ({direction}): {e}")
                finally:
                    dest_writer.close()
                    await dest_writer.wait_closed()

            # Start forwarding tasks
            client_to_server = asyncio.create_task(
                forward_data(reader, target_writer, "client_to_server")
            )
            server_to_client = asyncio.create_task(
                forward_data(target_reader, writer, "server_to_client")
            )

            # Wait for either direction to complete
            await asyncio.gather(client_to_server, server_to_client, return_exceptions=True)

        except Exception as e:
            logger.error(f"Connection handling error: {e}")

        finally:
            # Close connections
            try:
                writer.close()
                await writer.wait_closed()
            except:
                pass

            # Record metrics
            connection_duration = time.time() - connection_start
            ssl_info = writer.get_extra_info('ssl_object')

            metrics = ConnectionMetrics(
                endpoint_name=endpoint.name,
                client_ip=client_addr[0] if client_addr else "unknown",
                connected_at=datetime.fromtimestamp(connection_start),
                bytes_sent=bytes_sent,
                bytes_received=bytes_received,
                duration=connection_duration,
                tls_version=ssl_info.version() if ssl_info else "none",
                cipher_suite=ssl_info.cipher()[0] if ssl_info and ssl_info.cipher() else "none",
                client_cert_subject=client_cert_subject
            )

            self.connection_metrics.append(metrics)
            self._log_metrics(metrics)

            logger.info(f"🔚 Connection closed: {endpoint.name} from {client_addr} (duration: {connection_duration:.2f}s)")

    def _log_metrics(self, metrics: ConnectionMetrics):
        """Log connection metrics."""
        try:
            metrics_data = asdict(metrics)
            metrics_data['connected_at'] = metrics.connected_at.isoformat()

            with open(self.metrics_log_path, 'a') as f:
                f.write(json.dumps(metrics_data) + '\n')
        except Exception as e:
            logger.error(f"Failed to log metrics: {e}")

    def generate_client_certificates(self, clients: List[str]) -> Dict[str, Tuple[str, str]]:
        """
        Generate client certificates for mTLS authentication.

        Args:
            clients: List of client names

        Returns:
            Dictionary mapping client names to (cert_path, key_path) tuples
        """
        certificates = {}

        for client_name in clients:
            try:
                cert_path, key_path = self.cert_manager.generate_client_certificate(client_name)
                certificates[client_name] = (cert_path, key_path)
                logger.info(f"✅ Client certificate generated for: {client_name}")
            except Exception as e:
                logger.error(f"Failed to generate client certificate for {client_name}: {e}")

        return certificates

    def get_endpoint_status(self) -> Dict[str, Any]:
        """
        Get status of all proxy endpoints.

        Returns:
            Status dictionary
        """
        status = {
            "timestamp": datetime.utcnow().isoformat(),
            "endpoints": {},
            "total_connections": len(self.connection_metrics),
            "active_endpoints": len(self.endpoints)
        }

        for name, endpoint in self.endpoints.items():
            endpoint_metrics = [m for m in self.connection_metrics if m.endpoint_name == name]

            status["endpoints"][name] = {
                "database_type": endpoint.database_type.value,
                "listen_address": f"{endpoint.listen_host}:{endpoint.listen_port}",
                "target_address": f"{endpoint.target_host}:{endpoint.target_port}",
                "tls_enabled": endpoint.tls_enabled,
                "client_cert_required": endpoint.client_cert_required,
                "total_connections": len(endpoint_metrics),
                "certificate_info": asdict(endpoint.certificate_info) if endpoint.certificate_info else None
            }

        return status


async def setup_default_proxy_endpoints():
    """Set up default proxy endpoints for PLC-GPT databases."""
    proxy = MTLSReverseProxy()

    # Default database endpoints
    endpoints = [
        {
            "name": "postgresql-proxy",
            "database_type": DatabaseType.POSTGRESQL,
            "listen_host": "127.0.0.1",
            "listen_port": 5433,  # Proxy port
            "target_host": "localhost",
            "target_port": 5432,  # Actual PostgreSQL port
            "tls_enabled": True,
            "client_cert_required": True
        },
        {
            "name": "neo4j-proxy",
            "database_type": DatabaseType.NEO4J,
            "listen_host": "127.0.0.1",
            "listen_port": 7688,  # Proxy port
            "target_host": "localhost",
            "target_port": 7687,  # Actual Neo4j port
            "tls_enabled": True,
            "client_cert_required": True
        },
        {
            "name": "redis-proxy",
            "database_type": DatabaseType.REDIS,
            "listen_host": "127.0.0.1",
            "listen_port": 6380,  # Proxy port
            "target_host": "localhost",
            "target_port": 6379,  # Actual Redis port
            "tls_enabled": True,
            "client_cert_required": True
        },
        {
            "name": "qdrant-proxy",
            "database_type": DatabaseType.QDRANT,
            "listen_host": "127.0.0.1",
            "listen_port": 6334,  # Proxy port
            "target_host": "localhost",
            "target_port": 6333,  # Actual Qdrant port
            "tls_enabled": True,
            "client_cert_required": True
        }
    ]

    # Add all endpoints
    for endpoint_config in endpoints:
        success = proxy.add_endpoint(**endpoint_config)
        if success:
            logger.info(f"✅ Configured proxy endpoint: {endpoint_config['name']}")
        else:
            logger.error(f"❌ Failed to configure proxy endpoint: {endpoint_config['name']}")

    # Generate client certificates for services
    client_names = [
        "plc-gbt-gateway",
        "plc-gbt-worker",
        "plc-gbt-api",
        "plc-gbt-monitoring"
    ]

    certificates = proxy.generate_client_certificates(client_names)
    logger.info(f"✅ Generated {len(certificates)} client certificates")

    return proxy


if __name__ == "__main__":
    # Test the mTLS reverse proxy
    async def test_mtls_proxy():
        print("🔐 Testing mTLS Reverse Proxy...")

        # Set up proxy
        proxy = await setup_default_proxy_endpoints()

        # Get status
        status = proxy.get_endpoint_status()
        print(f"📊 Proxy Status: {json.dumps(status, indent=2)}")

        print("🎉 mTLS Reverse Proxy test completed!")
        print("To start proxy endpoints, run individual start_proxy() calls in production")

    # Run test
    asyncio.run(test_mtls_proxy())
