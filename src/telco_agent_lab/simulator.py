"""Deterministic in-memory telecom systems with guarded synthetic operations."""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from threading import Lock
from typing import Any


SERVICES = {"voice", "sms", "data-roaming", "voicemail"}


class TelcoSimulator:
    """Small, deterministic HLR/HSS/AuC-inspired sandbox.

    Every identifier and record is synthetic. Authentication secrets and
    cryptographic vectors are intentionally absent from the data model.
    """

    def __init__(self) -> None:
        self._lock = Lock()
        self._subscribers: dict[str, dict[str, Any]] = {
            "sub-1001": {
                "subscriber_id": "sub-1001",
                "msisdn": "+47000000001",
                "imsi": "001010000000001",
                "plan": "Nordic Basic",
                "status": "active",
                "services": ["voice", "sms", "voicemail"],
                "network": {"registered": True, "mme": "mme-lab-01", "last_seen": "2026-11-10T09:15:00Z"},
                "auth": {"profile": "aka-lab-v1", "state": "provisioned", "last_auth": "2026-11-10T09:14:52Z"},
                "case_note": "Customer reports intermittent data while roaming.",
            },
            "sub-1002": {
                "subscriber_id": "sub-1002",
                "msisdn": "+47000000002",
                "imsi": "001010000000002",
                "plan": "IoT Connect",
                "status": "active",
                "services": ["sms", "data-roaming"],
                "network": {"registered": False, "mme": None, "last_seen": "2026-11-09T21:03:11Z"},
                "auth": {"profile": "aka-iot-lab", "state": "provisioned", "last_auth": "2026-11-09T21:03:10Z"},
                "case_note": "Device is scheduled for a coverage check.",
            },
            "sub-1003": {
                "subscriber_id": "sub-1003",
                "msisdn": "+47000000003",
                "imsi": "001010000000003",
                "plan": "Nordic Basic",
                "status": "suspended",
                "services": ["sms"],
                "network": {"registered": False, "mme": None, "last_seen": "2026-11-08T16:40:00Z"},
                "auth": {"profile": "aka-lab-v1", "state": "provisioned", "last_auth": "2026-11-08T16:39:58Z"},
                "case_note": "Suspension was requested by the synthetic care workflow.",
            },
        }
        self._audit: list[dict[str, Any]] = []

    def list_subscribers(self) -> list[dict[str, str]]:
        with self._lock:
            return [
                {"subscriber_id": item["subscriber_id"], "plan": item["plan"], "status": item["status"]}
                for item in self._subscribers.values()
            ]

    def get_subscriber(self, subscriber_id: str) -> dict[str, Any]:
        with self._lock:
            item = self._subscribers.get(subscriber_id)
            if item is None:
                return {"ok": False, "error": "unknown_subscriber", "subscriber_id": subscriber_id}
            result = deepcopy(item)
            result["case_note_trust"] = "untrusted_customer_supplied_text"
            return {"ok": True, "subscriber": result}

    def get_network_status(self, subscriber_id: str) -> dict[str, Any]:
        with self._lock:
            item = self._subscribers.get(subscriber_id)
            if item is None:
                return {"ok": False, "error": "unknown_subscriber", "subscriber_id": subscriber_id}
            return {"ok": True, "subscriber_id": subscriber_id, **deepcopy(item["network"])}

    def get_auth_status(self, subscriber_id: str) -> dict[str, Any]:
        """Return status metadata only; never return Ki, keys, or auth vectors."""
        with self._lock:
            item = self._subscribers.get(subscriber_id)
            if item is None:
                return {"ok": False, "error": "unknown_subscriber", "subscriber_id": subscriber_id}
            return {
                "ok": True,
                "subscriber_id": subscriber_id,
                **deepcopy(item["auth"]),
                "secrets_returned": False,
            }

    def provision_service(self, subscriber_id: str, service: str, confirmation: str = "") -> dict[str, Any]:
        if service not in SERVICES:
            return {"ok": False, "error": "unsupported_service", "allowed_services": sorted(SERVICES)}
        required_confirmation = f"CONFIRM:{subscriber_id}:{service}"
        with self._lock:
            item = self._subscribers.get(subscriber_id)
            if item is None:
                return {"ok": False, "error": "unknown_subscriber", "subscriber_id": subscriber_id}
            if item["status"] != "active":
                self._record("provision_service", subscriber_id, service, "denied_inactive")
                return {"ok": False, "error": "subscriber_not_active", "status": item["status"]}
            if confirmation != required_confirmation:
                self._record("provision_service", subscriber_id, service, "approval_required")
                return {
                    "ok": False,
                    "error": "explicit_confirmation_required",
                    "confirmation_token": required_confirmation,
                    "changed": False,
                }
            if service not in item["services"]:
                item["services"].append(service)
                item["services"].sort()
            self._record("provision_service", subscriber_id, service, "applied")
            return {"ok": True, "subscriber_id": subscriber_id, "services": list(item["services"]), "changed": True}

    def suspend_line(self, subscriber_id: str, confirmation: str = "") -> dict[str, Any]:
        required_confirmation = f"CONFIRM:SUSPEND:{subscriber_id}"
        with self._lock:
            item = self._subscribers.get(subscriber_id)
            if item is None:
                return {"ok": False, "error": "unknown_subscriber", "subscriber_id": subscriber_id}
            if confirmation != required_confirmation:
                self._record("suspend_line", subscriber_id, None, "approval_required")
                return {
                    "ok": False,
                    "error": "explicit_confirmation_required",
                    "confirmation_token": required_confirmation,
                    "changed": False,
                }
            item["status"] = "suspended"
            item["network"]["registered"] = False
            item["network"]["mme"] = None
            self._record("suspend_line", subscriber_id, None, "applied")
            return {"ok": True, "subscriber_id": subscriber_id, "status": "suspended", "changed": True}

    def get_audit_log(self) -> list[dict[str, Any]]:
        with self._lock:
            return deepcopy(self._audit)

    def _record(self, operation: str, subscriber_id: str, target: str | None, decision: str) -> None:
        self._audit.append({
            "at": datetime.now(UTC).isoformat(timespec="seconds"),
            "operation": operation,
            "subscriber_id": subscriber_id,
            "target": target,
            "decision": decision,
        })

