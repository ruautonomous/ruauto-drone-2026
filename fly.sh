#!/bin/bash
# Voluntary disclosure: This shell script was created with Gemini. It is start the drone's mission easily

# Define absolute paths
REPO_DIR="/home/ruauto/ruauto/auto/ruauto-drone-2026"
#SCALE_SCRIPT="/home/ruauto/ruauto/auto/hx711py-jetsonnano/stable_scale.py"
MAIN_SCRIPT="$REPO_DIR/src/main.py"
VENV_PATH="/home/ruauto/ruauto/venv/bin/activate"

#echo "Starting Drone Systems..."

# 1. Start the Broadcaster in a detached tmux session named 'hardware'
# We use sudo here because the broadcaster needs hardware access
#echo "  -> Launching Scale Broadcaster (System Python)..."
#tmux new-session -d -s hardware "sudo /usr/bin/python3 $SCALE_SCRIPT"

# 2. Start the Main App in a detached tmux session named 'drone'
echo "  -> Launching Main App (Venv Python)..."
tmux new-session -d -s drone "source $VENV_PATH && python3 $MAIN_SCRIPT"

echo "------------------------------------------------------"
echo "Done! Both processes are running in the background."
echo ""
#echo "To check the SCALE:      tmux attach -t hardware"
echo "To check the MAIN APP:   tmux attach -t drone"
echo "To detach from a view:   Press Ctrl+B, then D"
echo "To stop everything:      sudo pkill -f stable_scale.py && tmux kill-server"
echo "------------------------------------------------------"