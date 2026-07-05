# FaceShield

FaceShield is an AI face forgery detection system for image-level fraud screening and evidence support. The context language keeps the project focused on forged face detection rather than generic image classification.

## Language

**Image-level Detection**:
A detection task where one uploaded image or extracted video frame is classified as real or fake.
_Avoid_: Video-level detection, generic image classification

**Real Face**:
A face image whose visible identity and facial region come from an original, non-manipulated source.
_Avoid_: Normal image, true sample

**Forged Face**:
A face image whose facial identity, expression, or facial region has been generated or manipulated by a face forgery method.
_Avoid_: Fake picture, abnormal image

**Forgery Probability**:
The model score representing how likely an image is to contain a forged face.
_Avoid_: Confidence, fake rate

**Risk Level**:
A user-facing category derived from the forgery probability for result presentation.
_Avoid_: Model label, grade

**Suspicious Region Heatmap**:
A visual explanation highlighting image regions that contributed most to the forgery decision.
_Avoid_: Attention picture, red map

**Frequency-Spatial Fusion**:
The algorithm approach that combines visual texture and structure cues with frequency-domain artifact cues for forged face detection.
_Avoid_: Multi-feature mix, double model

**Face Crop**:
An image region produced by automatically detecting a face, expanding the box to retain nearby forgery boundaries, and resizing it for model input.
_Avoid_: Manual crop, face-only cutout

**Detection Record**:
A retained result of one image-level detection owned by the system user who submitted the image, including the image identity, prediction, score, model version, and explanation artifact.
_Avoid_: Log, history item

**System User**:
A person who signs in to FaceShield to submit images for detection and view retained detection records.
_Avoid_: Visitor, operator, account
