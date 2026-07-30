import json
import os
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = PROJECT_ROOT / "client" / "app" / "data" / "templates"
TEMPLATE_PATHS = [
    TEMPLATE_DIR / f"mysql-test-0{index}-{suffix}.json"
    for index, suffix in [
        (1, "crud-mapping"),
        (2, "query-select"),
        (3, "delete-commands"),
        (4, "batching-errors"),
        (5, "agent-readonly"),
        (6, "agent-full-access"),
    ]
]
CURRENT_VERSION_TEMPLATE_PATHS = [
    TEMPLATE_DIR / "mysql-current-crud-test.json",
    TEMPLATE_DIR / "mysql-current-agent-tool-test.json",
]


def _templates():
    return [json.loads(path.read_text(encoding="utf-8")) for path in TEMPLATE_PATHS]


def _current_version_templates():
    return [json.loads(path.read_text(encoding="utf-8")) for path in CURRENT_VERSION_TEMPLATE_PATHS]


def _mysql_nodes(templates):
    return [
        node
        for template in templates
        for node in template["flow_data"]["nodes"]
        if node["type"] == "MySQL"
    ]


def _mysql_tool_nodes(templates):
    return [
        node
        for template in templates
        for node in template["flow_data"]["nodes"]
        if node["type"] == "MySQLTool"
    ]


def test_mysql_test_templates_are_well_formed():
    templates = _templates()

    assert len(templates) == 6
    assert len({template["id"] for template in templates}) == 6
    for template in templates:
        nodes = template["flow_data"]["nodes"]
        edges = template["flow_data"]["edges"]
        node_ids = {node["id"] for node in nodes}
        assert len(node_ids) == len(nodes)
        assert all(edge["source"] in node_ids and edge["target"] in node_ids for edge in edges)
        assert all(edge.get("sourceHandle") != "rows" for edge in edges)


def test_mysql_test_templates_cover_every_operation_and_option_family():
    templates = _templates()
    mysql_nodes = _mysql_nodes(templates)
    data = [node["data"] for node in mysql_nodes]

    assert {node["operation"] for node in data} >= {
        "delete_table",
        "execute_query",
        "insert",
        "upsert",
        "select",
        "update",
    }
    assert {node.get("data_mode") for node in data} >= {"auto_map", "manual"}
    assert {node.get("delete_command") for node in data} >= {"delete", "truncate", "drop"}
    assert {node.get("query_batching") for node in data} >= {"single", "independent", "transaction"}
    assert {node.get("combine_conditions") for node in data} >= {"AND", "OR"}
    assert {node.get("return_all") for node in data} >= {True, False}
    assert {node.get("large_numbers_output") for node in data} >= {"text", "numbers"}
    assert {node.get("decimal_numbers") for node in data} >= {True, False}
    assert {node.get("priority") for node in data} >= {"LOW_PRIORITY", "HIGH_PRIORITY"}
    assert any(node.get("replace_empty_strings") is True for node in data)
    assert any(node.get("select_distinct") is True for node in data)
    assert any(node.get("skip_on_conflict") is True for node in data)
    assert any(node.get("continue_on_fail") is True for node in data)
    assert any(node.get("detailed_output") is True for node in data)
    assert any("connection_timeout_ms" in node and "connection_limit" in node for node in data)
    assert any("$1:name" in node.get("query", "") for node in data)


def test_agent_templates_connect_mysql_tool_to_agent_tools():
    templates = _templates()
    tool_edges = [
        edge
        for template in templates
        for edge in template["flow_data"]["edges"]
        if edge.get("sourceHandle") == "tool"
    ]

    assert len(tool_edges) == 2
    assert all(edge["targetHandle"] == "tools" for edge in tool_edges)

    mysql_nodes_by_id = {
        node["id"]: node
        for template in templates
        for node in template["flow_data"]["nodes"]
        if node["type"] == "MySQLTool"
    }
    assert all(mysql_nodes_by_id[edge["source"]]["data"]["access_profile"] in {"read_only", "full_admin"} for edge in tool_edges)
    assert all(mysql_nodes_by_id[edge["source"]]["data"].get("allowed_tables") for edge in tool_edges)


def test_current_version_templates_are_documented_and_use_split_mysql_nodes():
    templates = _current_version_templates()

    assert len(templates) == 2
    assert len({template["id"] for template in templates}) == 2
    for template in templates:
        nodes = template["flow_data"]["nodes"]
        edges = template["flow_data"]["edges"]
        node_ids = {node["id"] for node in nodes}
        sticky_notes = [node for node in nodes if node["type"] == "StickyNoteNode"]

        assert len(node_ids) == len(nodes)
        assert all(edge["source"] in node_ids and edge["target"] in node_ids for edge in edges)
        assert len(sticky_notes) >= 3
        assert all(note["data"].get("text", "").strip() for note in sticky_notes)
        assert all(note.get("width", 0) >= 100 and note.get("height", 0) >= 100 for note in sticky_notes)
        assert all(edge.get("sourceHandle") != "rows" for edge in edges)

    crud_template, agent_template = templates
    crud_nodes = crud_template["flow_data"]["nodes"]
    assert {node["data"]["operation"] for node in crud_nodes if node["type"] == "MySQL"} == {
        "execute_query", "insert", "upsert", "update", "select", "delete_table"
    }
    assert not any(node["type"] == "MySQLTool" for node in crud_nodes)

    agent_nodes = agent_template["flow_data"]["nodes"]
    tools = [node for node in agent_nodes if node["type"] == "MySQLTool"]
    assert len(tools) == 1
    assert tools[0]["data"]["access_profile"] == "read_only"
    assert tools[0]["data"]["allowed_tables"] == "customers,orders,products"
    assert not any(node["type"] == "MySQL" for node in agent_nodes)
    assert any(
        edge["source"] == tools[0]["id"]
        and edge["sourceHandle"] == "tool"
        and edge["targetHandle"] == "tools"
        for edge in agent_template["flow_data"]["edges"]
    )

    credential_nodes = [
        node
        for template in templates
        for node in template["flow_data"]["nodes"]
        if "credential_id" in node.get("data", {})
    ]
    assert credential_nodes
    assert all(node["data"]["credential_id"] == "" for node in credential_nodes)


@pytest.mark.skipif(not os.getenv("MYSQL_SMOKE_HOST"), reason="requires the local MySQL demo container")
def test_non_agent_workflow_templates_against_local_mysql():
    from app.nodes.integrations.mysql_node import MySQLNode

    node = MySQLNode()
    node.credentials = [{
        "id": "mysql-smoke",
        "service_type": "mysql",
        "secret": {
            "host": os.environ["MYSQL_SMOKE_HOST"],
            "port": int(os.getenv("MYSQL_SMOKE_PORT", "3306")),
            "database": os.getenv("MYSQL_SMOKE_DATABASE", "kai_demo"),
            "username": os.getenv("MYSQL_SMOKE_USER", "kai"),
            "password": os.getenv("MYSQL_SMOKE_PASSWORD", "kai"),
        },
    }]
    connected_inputs = {
        "mysql_test_01_insert_auto_map": [
            {
                "email": "mysql-suite-one@example.com",
                "full_name": "Suite One",
                "status": "lead",
                "notes": "",
                "amount": 10.25,
                "big_value": 9223372036854775807,
            },
            {
                "email": "mysql-suite-two@example.com",
                "full_name": "Suite Two",
                "status": "active",
                "notes": "initial",
                "amount": 250.50,
                "big_value": 9007199254740992,
            },
        ],
        "mysql_test_02_batched_query": [["active", 0], ["lead", 0]],
        "mysql_test_04_independent_continue": [
            {"email": "batch-success@example.com", "status": "created"},
            {"email": "duplicate@example.com", "status": "must-fail"},
            {"email": "batch-after-error@example.com", "status": "created"},
        ],
    }

    try:
        for template in [*_templates()[:4], _current_version_templates()[0]]:
            for workflow_node in template["flow_data"]["nodes"]:
                if workflow_node["type"] != "MySQL":
                    continue
                configuration = {**workflow_node["data"], "credential_id": "mysql-smoke"}
                connected = connected_inputs.get(configuration["name"])
                result = node.execute(configuration, {"input": connected} if connected is not None else {})
                if configuration["name"] == "mysql_test_04_independent_continue":
                    assert len(result["errors"]) == 1
                else:
                    assert not result["errors"]
                if configuration["name"] == "mysql_current_select_test_row":
                    assert result["row_count"] == 1
                    assert result["rows"][0]["full_name"] == "Current Version Upserted"
                    assert result["rows"][0]["status"] == "active"
                    assert result["rows"][0]["score"] == 150.75
    finally:
        cleanup = {
            "credential_id": "mysql-smoke",
            "operation": "execute_query",
            "query": (
                "DROP TABLE IF EXISTS mysql_node_feature_test; "
                "DROP TABLE IF EXISTS mysql_node_query_test; "
                "DROP TABLE IF EXISTS mysql_test_delete_rows; "
                "DROP TABLE IF EXISTS mysql_test_truncate; "
                "DROP TABLE IF EXISTS mysql_test_drop; "
                "DROP TABLE IF EXISTS mysql_node_error_test;"
                "DROP TABLE IF EXISTS mysql_current_version_test;"
            ),
            "query_parameters": [],
        }
        node.execute(cleanup, {})
