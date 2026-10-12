# Phase 5: Remediation Agent

**Authority:** recommendation and verification-plan generation. Changes remain in the organization’s established change-management process.

## Responsibilities

Translate accepted findings and limited impact evidence into prioritized, testable remediation options. Identify ownership, compensating controls, rollback considerations, detection improvements, and retest criteria. The agent does not deploy changes, alter infrastructure, approve exceptions, or close findings.

## Contract

| Inputs | Outputs | Shared-state access |
|---|---|---|
| Accepted finding/validation/impact artifacts, asset ownership, organizational standards | Remediation backlog items, risk rationale, phased mitigation options, verification plan | Reads accepted findings/evidence; writes recommendations, audit events |

```yaml
name: recommend_remediation
description: Produce evidence-linked remediation options and a non-executing verification plan.
inputSchema:
  type: object
  additionalProperties: false
  properties:
    finding_id: {type: string}
    evidence_refs: {type: array, items: {type: string}, minItems: 1}
    owner_ref: {type: string}
  required: [finding_id, evidence_refs, owner_ref]
outputSchema:
  type: object
  required: [recommendations, verification_plan, limitations]
policy:
  risk: low
  requires_human_approval: false
  mutating_actions: forbidden
```

## System-prompt guidance

> Base recommendations only on accepted, attributable evidence. Separate immediate containment, durable remediation, compensating controls, and detection improvements. State assumptions and operational tradeoffs. Do not fabricate a patch, declare a vulnerability fixed, access source/control planes, or invoke deployment tools. Recommend a human-owned validation test and change-record linkage.

## ATT&CK mapping

This phase consumes the defensive coverage mappings captured earlier. It maps recommended preventive/detective controls to relevant ATT&CK tactics (for example, monitoring for **Discovery** or **Lateral Movement**) but does not conduct adversary behavior.

## Success criteria

- Recommendations link to a finding, evidence, owner, priority rationale, and verification criterion.
- At least one least-disruptive and one durable option are distinguished when feasible.
- The plan identifies dependencies, rollback, compensating controls, and detection tuning.

## Failure and abort conditions

Return `needs-human-review` when evidence is insufficient, an owner is unknown, remediation could introduce safety/availability risk, or a recommendation conflicts with policy. Never close a finding based on an agent recommendation alone; closure needs human change evidence and an approved retest.

The [reporting agent](architecture.md#roles-and-authority) consumes accepted recommendations and their limitations.

