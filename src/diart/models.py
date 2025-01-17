from typing import Optional, Text

import torch
import torch.nn as nn

try:
    import pyannote.audio.pipelines.utils as pyannote
    _has_pyannote = True
except ImportError:
    _has_pyannote = False


class SegmentationModel(nn.Module):
    """
    Minimal interface for a segmentation model.
    """

    @staticmethod
    def from_pyannote(model, use_auth_token: Optional[Text] = None) -> 'SegmentationModel':
        """
        Returns a `SegmentationModel` wrapping a pyannote model.

        Parameters
        ----------
        model: pyannote.PipelineModel
        use_auth_token : When loading a private or gated huggingface.co pipeline, set
            `use_auth_token` to True or to a string containing your hugginface.co
            authentication token that can be obtained by
            visiting https://hf.co/settings/tokens

        Returns
        -------
        wrapper: SegmentationModel
        """
        assert _has_pyannote, "No pyannote.audio installation found"

        class PyannoteSegmentationModel(SegmentationModel):
            def __init__(self, pyannote_model, use_auth_token):
                super().__init__()
                self.model = pyannote.get_model(pyannote_model, use_auth_token)

            def get_sample_rate(self) -> int:
                return self.model.audio.sample_rate

            def get_duration(self) -> float:
                return self.model.specifications.duration

            def __call__(self, waveform: torch.Tensor) -> torch.Tensor:
                return self.model(waveform)

        return PyannoteSegmentationModel(model, use_auth_token)

    def get_sample_rate(self) -> int:
        """Return the sample rate expected for model inputs"""
        raise NotImplementedError

    def get_duration(self) -> float:
        """Return the input duration by default (usually the one used during training)"""
        raise NotImplementedError

    def __call__(self, waveform: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of a segmentation model.

        Parameters
        ----------
        waveform: torch.Tensor, shape (batch, channels, samples)

        Returns
        -------
        speaker_segmentation: torch.Tensor, shape (batch, frames, speakers)
        """
        raise NotImplementedError


class EmbeddingModel(nn.Module):
    """Minimal interface for an embedding model."""

    @staticmethod
    def from_pyannote(model, use_auth_token: Optional[Text] = None) -> 'EmbeddingModel':
        """
        Returns an `EmbeddingModel` wrapping a pyannote model.

        Parameters
        ----------
        model: pyannote.PipelineModel
        use_auth_token : When loading a private or gated huggingface.co pipeline, set
            `use_auth_token` to True or to a string containing your hugginface.co
            authentication token that can be obtained by
            visiting https://hf.co/settings/tokens

        Returns
        -------
        wrapper: EmbeddingModel
        """
        assert _has_pyannote, "No pyannote.audio installation found"

        class PyannoteEmbeddingModel(EmbeddingModel):
            def __init__(self, pyannote_model, use_auth_token):
                super().__init__()
                self.model = pyannote.get_model(pyannote_model, use_auth_token)

            def __call__(
                self,
                waveform: torch.Tensor,
                weights: Optional[torch.Tensor] = None,
            ) -> torch.Tensor:
                return self.model(waveform, weights=weights)

        return PyannoteEmbeddingModel(model, use_auth_token)

    def __call__(
        self,
        waveform: torch.Tensor,
        weights: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Forward pass of an embedding model with optional weights.

        Parameters
        ----------
        waveform: torch.Tensor, shape (batch, channels, samples)
        weights: Optional[torch.Tensor], shape (batch, frames)
            Temporal weights for each sample in the batch. Defaults to no weights.

        Returns
        -------
        speaker_embeddings: torch.Tensor, shape (batch, speakers, embedding_dim)
        """
        raise NotImplementedError
