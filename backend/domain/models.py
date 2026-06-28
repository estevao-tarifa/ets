from __future__ import annotations

from dataclasses import dataclass

from backend.domain.enums import EvidenceType, JobStatus, NodeLevel


@dataclass(frozen=True)
class KnowledgeNodeData:
    id: int
    materia_id: int
    nome: str
    nivel: NodeLevel
    descricao: str | None = None


@dataclass(frozen=True)
class EvidenciaData:
    id: int
    node_id: int
    tipo: EvidenceType
    resultado: float  # 0.0 - 1.0
    session_id: int | None = None


@dataclass(frozen=True)
class FlashcardData:
    id: int
    node_id: int
    frente: str
    verso: str
    ease_factor: float = 2.5
    interval_days: int = 1
    acertos: int = 0
    erros: int = 0


@dataclass(frozen=True)
class JobData:
    id: int
    material_id: int
    status: JobStatus
    tentativas: int = 0
    max_tentativas: int = 3
    current_step: str | None = None
    error_msg: str | None = None
