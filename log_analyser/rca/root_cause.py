from typing import Literal
from pydantic import BaseModel, Field
from instructor import Instructor
from ..core.log import ParsedLog


class RootCause(BaseModel):
    """
    Root cause analysis for incidents

    Analyzes structured logs and context to identify root causes using deterministic reasoning.
    """

    severity: Literal["low", "medium", "high", "critical"] = Field(
        description="Incident severity: low=isolated/transient, medium=partial degradation, high=sustained failure, critical=outage/cascading/data risk"
    )
    description: str = Field(
        description="Detailed explanation of the incident, distinguishing symptoms from root cause"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score (0.0-1.0): >0.8=strong evidence, 0.5-0.8=probable, <0.5=weak/limited context",
    )
    root_cause: str = Field(
        description="Primary root cause identified from evidence. Use 'undetermined' if insufficient data"
    )
    recommended_actions: list[str] = Field(
        description="Recommend fixes that the developer can do to solve this problem"
    )
    source_of_issue: Literal[
        "application", "infrastructure", "configuration", "dependency", "unknown"
    ] = Field(description="Source category of the root cause")


def infer(client: Instructor, log: ParsedLog, model: str):
    return client.create(
        response_model=RootCause,
        model=model,
        messages=[
            {
                "role": "system",
                "content": """
                        You are a senior Site Reliability Engineer Agent performing deterministic root cause analysis on cloud systems.
                        Analyze structured logs and context. Reason strictly from provided evidence. Do not speculate, fabricate, or infer beyond observable data. If evidence is weak, lower confidence explicitly.
                        Responsibilities:
                        - Correlate logs within time window.
                        - Identify primary trigger.
                        - Distinguish symptom vs root cause.
                        - Avoid repeating raw logs.
                        - Prefer concrete infra/config/dependency causes over vague explanations.
                        - Consider common patterns: OOM, timeout, permission denied, network failure, deployment regression, config drift, dependency outage.
                        """,
            },
            {"role": "user", "content": log.raw},
        ],
    )
