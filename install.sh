#!/bin/bash
# ============================================================
#  Yukioh_Ōkami — Termux Installer v4.5 (Original Style)
# ============================================================

clear

RED='\033[1;31m'
GREEN='\033[1;32m'
CYAN='\033[1;36m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
WHITE='\033[1;37m'
DIM='\033[2m'
BOLD='\033[1m'
NC='\033[0m'

# ---- Box drawing (exact original characters) ----
BOX_W=60
box_top() {
    printf "  ${GREEN}╔"
    printf "%${BOX_W}s" | tr ' ' '═'
    printf "╗${NC}\n"
}
box_bottom() {
    printf "  ${GREEN}╚"
    printf "%${BOX_W}s" | tr ' ' '═'
    printf "╝${NC}\n"
}
box_line() {
    local text="$1"
    local pad=$(( BOX_W - ${#text} - 1 ))
    printf "  ${GREEN}║ ${text}%${pad}s ${GREEN}║${NC}\n" ""
}
box_center() {
    local text="$1"
    local pad_left=$(( (BOX_W - ${#text}) / 2 ))
    local pad_right=$(( BOX_W - ${#text} - pad_left ))
    printf "  ${GREEN}║ %${pad_left}s%s%${pad_right}s ${GREEN}║${NC}\n" "" "$text" ""
}

# ---- Helpers ----
spinner() {
    local pid=$1
    local msg=$2
    local spin='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
    local i=0
    while kill -0 $pid 2>/dev/null; do
        printf "\r  ${CYAN}${spin:$i:1}${NC}  ${DIM}$msg${NC}"
        i=$(( (i+1) % 10 ))
        sleep 0.08
    done
    printf "\r"
}

progress_bar() {
    local current=$1
    local total=$2
    local label=$3
    local width=30
    local filled=$(( current * width / total ))
    local empty=$(( width - filled ))
    local pct=$(( current * 100 / total ))
    local bar
    bar="${GREEN}"
    for ((i=0; i<filled; i++)); do bar+="█"; done
    bar+="${DIM}"
    for ((i=0; i<empty; i++)); do bar+="░"; done
    bar+="${NC}"
    printf "  [${bar}] ${BOLD}%3d%%${NC}  ${DIM}%s${NC}\n" "$pct" "$label"
}

section() {
    echo
    echo -e "  ${BLUE}┌────────────────────────────────────────────────────┐${NC}"
    echo -e "  ${BLUE}│${NC}  ${BOLD}${WHITE}$1${NC}"
    echo -e "  ${BLUE}└────────────────────────────────────────────────────┘${NC}"
}

log_ok()   { echo -e "  ${GREEN}[✔]${NC}  $1"; }
log_info() { echo -e "  ${CYAN}[➤]${NC}  $1"; }
log_warn() { echo -e "  ${YELLOW}[!]${NC}  $1"; }
log_err()  { echo -e "  ${RED}[✘]${NC}  $1"; }
divider()  { echo -e "  ${DIM}──────────────────────────────────────────────────${NC}"; }

# ---- Banner ----
print_banner() {
    box_top
    box_line ""
    box_line "   ██╗   ██╗██╗   ██╗██╗  ██╗██╗ ██████╗ ██╗  ██╗"
    box_line "   ╚██╗ ██╔╝██║   ██║██║ ██╔╝██║██╔═══██╗██║  ██║"
    box_line "    ╚████╔╝ ██║   ██║█████╔╝ ██║██║   ██║███████║"
    box_line "     ╚██╔╝  ██║   ██║██╔═██╗ ██║██║   ██║██╔══██║"
    box_line "      ██║   ╚██████╔╝██║  ██╗██║╚██████╔╝██║  ██║"
    box_line "      ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═╝"
    box_line ""
    box_center "YUKIOH OKAMI TOOL INSTALLER v4.5"
    box_center "PUBG / BGMI PAK MODDING TOOL SETUP"
    box_bottom
    echo
}

# ---- Main ----
print_banner
sleep 0.5

# STEP 1
section "STEP 1/6 — SYSTEM UPDATE"
log_info "Updating Termux packages..."
{
    pkg update -y
} > /dev/null 2>&1 &
spinner $! "Updating packages..."
wait $!
log_ok "System packages updated"
progress_bar 1 6 "System updated"
sleep 0.3

# STEP 2 (EXACT commands you requested)
section "STEP 2/6 — INSTALL DEPENDENCIES"
log_info "Installing python, openjdk-17, lua53..."
{
    pkg install python openjdk-17 lua53 -y
} > /dev/null 2>&1 &
spinner $! "Installing packages..."
wait $!
PY_VER=$(python --version 2>&1 | awk '{print $2}')
log_ok "Python $PY_VER, Java, Lua installed"
progress_bar 2 6 "System deps ready"
sleep 0.3

# STEP 3
section "STEP 3/6 — PIP UPGRADE"
log_info "Upgrading pip..."
{
    pip install --upgrade pip
} > /dev/null 2>&1 &
spinner $! "Upgrading pip..."
wait $!
log_ok "pip upgraded"
progress_bar 3 6 "pip upgraded"
sleep 0.3

# STEP 4 (EXACT pip install command)
section "STEP 4/6 — PYTHON MODULES"
log_info "Installing Python modules..."
{
    pip install pycryptodome zstandard gmalg requests rich psutil colorama
} > /dev/null 2>&1 &
spinner $! "Installing modules..."
wait $!
log_ok "All modules installed"
progress_bar 4 6 "Modules ready"
sleep 0.3

# STEP 5 (clone with safety)
section "STEP 5/6 — CLONE REPOSITORY"

cd "$HOME" || exit 1

if [ -d "$HOME/Yukioh_Okami_Tool" ]; then
    log_warn "Old Yukioh_Okami_Tool found"
    log_info "Deleting old folder..."
    rm -rf "$HOME/Yukioh_Okami_Tool" &
    spinner $! "Removing old tool..."
    wait $!
    log_ok "Old tool deleted"
fi

log_info "Cloning Yukioh_Okami_Tool..."
git clone https://github.com/Himesh-Shah93/Yukioh_Okami_Tool "$HOME/Yukioh_Okami_Tool" 2>&1 | while IFS= read -r line; do
    echo -e "  ${DIM}$line${NC}"
done

if [ ${PIPESTATUS[0]} -ne 0 ]; then
    log_err "Git clone failed! Retrying..."
    sleep 2
    git clone https://github.com/Himesh-Shah93/Yukioh_Okami_Tool "$HOME/Yukioh_Okami_Tool" 2>&1 | while IFS= read -r line; do
        echo -e "  ${DIM}$line${NC}"
    done
    if [ ${PIPESTATUS[0]} -ne 0 ]; then
        log_err "Clone failed after retry. Check internet."
        exit 1
    fi
fi

log_ok "Tool ready at ${CYAN}~/Yukioh_Okami_Tool${NC}"
cd "$HOME/Yukioh_Okami_Tool" || exit 1
chmod +x *.py
log_ok "Executable permissions set"
progress_bar 5 6 "Repo cloned"
sleep 0.3

# STEP 6
section "STEP 6/6 — GLOBAL COMMAND"
CMD_PATH="${PREFIX:-/usr/local}/bin/Yukioh_Okami_Tool"
cat > "$CMD_PATH" << 'CMDEOF'
#!/bin/bash

cd "$HOME/Yukioh_Okami_Tool" || exit 1

if [ -f "Yukioh_Okami.py" ]; then
    python Yukioh_Okami.py
else
    echo "Yukioh_Okami.py not found!"
    exit 1
fi
CMDEOF

chmod +x "$CMD_PATH"
log_ok "Global command created: ${CYAN}Yukioh_Okami_Tool${NC}"
progress_bar 6 6 "Installation complete"
sleep 0.3

# ---- Final Box ----
echo
box_top
box_line ""
box_line "   ✔  YUKIOH OKAMI TOOL INSTALLED SUCCESSFULLY!"
box_line ""
box_line "   HOW TO RUN:"
box_line "     ▶  Yukioh_Okami_Tool"
box_line "     ▶  cd ~/Yukioh_Okami_Tool && python Yukioh_Okami.py"
box_line ""
box_line "   INSTALLED AT:"
box_line "     ~/Yukioh_Okami_Tool"
box_line ""
box_line "   GLOBAL CMD:"
box_line "     ${PREFIX:-/usr/local}/bin/Yukioh_Okami_Tool"
box_line ""
box_line "   ⚠  Do NOT run via curl | bash"
box_line "   Interactive login required"
box_line ""
box_bottom
echo