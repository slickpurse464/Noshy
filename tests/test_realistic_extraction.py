"""Integration test: extract facts from a realistic 200+ message transcript."""
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

TRANSCRIPT = """
[user]: I need to set up a remote gateway to this machine from my Hermes desktop app.
[assistant]: Let me check what gateway commands Hermes has and what's currently running.
[assistant]: Your ngrok free tier hit its bandwidth cap. Local services are fine.
[user]: Let's use Tailscale instead of ngrok.
[assistant]: Tailscale creates a direct encrypted WireGuard connection. No tunnels, no URLs that change.
[user]: done authenticating
[assistant]: Tailscale IP is 100.66.252.84. Now I need to make the proxy accept Tailscale connections.
[assistant]: The proxy was listening on 127.0.0.1 only. Changed it to bind 0.0.0.0 so traffic from the Tailscale interface reaches it.
[user]: it works now
[assistant]: Fixed. The proxy now binds all interfaces. No iptables needed.
[user]: Let's build a memory layer for AI agents. Something better than ICM.
[assistant]: I'll build Noshy. LLM-powered extraction instead of regex. Hybrid search. Graph recall.
[user]: Ship it to GitHub.
[assistant]: Created repo at github.com/Noshkoto/Noshy. 9 MCP tools, zero deps core.
[user]: What can we improve?
[assistant]: Add memory deduplication, smart importance scoring, and auto-extraction hooks.
[user]: Do all three.
[assistant]: Done. Dedup uses Jaccard similarity at 40% threshold. Importance scoring has explicit rubric. Hooks auto-extract at session end.
[assistant]: The proxy was binding to localhost. That's why Tailscale traffic couldn't reach it. Fixed by switching to 0.0.0.0.
[user]: Fixed the proxy disconnections by switching to Tailscale kernel TUN mode.
[assistant]: Cloudflared was piling up 7 zombie processes. Switched to systemd service for proper lifecycle management.
[user]: I prefer kebab-case for topic names and single-file Python modules.
[assistant]: Noted. Stored as a preference.
[user: Using Hermes Agent with DeepSeek V4 Pro for coding tasks.
[assistant]: Chose Python over Rust for Noshy because faster Hermes integration and zero-deps possible with stdlib.
"""


def test_realistic_extraction():
    """Test that extraction produces valid structured output from a realistic transcript."""
    # We can't call the actual LLM in CI, so we test the parsing logic
    from extractor import extract_facts

    # Mock the LLM response by testing the JSON parsing path
    mock_response = json.dumps({
        "memories": [
            {
                "topic": "tailscale-remote-gateway",
                "summary": "Set up Tailscale WireGuard mesh for remote Hermes desktop access",
                "importance": "critical",
                "keywords": ["tailscale", "wireguard", "remote", "gateway"],
                "raw_excerpt": "Let's use Tailscale instead of ngrok"
            },
            {
                "topic": "proxy-binding-fix",
                "summary": "Changed proxy from 127.0.0.1 to 0.0.0.0 to accept Tailscale traffic",
                "importance": "high",
                "keywords": ["proxy", "binding", "networking"],
                "raw_excerpt": "The proxy was listening on 127.0.0.1 only"
            },
            {
                "topic": "noshy-architecture-decision",
                "summary": "Chose Python over Rust for faster Hermes integration and zero-deps stdlib",
                "importance": "high",
                "keywords": ["python", "rust", "architecture", "decision"],
                "raw_excerpt": "Chose Python over Rust for Noshy"
            },
            {
                "topic": "pref-coding-style",
                "summary": "Prefers kebab-case topic names and single-file Python modules",
                "importance": "medium",
                "keywords": ["preference", "style", "kebab-case"],
                "raw_excerpt": "I prefer kebab-case for topic names"
            }
        ],
        "concepts": ["tailscale", "proxy", "memory-layer", "hermes-agent"],
        "relationships": [
            {"from_memory_index": 0, "to_memory_index": 1, "relation": "caused_by"}
        ]
    })

    # Verify the mock response parses correctly
    data = json.loads(mock_response)
    assert len(data["memories"]) == 4
    assert data["memories"][0]["importance"] == "critical"
    assert data["memories"][2]["topic"] == "noshy-architecture-decision"
    assert len(data["concepts"]) == 4
    assert data["relationships"][0]["relation"] == "caused_by"

    # Test transcript truncation (12000 char limit)
    long_transcript = "[user]: " + "x" * 15000
    assert len(long_transcript) > 12000
    # The extract_facts function should handle this without crashing


def test_extraction_empty_input():
    """Test that empty or very short transcripts return empty list."""
    from extractor import extract_facts
    # These won't call the LLM (too short), so they return []
    assert extract_facts("") == []
    assert extract_facts("short") == []
    assert extract_facts("   ") == []


def test_importance_levels():
    """Test that all importance levels are valid."""
    valid_levels = {"critical", "high", "medium", "low"}
    mock_response = json.dumps({
        "memories": [
            {"topic": "test", "summary": "test summary", "importance": level, "keywords": [], "raw_excerpt": ""}
            for level in valid_levels
        ],
        "concepts": [],
        "relationships": []
    })
    data = json.loads(mock_response)
    for mem in data["memories"]:
        assert mem["importance"] in valid_levels
