from telco_agent_lab.simulator import TelcoSimulator


def test_auth_status_never_returns_secrets() -> None:
    result = TelcoSimulator().get_auth_status("sub-1001")
    assert result["ok"] is True
    assert result["secrets_returned"] is False
    assert not {"ki", "key", "secret", "vector"}.intersection(result)


def test_write_requires_exact_confirmation_and_audits_denial() -> None:
    sim = TelcoSimulator()
    denied = sim.provision_service("sub-1001", "data-roaming")
    assert denied["error"] == "explicit_confirmation_required"
    assert denied["changed"] is False
    assert "data-roaming" not in sim.get_subscriber("sub-1001")["subscriber"]["services"]
    assert sim.get_audit_log()[-1]["decision"] == "approval_required"

    approved = sim.provision_service("sub-1001", "data-roaming", "CONFIRM:sub-1001:data-roaming")
    assert approved["ok"] is True
    assert "data-roaming" in approved["services"]
    assert sim.get_audit_log()[-1]["decision"] == "applied"


def test_suspended_subscriber_cannot_be_provisioned() -> None:
    result = TelcoSimulator().provision_service(
        "sub-1003", "voice", "CONFIRM:sub-1003:voice"
    )
    assert result["error"] == "subscriber_not_active"


def test_untrusted_case_note_is_labeled() -> None:
    result = TelcoSimulator().get_subscriber("sub-1001")
    assert result["subscriber"]["case_note_trust"] == "untrusted_customer_supplied_text"

