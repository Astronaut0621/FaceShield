from __future__ import annotations


def _imports():
    try:
        import paddle
        from paddle import nn
        import paddle.nn.functional as F
    except ImportError as exc:
        raise RuntimeError("PaddlePaddle is required to build FaceShield models.") from exc
    return paddle, nn, F


class ConvBNReLU:
    def __new__(cls, in_channels: int, out_channels: int, stride: int = 1):
        _, nn, F = _imports()

        class _ConvBNReLU(nn.Layer):
            def __init__(self) -> None:
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

            def forward(self, x):
                return F.relu(self.bn(self.conv(x)))

        return _ConvBNReLU()


def build_model(model_name: str, dropout: float = 0.3, feature_dim: int = 128):
    paddle, nn, F = _imports()

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

        def forward(self, x):
            x = self.features(x)
            x = self.pool(x)
            return paddle.flatten(x, start_axis=1)

    class BaselineCNN(nn.Layer):
        def __init__(self) -> None:
            super().__init__()
            self.backbone = TinyBackbone(in_channels=3, feature_dim=feature_dim)
            self.classifier = nn.Sequential(
                nn.Dropout(dropout),
                nn.Linear(feature_dim, 2),
            )

        def forward(self, rgb):
            return self.classifier(self.backbone(rgb))

    class FusionFFTNet(nn.Layer):
        def __init__(self) -> None:
            super().__init__()
            self.spatial_branch = TinyBackbone(in_channels=3, feature_dim=feature_dim)
            self.frequency_branch = TinyBackbone(in_channels=1, feature_dim=feature_dim)
            self.classifier = nn.Sequential(
                nn.Dropout(dropout),
                nn.Linear(feature_dim * 2, feature_dim),
                nn.ReLU(),
                nn.Dropout(dropout),
                nn.Linear(feature_dim, 2),
            )

        def forward(self, rgb, fft):
            spatial = self.spatial_branch(rgb)
            frequency = self.frequency_branch(fft)
            return self.classifier(paddle.concat([spatial, frequency], axis=1))

    class FusionGatedFFTNet(nn.Layer):
        def __init__(self) -> None:
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
                nn.Linear(feature_dim, 2),
            )

        def forward(self, rgb, frequency):
            spatial = self.spatial_branch(rgb)
            frequency_feature = self.frequency_branch(frequency)
            gate = self.gate(paddle.concat([spatial, frequency_feature], axis=1))
            fused = spatial + self.frequency_scale * gate * frequency_feature
            return self.classifier(fused)

    if model_name == "baseline":
        return BaselineCNN()
    if model_name == "fusion_fft":
        return FusionFFTNet()
    if model_name == "fusion_v2":
        return FusionGatedFFTNet()
    raise ValueError(f"Unsupported model: {model_name}")
