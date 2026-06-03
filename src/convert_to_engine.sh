#!/usr/bin/env bash
# =============================================================================
#  convert_to_engine.sh
#  Convert best.onnx (YOLOv26 detection) and resnet_classifier*.onnx
#  to TensorRT .engine files on Jetson Orin Nano — JetPack 6.1
#  (L4T 36.4.x | CUDA 12.6 | TensorRT 10.3)
#
#  Usage:
#    chmod +x convert_to_engine.sh
#    ./convert_to_engine.sh
#
#  Optional — override default paths via env vars before running:
#    YOLO_ONNX=/path/to/best.onnx
#    RESNET_ONNX=/path/to/resnet_classifier.onnx
#    RESNET2_ONNX=/path/to/resnet_classifier_2_.onnx   (leave empty to skip)
#    OUT_DIR=/path/to/output/dir
# =============================================================================

set -euo pipefail

# ── Colour helpers ────────────────────────────────────────────────────────────
GREEN='\033[0;32m'; CYAN='\033[0;36m'; RED='\033[0;31m'; BOLD='\033[1m'; NC='\033[0m'
info()    { echo -e "${CYAN}[INFO]${NC}  $*"; }
success() { echo -e "${GREEN}[ OK ]${NC}  $*"; }
die()     { echo -e "${RED}[ERR ]${NC}  $*" >&2; exit 1; }

# ── Paths — edit these or override with env vars ──────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

YOLO_ONNX="${YOLO_ONNX:-${SCRIPT_DIR}/best.onnx}"
RESNET_ONNX="${RESNET_ONNX:-${SCRIPT_DIR}/resnet_classifier.onnx}"
RESNET2_ONNX="${RESNET2_ONNX:-${SCRIPT_DIR}/resnet_classifier_2_.onnx}"
OUT_DIR="${OUT_DIR:-${SCRIPT_DIR}/engines}"

TRTEXEC="/usr/src/tensorrt/bin/trtexec"

# ── Sanity checks ─────────────────────────────────────────────────────────────
[[ -x "$TRTEXEC" ]] || die "trtexec not found at $TRTEXEC — is JetPack 6.1 installed?"
[[ -f "$YOLO_ONNX"   ]] || die "YOLO ONNX not found:   $YOLO_ONNX"
[[ -f "$RESNET_ONNX" ]] || die "ResNet ONNX not found: $RESNET_ONNX"

mkdir -p "$OUT_DIR"

echo -e "${BOLD}"
echo "════════════════════════════════════════════════════════"
echo "  TensorRT Engine Builder — Jetson Orin Nano / JP 6.1  "
echo "════════════════════════════════════════════════════════${NC}"
info "Output dir : $OUT_DIR"
info "trtexec    : $TRTEXEC"
echo

# ── 1. YOLO detection model (best.onnx) ──────────────────────────────────────
# Model facts (from export metadata):
#   • YOLOv26n, Ultralytics 8.4.46
#   • Input  : graph_input_cast_0  — static [1, 3, 1024, 1024]
#   • Output : output0             — post-NMS (end2end=True, NMS baked in)
#   • Exported with half=True  →  FP16 is native precision
#   • 2 classes: BLACK-WHITE-SQUARES, Fake-Square

YOLO_ENGINE="${OUT_DIR}/best_fp16.engine"
info "Building YOLO engine (FP16) — this takes a few minutes…"

"$TRTEXEC" \
    --onnx="$YOLO_ONNX" \
    --saveEngine="$YOLO_ENGINE" \
    --fp16 \
    --inputIOFormats=fp16:chw \
    --outputIOFormats=fp16:chw \
    --builderOptimizationLevel=3 \
    --timingCacheFile="${OUT_DIR}/yolo_timing.cache" \
    2>&1 | grep -E "(Building|Timing|Created|Engine|Layers|mean|Error|Warning)" || true

success "YOLO engine  → $YOLO_ENGINE"
echo

# ── 2. ResNet classifier (resnet_classifier.onnx) ────────────────────────────
# Model facts:
#   • Input  : input   — [1, 3, H, W]  (static batch)
#   • Output : output  — classification logits
#   • 43 MB model; FP16 halves memory and speeds up on Orin Nano

RESNET_ENGINE="${OUT_DIR}/resnet_classifier_fp16.engine"
info "Building ResNet classifier engine (FP16) — this takes a few minutes…"

"$TRTEXEC" \
    --onnx="$RESNET_ONNX" \
    --saveEngine="$RESNET_ENGINE" \
    --fp16 \
    --builderOptimizationLevel=3 \
    --timingCacheFile="${OUT_DIR}/resnet_timing.cache" \
    2>&1 | grep -E "(Building|Timing|Created|Engine|Layers|mean|Error|Warning)" || true

success "ResNet engine → $RESNET_ENGINE"
echo

# ── 3. resnet_classifier_2_.onnx (optional — skipped if not present) ─────────
if [[ -f "$RESNET2_ONNX" ]]; then
    RESNET2_ENGINE="${OUT_DIR}/resnet_classifier_2_fp16.engine"
    info "Building ResNet classifier_2 engine (FP16)…"

    "$TRTEXEC" \
        --onnx="$RESNET2_ONNX" \
        --saveEngine="$RESNET2_ENGINE" \
        --fp16 \
        --builderOptimizationLevel=3 \
        --timingCacheFile="${OUT_DIR}/resnet2_timing.cache" \
        2>&1 | grep -E "(Building|Timing|Created|Engine|Layers|mean|Error|Warning)" || true

    success "ResNet2 engine → $RESNET2_ENGINE"
    echo
else
    info "resnet_classifier_2_.onnx not found — skipping (set RESNET2_ONNX= to enable)"
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo -e "${BOLD}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Done! Engine files:${NC}"
find "$OUT_DIR" -name "*.engine" -exec ls -lh {} \;
echo
info "Quick latency check: $TRTEXEC --loadEngine=<file> --iterations=200"
echo -e "${BOLD}════════════════════════════════════════════════════════${NC}"
