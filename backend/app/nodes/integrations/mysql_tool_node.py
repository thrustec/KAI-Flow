"""Security-scoped MySQL tool provider for AI agents."""

from __future__ import annotations

import json
import re
from decimal import Decimal
from typing import Any, Dict, List, Mapping, Set

from langchain_core.tools import Tool

from ..base import (
    NodeInput,
    NodeOutput,
    NodePosition,
    NodeProperty,
    NodePropertyType,
    NodeType,
    ProviderNode,
)
from .mysql_node import _as_bool, _credential_secret, _flatten_node_configuration, mysql_connection


_ACCESS_COMMANDS: Dict[str, Set[str]] = {
    "schema_only": {"SHOW", "DESCRIBE", "DESC", "EXPLAIN"},
    "read_only": {"SHOW", "DESCRIBE", "DESC", "EXPLAIN", "SELECT"},
    "read_insert": {"SHOW", "DESCRIBE", "DESC", "EXPLAIN", "SELECT", "INSERT"},
    "read_write": {
        "SHOW", "DESCRIBE", "DESC", "EXPLAIN", "SELECT", "INSERT", "UPDATE", "DELETE", "REPLACE"
    },
    "schema_write": {
        "SHOW", "DESCRIBE", "DESC", "EXPLAIN", "SELECT", "INSERT", "UPDATE", "DELETE", "REPLACE",
        "CREATE", "ALTER", "DROP", "TRUNCATE", "RENAME",
    },
    "full_admin": {
        "SHOW", "DESCRIBE", "DESC", "EXPLAIN", "SELECT", "INSERT", "UPDATE", "DELETE", "REPLACE",
        "CREATE", "ALTER", "DROP", "TRUNCATE", "RENAME", "CALL", "SET", "ANALYZE", "OPTIMIZE",
    },
}

_TABLE_REFERENCE = re.compile(
    r"\b(?:(?:FROM|JOIN|INTO|UPDATE)\s+|TABLE\s+(?:IF\s+(?:NOT\s+)?EXISTS\s+)?)"
    r"((?:`[^`]+`|[A-Za-z0-9_$]+)(?:\.(?:`[^`]+`|[A-Za-z0-9_$]+))?)",
    re.IGNORECASE,
)


def _strip_code_fence(query: str) -> str:
    value = str(query or "").strip()
    match = re.fullmatch(r"```(?:sql)?\s*(.*?)\s*```", value, flags=re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else value


def _validate_single_statement(statement: str) -> str:
    """Reject comments and stacked SQL while respecting quoted string contents."""
    quote: str | None = None
    escaped = False
    semicolons: List[int] = []
    index = 0
    while index < len(statement):
        char = statement[index]
        next_char = statement[index + 1] if index + 1 < len(statement) else ""
        if escaped:
            escaped = False
        elif quote:
            if char == "\\":
                escaped = True
            elif char == quote:
                if next_char == quote:
                    index += 1
                else:
                    quote = None
        elif char in {"'", '"', "`"}:
            quote = char
        elif (char == "-" and next_char == "-") or char == "#" or (char == "/" and next_char == "*"):
            raise ValueError("SQL comments are disabled for MySQL Tool queries.")
        elif char == ";":
            semicolons.append(index)
        index += 1

    if quote:
        raise ValueError("The SQL query contains an unterminated quoted value.")
    if semicolons:
        final_non_space = len(statement.rstrip()) - 1
        if len(semicolons) > 1 or semicolons[0] != final_non_space:
            raise ValueError("MySQL Tool accepts exactly one SQL statement per call.")
        statement = statement[:semicolons[0]].rstrip()
    if not statement:
        raise ValueError("Provide a SQL query.")
    return statement


def _mask_quoted_sql(statement: str) -> str:
    output: List[str] = []
    quote: str | None = None
    escaped = False
    for char in statement:
        if escaped:
            escaped = False
            output.append(" ")
        elif quote:
            if char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            output.append(" ")
        elif char in {"'", '"', "`"}:
            quote = char
            output.append(" ")
        else:
            output.append(char)
    return "".join(output)


def _mask_string_literals(statement: str) -> str:
    """Mask string literals while preserving backtick-quoted identifiers."""
    output: List[str] = []
    quote: str | None = None
    escaped = False
    for char in statement:
        if escaped:
            escaped = False
            output.append(" ")
        elif quote:
            if char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            output.append(" ")
        elif char in {"'", '"'}:
            quote = char
            output.append(" ")
        else:
            output.append(char)
    return "".join(output)


def _statement_command(statement: str) -> str:
    """Return the effective command, including the command following a WITH CTE."""
    masked = _mask_quoted_sql(statement)
    first = re.match(r"\s*([A-Za-z]+)", masked)
    if not first:
        raise ValueError("Unable to determine the SQL command.")
    command = first.group(1).upper()
    if command != "WITH":
        return command

    depth = 0
    for match in re.finditer(r"[A-Za-z_]+|[()]", masked[first.end():]):
        token = match.group(0).upper()
        if token == "(":
            depth += 1
        elif token == ")":
            depth = max(0, depth - 1)
        elif depth == 0 and token in {"SELECT", "INSERT", "UPDATE", "DELETE", "REPLACE"}:
            return token
    raise ValueError("Unable to determine the command following WITH.")


def _normalized_allowed_tables(value: Any) -> Set[str]:
    if isinstance(value, list):
        parts = value
    else:
        parts = str(value or "").split(",")
    return {str(part).strip().strip("`").lower() for part in parts if str(part).strip()}


def _referenced_tables(statement: str) -> Set[str]:
    tables: Set[str] = set()
    masked = _mask_string_literals(statement)
    cte_aliases = {
        match.group(1).replace("`", "").lower()
        for match in re.finditer(r"(?:\bWITH\b|,)\s*(`[^`]+`|[A-Za-z0-9_$]+)(?:\s*\([^)]*\))?\s+AS\s*\(", masked, re.IGNORECASE)
    }
    for match in _TABLE_REFERENCE.finditer(masked):
        raw = match.group(1).replace("`", "").lower()
        if raw not in {"select", "set"} and raw not in cte_aliases:
            tables.add(raw)
            tables.add(raw.rsplit(".", 1)[-1])
    index_target = re.search(r"\bCREATE\s+(?:UNIQUE\s+)?INDEX\b.*?\bON\s+(`[^`]+`|[A-Za-z0-9_$]+)", masked, re.IGNORECASE | re.DOTALL)
    if index_target:
        tables.add(index_target.group(1).replace("`", "").lower())
    return tables


class MySQLToolNode(ProviderNode):
    """Provide a single-statement, permission-scoped MySQL tool to an Agent."""

    def __init__(self):
        super().__init__()
        self._metadata = {
            "name": "MySQLTool",
            "display_name": "MySQL Tool",
            "description": "Give an Agent explicitly scoped access to a MySQL database.",
            "category": "Tool",
            "node_type": NodeType.PROVIDER,
            "icon": {"name": "mysql", "path": "icons/mysql.svg", "alt": "MySQL Tool"},
            "colors": ["cyan-700", "blue-900"],
            "version": "1.0.0",
            "inputs": [
                NodeInput(name="credential_id", type="str", description="Selected MySQL credential ID.", required=True),
                NodeInput(name="access_profile", type="str", description="Allowed SQL command profile.", default="read_only", required=False),
                NodeInput(name="allowed_tables", type="str", description="Optional table allowlist.", default="", required=False),
                NodeInput(name="max_rows", type="int", description="Maximum returned rows.", default=200, required=False),
                NodeInput(name="tool_name", type="str", description="Name exposed to the Agent.", default="mysql_database", required=False),
                NodeInput(name="connection_timeout_ms", type="int", description="Connection timeout in milliseconds.", default=30000, required=False),
            ],
            "outputs": [
                NodeOutput(
                    name="tool",
                    displayName="Tool",
                    type="BaseTool",
                    description="Permission-scoped MySQL tool for an Agent's Tools input.",
                    is_connection=True,
                    direction=NodePosition.TOP,
                )
            ],
            "properties": [
                NodeProperty(
                    name="credential_id", displayName="Credential", type=NodePropertyType.CREDENTIAL_SELECT,
                    serviceType="mysql", required=True, description="MySQL credential used only by this tool."
                ),
                NodeProperty(
                    name="access_profile", displayName="Agent Permissions", type=NodePropertyType.SELECT,
                    default="read_only", required=True,
                    description="Choose the smallest permission set the Agent needs.",
                    options=[
                        {"label": "Inspect schema only (safest)", "value": "schema_only"},
                        {"label": "Read data (recommended)", "value": "read_only"},
                        {"label": "Read and insert rows", "value": "read_insert"},
                        {"label": "Read and modify rows", "value": "read_write"},
                        {"label": "Data and schema changes (dangerous)", "value": "schema_write"},
                        {"label": "Full administrative SQL (highest risk)", "value": "full_admin"},
                    ],
                ),
                NodeProperty(
                    name="allowed_tables", displayName="Allowed Tables", type=NodePropertyType.TEXT,
                    placeholder="customers, orders", required=False, tabName="options",
                    description="Optional comma-separated allowlist. Leave empty to allow all tables permitted by the database user."
                ),
                NodeProperty(
                    name="max_rows", displayName="Maximum Returned Rows", type=NodePropertyType.NUMBER,
                    default=200, min=1, max=5000, required=False, tabName="options",
                    description="Stops returning rows after this limit to protect Agent context and memory."
                ),
                NodeProperty(
                    name="tool_name", displayName="Tool Name", type=NodePropertyType.TEXT,
                    default="mysql_database", required=False, tabName="options",
                    description="Stable name exposed to the Agent."
                ),
                NodeProperty(
                    name="connection_timeout_ms", displayName="Connection Timeout (ms)", type=NodePropertyType.NUMBER,
                    default=30000, min=1000, max=300000, required=False, tabName="options"
                ),
            ],
        }

    def get_required_packages(self) -> List[str]:
        return ["PyMySQL>=1.1.1,<2.0.0", "sshtunnel>=0.4.0,<1.0.0", "paramiko>=2.7.2,<4.0.0"]

    def execute(self, **kwargs: Any) -> Dict[str, Any]:
        configuration = {**_flatten_node_configuration(self.user_data), **kwargs}
        secret = _credential_secret(self, configuration.get("credential_id"))
        access_profile = str(configuration.get("access_profile") or "read_only").lower()
        if access_profile not in _ACCESS_COMMANDS:
            raise ValueError("Unknown MySQL Tool access profile.")
        allowed_tables = _normalized_allowed_tables(configuration.get("allowed_tables"))
        max_rows = min(5000, max(1, int(configuration.get("max_rows") or 200)))
        raw_name = str(configuration.get("tool_name") or "mysql_database").strip()
        tool_name = re.sub(r"[^a-zA-Z0-9_-]", "_", raw_name) or "mysql_database"

        def run_query(query: str) -> str:
            try:
                statement = _validate_single_statement(_strip_code_fence(query))
                command = _statement_command(statement)
                if command not in _ACCESS_COMMANDS[access_profile]:
                    return json.dumps({
                        "error": f"{command} is not allowed by the '{access_profile}' permission profile."
                    })

                if allowed_tables:
                    referenced = _referenced_tables(statement)
                    unauthorized = sorted(
                        table for table in referenced
                        if table not in allowed_tables and table.rsplit(".", 1)[-1] not in allowed_tables
                    )
                    if unauthorized:
                        return json.dumps({"error": f"Table access denied: {', '.join(unauthorized)}"})
                    # When a table allowlist exists, never run a statement whose
                    # table scope cannot be proven. This also prevents SHOW TABLES
                    # and similar metadata queries from revealing unlisted tables.
                    if command != "SET" and not referenced:
                        return json.dumps({"error": "Could not verify table access for this query."})

                rows: List[Dict[str, Any]] = []
                affected_rows = 0
                last_insert_id = None
                truncated = False
                with mysql_connection(secret, configuration) as connection:
                    try:
                        with connection.cursor() as cursor:
                            cursor.execute(statement)
                            if cursor.description:
                                fetched = list(cursor.fetchmany(max_rows + 1))
                                truncated = len(fetched) > max_rows
                                rows = [self._serialize_row(row) for row in fetched[:max_rows]]
                            affected_rows = max(0, int(cursor.rowcount or 0))
                            last_insert_id = int(cursor.lastrowid) if cursor.lastrowid else None
                        connection.commit()
                    except Exception:
                        connection.rollback()
                        raise

                return json.dumps({
                    "rows": rows,
                    "row_count": len(rows),
                    "truncated": truncated,
                    "max_rows": max_rows,
                    "affected_rows": affected_rows,
                    "last_insert_id": last_insert_id,
                }, ensure_ascii=False, default=str)
            except Exception as exc:
                return json.dumps({"error": str(exc)}, ensure_ascii=False)

        permission_text = ", ".join(sorted(_ACCESS_COMMANDS[access_profile]))
        table_text = ", ".join(sorted(allowed_tables)) if allowed_tables else "all credential-visible tables"
        tool = Tool(
            name=tool_name,
            func=run_query,
            description=(
                f"Run one SQL statement against MySQL database '{secret.get('database') or 'default'}'. "
                f"Allowed commands: {permission_text}. Allowed tables: {table_text}. "
                "If the schema is unknown, inspect it before querying. Never invent table or column names. "
                f"Return at most {max_rows} rows and prefer selective WHERE clauses."
            ),
        )
        return {"mysql_database": {"tool": tool}}

    @staticmethod
    def _serialize_row(row: Mapping[str, Any]) -> Dict[str, Any]:
        serialized: Dict[str, Any] = {}
        for key, value in row.items():
            if isinstance(value, Decimal):
                serialized[key] = str(value)
            elif isinstance(value, (bytes, bytearray)):
                serialized[key] = bytes(value).hex()
            else:
                serialized[key] = value
        return serialized
