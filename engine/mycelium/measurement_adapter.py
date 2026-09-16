#!/usr/bin/env python3
"""
Measurement Adapter Framework - Real BI/Analytics Integration.

Replaces synthetic actuals_provider with pluggable adapters for:
- Snowflake, BigQuery, PostgreSQL, Redshift
- PostHog, Amplitude, Mixpanel, GA4
- Custom SQL/HTTP endpoints
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import json
import hashlib

import sys
from pathlib import Path

from engine.mycelium.postgres_registry import PostgresNodeRegistry
from engine.mycelium.postgres_persistence import get_cursor


class AdapterType(Enum):
    SNOWFLAKE = "snowflake"
    BIGQUERY = "bigquery"
    POSTGRESQL = "postgresql"
    REDSHIFT = "redshift"
    POSTHOG = "posthog"
    AMPLITUDE = "amplitude"
    MIXPANEL = "mixpanel"
    GA4 = "ga4"
    CUSTOM_SQL = "custom_sql"
    CUSTOM_HTTP = "custom_http"


@dataclass
class MeasurementAdapterConfig:
    """Configuration for a measurement adapter."""
    adapter_type: AdapterType
    name: str
    department: str  # Owning department
    credentials: Dict[str, str]  # Encrypted in production
    query_template: str  # SQL or HTTP template with {metric_names}, {window_start}, {window_end}
    metric_mapping: Dict[str, str]  # Internal metric name -> external column/event name
    window_config: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    created_at: str = ""
    updated_at: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "adapter_type": self.adapter_type.value,
            "name": self.name,
            "department": self.department,
            "credentials": self.credentials,
            "query_template": self.query_template,
            "metric_mapping": self.metric_mapping,
            "window_config": self.window_config,
            "enabled": self.enabled,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MeasurementAdapterConfig':
        return cls(
            adapter_type=AdapterType(data["adapter_type"]),
            name=data["name"],
            department=data["department"],
            credentials=data["credentials"],
            query_template=data["query_template"],
            metric_mapping=data["metric_mapping"],
            window_config=data.get("window_config", {}),
            enabled=data.get("enabled", True),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", "")
        )


@dataclass
class MeasurementWindow:
    """Time window for measurement queries."""
    start: datetime
    end: datetime
    
    def to_dict(self) -> Dict:
        return {
            "start": self.start.isoformat() + "Z",
            "end": self.end.isoformat() + "Z"
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MeasurementWindow':
        return cls(
            start=datetime.fromisoformat(data["start"].replace("Z", "")),
            end=datetime.fromisoformat(data["end"].replace("Z", ""))
        )
    
    @classmethod
    def last_n_days(cls, days: int) -> 'MeasurementWindow':
        end = datetime.utcnow()
        start = end - timedelta(days=days)
        return cls(start=start, end=end)
    
    @classmethod
    def current_quarter(cls) -> 'MeasurementWindow':
        now = datetime.utcnow()
        quarter_start_month = ((now.month - 1) // 3) * 3 + 1
        start = datetime(now.year, quarter_start_month, 1)
        if quarter_start_month == 10:
            end = datetime(now.year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end = datetime(now.year, quarter_start_month + 3, 1) - timedelta(seconds=1)
        return cls(start=start, end=end)


class MeasurementAdapter(ABC):
    """Abstract base class for measurement adapters."""
    
    def __init__(self, config: MeasurementAdapterConfig):
        self.config = config
    
    @abstractmethod
    def fetch_metrics(self, metric_names: List[str], window: MeasurementWindow) -> Dict[str, float]:
        """
        Fetch metric values for the given window.
        
        Args:
            metric_names: Internal metric names (e.g., ["referral_pipeline_qoq", "paid_cac_delta_pct"])
            window: Time window for measurement
            
        Returns:
            Dict mapping internal metric name -> value
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test if adapter can connect to data source."""
        pass
    
    def _map_metrics(self, metric_names: List[str]) -> List[str]:
        """Map internal metric names to external column/event names."""
        return [self.config.metric_mapping.get(m, m) for m in metric_names]
    
    def _render_query(self, metric_names: List[str], window: MeasurementWindow) -> str:
        """Render query template with metric names and window."""
        external_metrics = self._map_metrics(metric_names)
        return self.config.query_template.format(
            metric_names=", ".join(f"'{m}'" for m in external_metrics),
            metric_list=external_metrics,
            window_start=window.start.isoformat(),
            window_end=window.end.isoformat(),
            start_date=window.start.strftime("%Y-%m-%d"),
            end_date=window.end.strftime("%Y-%m-%d"),
            start_timestamp=int(window.start.timestamp()),
            end_timestamp=int(window.end.timestamp()),
            **self.config.window_config
        )


class PostgresAdapter(MeasurementAdapter):
    """PostgreSQL measurement adapter using existing connection pool."""
    
    def fetch_metrics(self, metric_names: List[str], window: MeasurementWindow) -> Dict[str, float]:
        query = self._render_query(metric_names, window)
        external_metrics = self._map_metrics(metric_names)
        
        with get_cursor() as cur:
            cur.execute(query)
            row = cur.fetchone()
            if not row:
                return {m: 0.0 for m in metric_names}
            
            # Map external column names back to internal metric names
            reverse_mapping = {v: k for k, v in self.config.metric_mapping.items()}
            result = {}
            for internal, external in self.config.metric_mapping.items():
                if external in row:
                    result[internal] = float(row[external]) if row[external] is not None else 0.0
                else:
                    result[internal] = 0.0
            return result
    
    def test_connection(self) -> bool:
        try:
            with get_cursor() as cur:
                cur.execute("SELECT 1")
                return True
        except Exception:
            return False


class SnowflakeAdapter(MeasurementAdapter):
    """Snowflake measurement adapter."""
    
    def __init__(self, config: MeasurementAdapterConfig):
        super().__init__(config)
        self._conn = None
    
    def _get_connection(self):
        if self._conn is None:
            import snowflake.connector
            self._conn = snowflake.connector.connect(
                user=self.config.credentials["user"],
                password=self.config.credentials["password"],
                account=self.config.credentials["account"],
                warehouse=self.config.credentials.get("warehouse"),
                database=self.config.credentials.get("database"),
                schema=self.config.credentials.get("schema")
            )
        return self._conn
    
    def fetch_metrics(self, metric_names: List[str], window: MeasurementWindow) -> Dict[str, float]:
        query = self._render_query(metric_names, window)
        
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute(query)
        row = cur.fetchone()
        
        if not row:
            return {m: 0.0 for m in metric_names}
        
        # Assume columns match external metric names
        external_metrics = self._map_metrics(metric_names)
        reverse_mapping = {v: k for k, v in self.config.metric_mapping.items()}
        
        result = {}
        for i, external in enumerate(external_metrics):
            internal = reverse_mapping.get(external, external)
            result[internal] = float(row[i]) if row[i] is not None else 0.0
        
        return result
    
    def test_connection(self) -> bool:
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute("SELECT 1")
            return True
        except Exception:
            return False


class BigQueryAdapter(MeasurementAdapter):
    """Google BigQuery measurement adapter."""
    
    def __init__(self, config: MeasurementAdapterConfig):
        super().__init__(config)
        self._client = None
    
    def _get_client(self):
        if self._client is None:
            from google.cloud import bigquery
            credentials_path = self.config.credentials.get("credentials_path")
            if credentials_path:
                self._client = bigquery.Client.from_service_account_json(credentials_path)
            else:
                self._client = bigquery.Client()
        return self._client
    
    def fetch_metrics(self, metric_names: List[str], window: MeasurementWindow) -> Dict[str, float]:
        query = self._render_query(metric_names, window)
        
        client = self._get_client()
        query_job = client.query(query)
        rows = list(query_job.result())
        
        if not rows:
            return {m: 0.0 for m in metric_names}
        
        row = rows[0]
        # BigQuery Row supports dict-like access
        result = {}
        for internal, external in self.config.metric_mapping.items():
            if external in row:
                result[internal] = float(row[external]) if row[external] is not None else 0.0
            else:
                result[internal] = 0.0
        
        return result
    
    def test_connection(self) -> bool:
        try:
            client = self._get_client()
            client.query("SELECT 1").result()
            return True
        except Exception:
            return False


class PostHogAdapter(MeasurementAdapter):
    """PostHog measurement adapter via HTTP API."""
    
    def fetch_metrics(self, metric_names: List[str], window: MeasurementWindow) -> Dict[str, float]:
        import requests
        
        base_url = self.config.credentials["base_url"].rstrip("/")
        api_key = self.config.credentials["api_key"]
        project_id = self.config.credentials["project_id"]
        
        headers = {"Authorization": f"Bearer {api_key}"}
        
        result = {}
        for internal, external in self.config.metric_mapping.items():
            if internal not in metric_names:
                continue
            
            # PostHog events API
            url = f"{base_url}/api/projects/{project_id}/events/"
            params = {
                "event": external,
                "after": window.start.strftime("%Y-%m-%d"),
                "before": window.end.strftime("%Y-%m-%d"),
            }
            
            try:
                resp = requests.get(url, headers=headers, params=params, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                result[internal] = float(data.get("count", 0))
            except Exception:
                result[internal] = 0.0
        
        return result
    
    def test_connection(self) -> bool:
        import requests
        try:
            base_url = self.config.credentials["base_url"].rstrip("/")
            api_key = self.config.credentials["api_key"]
            project_id = self.config.credentials["project_id"]
            headers = {"Authorization": f"Bearer {api_key}"}
            resp = requests.get(f"{base_url}/api/projects/{project_id}/", headers=headers, timeout=10)
            return resp.status_code == 200
        except Exception:
            return False


class AmplitudeAdapter(MeasurementAdapter):
    """Amplitude measurement adapter via HTTP API."""
    
    def fetch_metrics(self, metric_names: List[str], window: MeasurementWindow) -> Dict[str, float]:
        import requests
        
        api_key = self.config.credentials["api_key"]
        secret_key = self.config.credentials["secret_key"]
        
        # Amplitude Chart REST API
        url = "https://amplitude.com/api/2/chart"
        
        result = {}
        for internal, external in self.config.metric_mapping.items():
            if internal not in metric_names:
                continue
            
            # Build chart query for this metric
            params = {
                "e": external,
                "start": window.start.strftime("%Y%m%d"),
                "end": window.end.strftime("%Y%m%d"),
                "m": "uniques",  # or "totals", "avg"
            }
            
            try:
                resp = requests.get(url, params=params, auth=(api_key, secret_key), timeout=30)
                resp.raise_for_status()
                data = resp.json()
                series = data.get("data", {}).get("series", [])
                if series:
                    result[internal] = float(series[0].get("values", [{}])[0].get("value", 0))
                else:
                    result[internal] = 0.0
            except Exception:
                result[internal] = 0.0
        
        return result
    
    def test_connection(self) -> bool:
        import requests
        try:
            api_key = self.config.credentials["api_key"]
            secret_key = self.config.credentials["secret_key"]
            resp = requests.get("https://amplitude.com/api/2/chart", 
                               params={"e": "test", "start": "20240101", "end": "20240102"},
                               auth=(api_key, secret_key), timeout=10)
            return resp.status_code == 200
        except Exception:
            return False


class CustomSQLAdapter(MeasurementAdapter):
    """Generic SQL adapter for any PostgreSQL-compatible database."""
    
    def __init__(self, config: MeasurementAdapterConfig):
        super().__init__(config)
        self._pool = None
    
    def _get_pool(self):
        if self._pool is None:
            import psycopg2.pool
            self._pool = psycopg2.pool.SimpleConnectionPool(
                1, 5,
                host=self.config.credentials["host"],
                port=self.config.credentials.get("port", 5432),
                database=self.config.credentials["database"],
                user=self.config.credentials["user"],
                password=self.config.credentials["password"]
            )
        return self._pool
    
    def fetch_metrics(self, metric_names: List[str], window: MeasurementWindow) -> Dict[str, float]:
        query = self._render_query(metric_names, window)
        
        pool = self._get_pool()
        conn = pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute(query)
                row = cur.fetchone()
                if not row:
                    return {m: 0.0 for m in metric_names}
                
                external_metrics = self._map_metrics(metric_names)
                reverse_mapping = {v: k for k, v in self.config.metric_mapping.items()}
                
                result = {}
                for internal, external in self.config.metric_mapping.items():
                    if external in row:
                        result[internal] = float(row[external]) if row[external] is not None else 0.0
                    else:
                        result[internal] = 0.0
                return result
        finally:
            pool.putconn(conn)
    
    def test_connection(self) -> bool:
        try:
            pool = self._get_pool()
            conn = pool.getconn()
            pool.putconn(conn)
            return True
        except Exception:
            return False


class CustomHTTPAdapter(MeasurementAdapter):
    """Generic HTTP adapter for REST/GraphQL APIs."""
    
    def fetch_metrics(self, metric_names: List[str], window: MeasurementWindow) -> Dict[str, float]:
        import requests
        
        base_url = self.config.credentials["base_url"].rstrip("/")
        headers = self.config.credentials.get("headers", {})
        if isinstance(headers, str):
            try:
                headers = json.loads(headers)
            except Exception:
                headers = {}
        
        auth = self.config.credentials.get("auth")
        if isinstance(auth, str):
            try:
                auth = tuple(json.loads(auth))
            except Exception:
                auth = None
        elif isinstance(auth, list):
            auth = tuple(auth)
        
        # Build query params from template
        query = self._render_query(metric_names, window)
        # Expect template to produce full URL or params dict
        try:
            endpoint = self.config.query_template.format(
                base_url=base_url,
                metric_names=",".join(self._map_metrics(metric_names)),
                window_start=window.start.isoformat(),
                window_end=window.end.isoformat()
            )
        except KeyError:
            endpoint = base_url
        
        try:
            resp = requests.get(endpoint, headers=headers, auth=auth, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            
            # Expect response format: {"metric_name": value, ...}
            result = {}
            for internal in metric_names:
                external = self.config.metric_mapping.get(internal, internal)
                if external in data:
                    result[internal] = float(data[external]) if data[external] is not None else 0.0
                else:
                    result[internal] = 0.0
            return result
        except Exception:
            return {m: 0.0 for m in metric_names}
    
    def test_connection(self) -> bool:
        import requests
        try:
            base_url = self.config.credentials["base_url"].rstrip("/")
            headers = self.config.credentials.get("headers", {})
            if isinstance(headers, str):
                try:
                    headers = json.loads(headers)
                except Exception:
                    headers = {}
            
            auth = self.config.credentials.get("auth")
            if isinstance(auth, str):
                try:
                    auth = tuple(json.loads(auth))
                except Exception:
                    auth = None
            elif isinstance(auth, list):
                auth = tuple(auth)
            
            resp = requests.get(f"{base_url}/health", headers=headers, auth=auth, timeout=10)
            return resp.status_code == 200
        except Exception:
            return False


ADAPTER_REGISTRY = {
    AdapterType.POSTGRESQL: PostgresAdapter,
    AdapterType.SNOWFLAKE: SnowflakeAdapter,
    AdapterType.BIGQUERY: BigQueryAdapter,
    AdapterType.REDSHIFT: CustomSQLAdapter,  # Same interface
    AdapterType.POSTHOG: PostHogAdapter,
    AdapterType.AMPLITUDE: AmplitudeAdapter,
    AdapterType.MIXPANEL: CustomHTTPAdapter,  # Similar HTTP pattern
    AdapterType.GA4: CustomHTTPAdapter,  # GA4 Data API
    AdapterType.CUSTOM_SQL: CustomSQLAdapter,
    AdapterType.CUSTOM_HTTP: CustomHTTPAdapter,
}


def get_adapter(config: MeasurementAdapterConfig) -> MeasurementAdapter:
    """Factory function to create adapter from config."""
    adapter_class = ADAPTER_REGISTRY.get(config.adapter_type)
    if not adapter_class:
        raise ValueError(f"No adapter registered for type: {config.adapter_type}")
    return adapter_class(config)


class MeasurementAdapterRegistry:
    """Manages adapter configs per department in PostgreSQL."""
    
    def __init__(self):
        self.registry = PostgresNodeRegistry()
        self._cache: Dict[str, MeasurementAdapter] = {}
    
    def _ensure_tables(self):
        """Create measurement_adapters table if not exists."""
        with get_cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS measurement_adapters (
                    id BIGSERIAL PRIMARY KEY,
                    adapter_type VARCHAR(50) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    department VARCHAR(255) NOT NULL,
                    credentials JSONB NOT NULL DEFAULT '{}',
                    query_template TEXT NOT NULL,
                    metric_mapping JSONB NOT NULL DEFAULT '{}',
                    window_config JSONB NOT NULL DEFAULT '{}',
                    enabled BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    UNIQUE(department, name)
                );
                CREATE INDEX IF NOT EXISTS idx_adapters_dept ON measurement_adapters(department);
            """)
    
    def register(self, config: MeasurementAdapterConfig) -> bool:
        """Register or update adapter config."""
        self._ensure_tables()
        
        with get_cursor() as cur:
            cur.execute("""
                INSERT INTO measurement_adapters 
                (adapter_type, name, department, credentials, query_template, metric_mapping, window_config, enabled)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (department, name) DO UPDATE SET
                    adapter_type = EXCLUDED.adapter_type,
                    credentials = EXCLUDED.credentials,
                    query_template = EXCLUDED.query_template,
                    metric_mapping = EXCLUDED.metric_mapping,
                    window_config = EXCLUDED.window_config,
                    enabled = EXCLUDED.enabled,
                    updated_at = NOW()
            """, (
                config.adapter_type.value,
                config.name,
                config.department,
                json.dumps(config.credentials),
                config.query_template,
                json.dumps(config.metric_mapping),
                json.dumps(config.window_config),
                config.enabled
            ))
        return True
    
    def get(self, department: str, name: str) -> Optional[MeasurementAdapterConfig]:
        """Get adapter config by department and name."""
        self._ensure_tables()
        
        with get_cursor() as cur:
            cur.execute("""
                SELECT adapter_type, name, department, credentials, query_template,
                       metric_mapping, window_config, enabled, created_at, updated_at
                FROM measurement_adapters
                WHERE department = %s AND name = %s AND enabled = TRUE
            """, (department, name))
            row = cur.fetchone()
            if not row:
                return None
            return MeasurementAdapterConfig(
                adapter_type=AdapterType(row['adapter_type']),
                name=row['name'],
                department=row['department'],
                credentials=row['credentials'],
                query_template=row['query_template'],
                metric_mapping=row['metric_mapping'],
                window_config=row['window_config'],
                enabled=row['enabled'],
                created_at=row['created_at'].isoformat() if row['created_at'] else "",
                updated_at=row['updated_at'].isoformat() if row['updated_at'] else ""
            )
    
    def list_for_department(self, department: str) -> List[MeasurementAdapterConfig]:
        """List all adapters for a department."""
        self._ensure_tables()
        
        with get_cursor() as cur:
            cur.execute("""
                SELECT adapter_type, name, department, credentials, query_template,
                       metric_mapping, window_config, enabled, created_at, updated_at
                FROM measurement_adapters
                WHERE department = %s AND enabled = TRUE
                ORDER BY name
            """, (department,))
            return [MeasurementAdapterConfig(
                adapter_type=AdapterType(row['adapter_type']),
                name=row['name'],
                department=row['department'],
                credentials=row['credentials'],
                query_template=row['query_template'],
                metric_mapping=row['metric_mapping'],
                window_config=row['window_config'],
                enabled=row['enabled'],
                created_at=row['created_at'].isoformat() if row['created_at'] else "",
                updated_at=row['updated_at'].isoformat() if row['updated_at'] else ""
            ) for row in cur.fetchall()]
    
    def get_adapter(self, department: str, name: str) -> Optional[MeasurementAdapter]:
        """Get instantiated adapter (cached)."""
        cache_key = f"{department}:{name}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        config = self.get(department, name)
        if not config:
            return None
        
        adapter = get_adapter(config)
        self._cache[cache_key] = adapter
        return adapter
    
    def invalidate_cache(self, department: str = None, name: str = None):
        """Invalidate adapter cache."""
        if department and name:
            self._cache.pop(f"{department}:{name}", None)
        elif department:
            keys_to_remove = [k for k in self._cache if k.startswith(f"{department}:")]
            for k in keys_to_remove:
                self._cache.pop(k, None)
        else:
            self._cache.clear()


# Global registry instance
_measurement_registry = None

def get_measurement_registry() -> MeasurementAdapterRegistry:
    global _measurement_registry
    if _measurement_registry is None:
        _measurement_registry = MeasurementAdapterRegistry()
    return _measurement_registry


def register_default_adapters():
    """Register default adapter configs for testing."""
    registry = get_measurement_registry()
    
    # PostgreSQL adapter (uses existing pool)
    pg_config = MeasurementAdapterConfig(
        adapter_type=AdapterType.POSTGRESQL,
        name="postgres_primary",
        department="system",
        credentials={},
        query_template="""
            SELECT 
                referral_pipeline_qoq,
                paid_cac_delta_pct,
                referral_to_opp_conversion
            FROM marketing_metrics
            WHERE date >= '{start_date}' AND date <= '{end_date}'
            ORDER BY date DESC LIMIT 1
        """,
        metric_mapping={
            "referral_pipeline_qoq": "referral_pipeline_qoq",
            "paid_cac_delta_pct": "paid_cac_delta_pct",
            "referral_to_opp_conversion": "referral_to_opp_conversion"
        }
    )
    registry.register(pg_config)
    
    # Example Snowflake config
    sf_config = MeasurementAdapterConfig(
        adapter_type=AdapterType.SNOWFLAKE,
        name="snowflake_analytics",
        department="marketing",
        credentials={
            "user": "${SNOWFLAKE_USER}",
            "password": "${SNOWFLAKE_PASSWORD}",
            "account": "${SNOWFLAKE_ACCOUNT}",
            "warehouse": "ANALYTICS_WH",
            "database": "ANALYTICS",
            "schema": "MARKETING"
        },
        query_template="""
            SELECT 
                referral_pipeline_qoq,
                paid_cac_delta_pct,
                referral_to_opp_conversion
            FROM marketing.kpi_daily
            WHERE date >= '{start_date}' AND date <= '{end_date}'
            ORDER BY date DESC LIMIT 1
        """,
        metric_mapping={
            "referral_pipeline_qoq": "referral_pipeline_qoq",
            "paid_cac_delta_pct": "paid_cac_delta_pct",
            "referral_to_opp_conversion": "referral_to_opp_conversion"
        }
    )
    registry.register(sf_config)
    
    # Example PostHog config
    ph_config = MeasurementAdapterConfig(
        adapter_type=AdapterType.POSTHOG,
        name="posthog_events",
        department="product",
        credentials={
            "base_url": "https://app.posthog.com",
            "api_key": "${POSTHOG_API_KEY}",
            "project_id": "${POSTHOG_PROJECT_ID}"
        },
        query_template="",  # Not used for PostHog
        metric_mapping={
            "signup_conversion": "signup_completed",
            "feature_adoption": "feature_used",
            "churn_risk": "cancel_subscription"
        }
    )
    registry.register(ph_config)


if __name__ == "__main__":
    # Test
    registry = get_measurement_registry()
    register_default_adapters()
    
    # Test Postgres adapter
    pg_adapter = registry.get_adapter("system", "postgres_primary")
    if pg_adapter:
        print("Postgres adapter created")
        result = pg_adapter.fetch_metrics(
            ["referral_pipeline_qoq", "paid_cac_delta_pct"],
            MeasurementWindow.last_n_days(30)
        )
        print(f"Metrics: {result}")
    
    print("Done")