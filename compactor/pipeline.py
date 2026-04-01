from dataclasses import dataclass

from compactor.blacklist import apply_blacklist


@dataclass
class PipelineConfig:
    blacklist: bool = False
    frequency: bool = False
    nlp: bool = False
    strip_timestamps: bool = False
    stats: bool = False
    freq_threshold: float = 0.02


def run_pipeline(text: str, config: PipelineConfig) -> str:
    if config.blacklist:
        text = apply_blacklist(text)
    return text
