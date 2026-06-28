from enum import Enum


class NodeLevel(str, Enum):
    conceito = "conceito"
    subtopico = "subtopico"
    topico = "topico"
    area = "area"


class NodeColor(str, Enum):
    azul = "azul"        # nunca estudado (dominio=None)
    verde = "verde"      # dominio >= 0.8
    amarelo = "amarelo"  # 0.5 <= dominio < 0.8, OR dominio < 0.5 without dependents
    vermelho = "vermelho"  # dominio < 0.5 AND has dependents


class EvidenceType(str, Enum):
    flashcard = "flashcard"
    exercicio = "exercicio"
    exam = "exam"
    revisao = "revisao"


class JobStatus(str, Enum):
    queued = "queued"
    running = "running"
    done = "done"
    failed = "failed"
    cancelled = "cancelled"


class RelationType(str, Enum):
    hierarquica = "hierarquica"
    cruzada = "cruzada"


class SessionStatus(str, Enum):
    ativa = "ativa"
    finalizada = "finalizada"
