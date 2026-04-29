"""Sample infrastructure module — imported by sample_code.py to demonstrate layer violations."""


class DatabaseClient:
    """Simulated database client for demonstration purposes."""

    def __init__(self, connection_string: str = "postgresql://localhost:5432/db"):
        self.connection_string = connection_string

    def execute(self, query: str) -> list[dict]:
        """Execute a query (simulated)."""
        return [{"id": 1, "username": "admin", "role": "administrator"}]

    def query(self, sql: str, params: dict | None = None) -> list[dict]:
        """Parameterised query method."""
        return self.execute(sql)
