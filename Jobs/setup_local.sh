#!/usr/bin/env bash
# Sets up the model services to run natively (without Docker), e.g. on macOS with MPS.
# Usage: ./setup_local.sh   (PYTHON=python3.11 ./setup_local.sh to pick the interpreter)
set -euo pipefail
cd "$(dirname "$0")"

PYTHON=${PYTHON:-python3.11}

clone() {
    [ -d "$2" ] || git clone --depth 1 "$1" "$2"
}

# ALIS is disabled: its checkpoint (lhq1024-snapshot.pkl) is no longer publicly available
# clone https://github.com/universome/alis Alis/alis
clone https://github.com/NVlabs/stylegan2-ada-pytorch Stylegan2/stylegan2
clone https://github.com/CompVis/latent-diffusion.git Superresolution/latent-diffusion
clone https://github.com/CompVis/taming-transformers.git Superresolution/src/taming-transformers
clone https://github.com/openai/CLIP.git Superresolution/src/clip

# alis uses np.float, which was removed in numpy 1.24
# find Alis/alis -name '*.py' -exec perl -pi -e 's/np\.float\(/float(/g' {} +

for svc in Stylegan2 Superresolution Worker; do  # Alis disabled
    echo "==> Creating virtualenv for $svc"
    "$PYTHON" -m venv "$svc/.venv"
    (cd "$svc" && .venv/bin/pip install --upgrade pip && .venv/bin/pip install -r requirements-local.txt)
done

# ldm and taming have no top-level __init__.py, so put the cloned repos straight on sys.path
SITE_PACKAGES=$(Superresolution/.venv/bin/python -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')
for repo in latent-diffusion src/taming-transformers src/clip; do
    echo "$(pwd)/Superresolution/$repo"
done > "$SITE_PACKAGES/superresolution-repos.pth"

mkdir -p Shared/images Shared/projection Shared/pca Shared/upscaled
echo "Done. Start everything with ./run_local.sh"
