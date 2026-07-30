import json

import pytest
from langchain_core.tools import BaseTool

from app.nodes.integrations.mysql_tool_node import (
    MySQLToolNode,
    _referenced_tables,
    _statement_command,
    _validate_single_statement,
)


@pytest.fixture()
def tool_node():
    tool = MySQLToolNode()
    tool.user_data = {"credential_id": "mysql-credential", "access_profile": "read_only"}
    tool.credentials = [{
        "id": "mysql-credential",
        "service_type": "mysql",
        "secret": {"host": "localhost", "database": "kai_demo", "username": "kai", "password": "kai"},
    }]
    return tool


def test_mysql_tool_metadata_has_only_tool_output(tool_node):
    assert tool_node.metadata.node_type.value == "provider"
    assert [output.name for output in tool_node.metadata.outputs] == ["tool"]
    assert tool_node.metadata.outputs[0].type == "BaseTool"
    profiles = next(prop for prop in tool_node.metadata.properties if prop.name == "access_profile")
    assert {option["value"] for option in profiles.options} == {
        "schema_only", "read_only", "read_insert", "read_write", "schema_write", "full_admin"
    }


def test_mysql_tool_returns_native_agent_tool_shape(tool_node):
    result = tool_node.execute()
    assert isinstance(result["mysql_database"]["tool"], BaseTool)
    assert result["mysql_database"]["tool"].name == "mysql_database"


def test_mysql_tool_rejects_writes_by_default_without_opening_database(tool_node):
    result = json.loads(tool_node.execute()["mysql_database"]["tool"].invoke("DELETE FROM customers"))
    assert "not allowed" in result["error"]


@pytest.mark.parametrize("query", ["SELECT 1; DROP TABLE customers", "SELECT 1; -- hidden", "SELECT 1 /* hidden */"])
def test_mysql_tool_rejects_stacked_or_commented_queries(query):
    with pytest.raises(ValueError):
        _validate_single_statement(query)


def test_mysql_tool_classifies_cte_by_effective_command():
    assert _statement_command("WITH recent AS (SELECT * FROM customers) SELECT * FROM recent") == "SELECT"
    assert _statement_command("WITH old AS (SELECT id FROM customers) DELETE FROM customers WHERE id IN (SELECT id FROM old)") == "DELETE"


def test_mysql_tool_finds_qualified_tables_without_treating_cte_as_a_table():
    tables = _referenced_tables(
        "WITH recent AS (SELECT * FROM kai_demo.customers) "
        "SELECT * FROM recent JOIN orders ON recent.id = orders.customer_id"
    )
    assert "kai_demo.customers" in tables
    assert "customers" in tables
    assert "orders" in tables
    assert "recent" not in tables


def test_mysql_tool_table_allowlist_rejects_other_tables_without_opening_database(tool_node):
    tool_node.user_data["allowed_tables"] = "customers"
    result = json.loads(tool_node.execute()["mysql_database"]["tool"].invoke("SELECT * FROM orders"))
    assert result == {"error": "Table access denied: orders"}


def test_mysql_tool_table_allowlist_rejects_unscoped_metadata_queries(tool_node):
    tool_node.user_data["allowed_tables"] = "customers"
    result = json.loads(tool_node.execute()["mysql_database"]["tool"].invoke("SHOW TABLES"))
    assert result == {"error": "Could not verify table access for this query."}
