from dataclasses import dataclass


@dataclass
class PipelineConfig:
    blacklist: bool = False
    frequency: bool = False
    nlp: bool = False
    strip_timestamps: bool = False
    stats: bool = False
    freq_threshold: float = 0.02


def run_pipeline(text: str, config: PipelineConfig) -> str:
    # Scaffold stage: phases are not wired yet, so the pipeline is pass-through.
    _ = config
    return text
