# SPDX-FileCopyrightText: 2026 Smarter > Harder
# SPDX-License-Identifier: MIT
"""Model findings and render deterministic text and JSON reports."""

import json
from collections import Counter
from dataclasses import asdict, dataclass

MESSAGE_IDS = {
    "FACT-01",
    "FMT-01",
    "FMT-02",
    "LOADER-01",
    "LOOP-01",
    "NAME-01",
    "REG-01",
    "SCAFFOLD-01",
    "SCAFFOLD-02",
    "SCAFFOLD-03",
    "TOOL",
}
WARNING_IDS = {"FLOOR-01"}


@dataclass(frozen=True)
class Finding:
    """One style, structure, or tool finding."""

    role_path: str | None
    path: str
    line: int
    id: str
    message: str
    kind: str

    def text(self):
        """Render the finding as its one-line text form."""

        base = f"{self.path}:{self.line} {self.id}"
        if self.id in WARNING_IDS:
            return f"{base}: warning: {self.message}"
        if self.id in MESSAGE_IDS:
            return f"{base}: {self.message}"
        return base


def _counts(findings):
    return Counter(finding.id for finding in findings)


def _summary(prefix, findings, warnings=()):
    summary = f"{prefix}: {len(findings)} finding(s)"
    counts = _counts(findings)
    if counts:
        summary += " " + " ".join(
            f"{rule_id} x{counts[rule_id]}" for rule_id in sorted(counts)
        )
    if warnings:
        counts = _counts(warnings)
        summary += f"; {len(warnings)} warning(s) " + " ".join(
            f"{rule_id} x{counts[rule_id]}" for rule_id in sorted(counts)
        )
    return summary


def text_report(findings, roles, roots):
    """Render findings, role summaries, root summaries, and the total."""

    lines = sorted(finding.text() for finding in findings)
    failing = [finding for finding in findings if finding.id not in WARNING_IDS]
    warnings = [finding for finding in findings if finding.id in WARNING_IDS]
    for role in sorted(roles, key=lambda item: item.role_path):
        role_findings = [
            finding for finding in failing if finding.role_path == role.role_path
        ]
        role_warnings = [
            finding for finding in warnings if finding.role_path == role.role_path
        ]
        lines.append(_summary(f"== {role.role_path}", role_findings, role_warnings))
    for root in sorted(roots):
        root_findings = [
            finding
            for finding in failing
            if finding.role_path is None and finding.path == root
        ]
        if root_findings:
            lines.append(_summary(f"== root {root}", root_findings))
    total = f"== total: {len(roles)} role(s), {len(failing)} finding(s)"
    if warnings:
        total += f", {len(warnings)} warning(s)"
    lines.append(total)
    return "\n".join(lines) + "\n"


def _finding_dict(finding):
    return dict(sorted(asdict(finding).items()))


def json_report(findings, roles):
    """Render the complete deterministic JSON report."""

    ordinary = sorted(
        (
            finding
            for finding in findings
            if finding.role_path is not None and finding.id not in WARNING_IDS
        ),
        key=lambda finding: finding.text(),
    )
    warnings = sorted(
        (
            finding
            for finding in findings
            if finding.role_path is not None and finding.id in WARNING_IDS
        ),
        key=lambda finding: finding.text(),
    )
    root = sorted(
        (
            finding
            for finding in findings
            if finding.role_path is None and finding.id not in WARNING_IDS
        ),
        key=lambda finding: finding.text(),
    )
    role_rows = []
    for role in sorted(roles, key=lambda item: item.role_path):
        role_findings = [
            finding for finding in ordinary if finding.role_path == role.role_path
        ]
        role_warnings = [
            finding for finding in warnings if finding.role_path == role.role_path
        ]
        role_rows.append(
            {
                "findings": len(role_findings),
                "ids": dict(sorted(_counts(role_findings).items())),
                "role_kind": role.kind,
                "role_path": role.role_path,
                "warning_ids": dict(sorted(_counts(role_warnings).items())),
                "warnings": len(role_warnings),
            }
        )
    failing = ordinary + root
    payload = {
        "findings": [_finding_dict(finding) for finding in ordinary],
        "roles": role_rows,
        "root_findings": [_finding_dict(finding) for finding in root],
        "summary": {
            "findings": len(failing),
            "ids": dict(sorted(_counts(failing).items())),
            "roles": len(roles),
            "warning_ids": dict(sorted(_counts(warnings).items())),
            "warnings": len(warnings),
        },
        "warnings": [_finding_dict(finding) for finding in warnings],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def exit_status(findings, report_only=False):
    """Return the report exit status for a completed check."""

    failing = any(finding.id not in WARNING_IDS for finding in findings)
    return 0 if report_only or not failing else 1
