from __future__ import annotations

import paddle
from paddle import nn
import paddle.nn.functional as F


FUSION_MODELS = {"fusion_fft", "fusion_v2"}


def is_fusion_model(model_name: str) -> bool:
    return model_name in FUSION_MODELS


class ConvBNReLU(nn.Layer):
    def __init__(self, in_channels: int, out_channels: int, stride: int = 1) -> None:
        super().__init__()
        self.conv = nn.Conv2D(
            in_channels,
            out_channels,
            kernel_size=3,
            stride=stride,
            padding=1,
            bias_attr=False,
        )
        self.bn = nn.BatchNorm2D(out_channels)

    def forward(self, x: paddle.Tensor) -> paddle.Tensor:
        return F.relu(self.bn(self.conv(x)))


class TinyBackbone(nn.Layer):
    def __init__(self, in_channels: int, feature_dim: int = 128) -> None:
        super().__init__()
        self.features = nn.Sequential(
            ConvBNReLU(in_channels, 32, stride=2),
            ConvBNReLU(32, 32),
            ConvBNReLU(32, 64, stride=2),
            ConvBNReLU(64, 64),
            ConvBNReLU(64, 128, stride=2),
            ConvBNReLU(128, 128),
            ConvBNReLU(128, feature_dim, stride=2),
            ConvBNReLU(feature_dim, feature_dim),
        )
        self.pool = nn.AdaptiveAvgPool2D((1, 1))
        self.out_dim = feature_dim

    def forward(self, x: paddle.Tensor) -> paddle.Tensor:
        x = self.features(x)
        x = self.pool(x)
        return paddle.flatten(x, start_axis=1)


class BaselineCNN(nn.Layer):
    def __init__(self, num_classes: int = 2, feature_dim: int = 128, dropout: float = 0.3) -> None:
        super().__init__()
        self.backbone = TinyBackbone(in_channels=3, feature_dim=feature_dim)
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(feature_dim, num_classes),
        )

    def forward(self, rgb: paddle.Tensor) -> paddle.Tensor:
        feature = self.backbone(rgb)
        return self.classifier(feature)


class FusionFFTNet(nn.Layer):
    def __init__(self, num_classes: int = 2, feature_dim: int = 128, dropout: float = 0.3) -> None:
        super().__init__()
        self.spatial_branch = TinyBackbone(in_channels=3, feature_dim=feature_dim)
        self.frequency_branch = TinyBackbone(in_channels=1, feature_dim=feature_dim)
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(feature_dim * 2, feature_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(feature_dim, num_classes),
        )

    def forward(self, rgb: paddle.Tensor, fft: paddle.Tensor) -> paddle.Tensor:
        spatial = self.spatial_branch(rgb)
        frequency = self.frequency_branch(fft)
        fused = paddle.concat([spatial, frequency], axis=1)
        return self.classifier(fused)


class FusionGatedFFTNet(nn.Layer):
    def __init__(self, num_classes: int = 2, feature_dim: int = 128, dropout: float = 0.3) -> None:
        super().__init__()
        self.spatial_branch = TinyBackbone(in_channels=3, feature_dim=feature_dim)
        self.frequency_branch = TinyBackbone(in_channels=1, feature_dim=feature_dim)
        self.gate = nn.Sequential(
            nn.Linear(feature_dim * 2, feature_dim),
            nn.ReLU(),
            nn.Linear(feature_dim, feature_dim),
            nn.Sigmoid(),
        )
        self.frequency_scale = self.create_parameter(
            shape=[1],
            dtype="float32",
            default_initializer=nn.initializer.Constant(0.1),
        )
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(feature_dim, feature_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(feature_dim, num_classes),
        )

    def forward(self, rgb: paddle.Tensor, frequency: paddle.Tensor) -> paddle.Tensor:
        spatial = self.spatial_branch(rgb)
        frequency_feature = self.frequency_branch(frequency)
        gate = self.gate(paddle.concat([spatial, frequency_feature], axis=1))
        fused = spatial + self.frequency_scale * gate * frequency_feature
        return self.classifier(fused)


def build_model(model_name: str, dropout: float = 0.3, feature_dim: int = 128) -> nn.Layer:
    if model_name == "baseline":
        return BaselineCNN(dropout=dropout, feature_dim=feature_dim)
    if model_name == "fusion_fft":
        return FusionFFTNet(dropout=dropout, feature_dim=feature_dim)
    if model_name == "fusion_v2":
        return FusionGatedFFTNet(dropout=dropout, feature_dim=feature_dim)
    raise ValueError(f"Unsupported model: {model_name}")
