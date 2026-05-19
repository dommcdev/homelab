#!/usr/bin/env bash
set -euo pipefail

export BORG_CACHE_DIR="$HOME/.cache/borg"
CURRENT_DAY=$(date +%u) # 1 = Monday, 7 = Sunday

# Retention format: keep-daily, keep-weekly, keep-monthly

echo "=== Starting Borg Backup Suite: $(date) ==="

profile_files() {
    SOURCE_DIR="$HOME/files"
    RETENTION=(7 4 6)
    declare -A TARGETS=(
        ["local-raid"]="/mnt/storage/backups/files-backup"
        ["remote-kabigon"]="ssh://kabigon/mnt/storage/backups/files-backup"
    )
    run_backup_pipeline "Files" "$SOURCE_DIR" RETENTION TARGETS
}

profile_photos() {
    SOURCE_DIR="$HOME/photos"
    RETENTION=(14 8 12) # Photos get a longer historical net
    declare -A TARGETS=(
        ["local-raid"]="/mnt/storage/backups/photos-backup"
#        ["remote-kabigon"]="ssh://kabigon/mnt/storage/backups/photos-backup"
    )
    run_backup_pipeline "Photos" "$SOURCE_DIR" RETENTION TARGETS
}

run_backup_pipeline() {
    local category="$1"
    local source="$2"
    local -n retention_ref="$3"
    local -n targets_ref="$4"

    echo "=================================================================="
    echo "Processing: [$category]"
    echo "Source Path: $source"
    echo "=================================================================="

    if [ ! -d "$source" ]; then
        echo "--> [ERROR] Source directory $source does not exist. Skipping category."
        return
    fi

    for REPO_NAME in "${!targets_ref[@]}"; do
        local repo_uri="${targets_ref[$REPO_NAME]}"
        echo "--------------------------------------------------"
        echo "Target Endpoint: [$REPO_NAME]"

        # --- Network Verification Check ---
        if [[ "$repo_uri" =~ ssh://([^@]+@)?([^/:]+) ]]; then
            local remote_host="${BASH_REMATCH[2]}"
            if ! ping -c 1 -W 2 "$remote_host" &>/dev/null; then
                echo "--> [SKIP] $remote_host is offline. Network target skipped."
                continue
            fi
            echo "--> Remote node is reachable."
        else
            echo "--> Local file path target."
        fi

        # --- Create Backup ---
        echo "--> Action: Generating incremental archive..."
        borg create --stats "$repo_uri::{hostname}-$category-%%Y-%%m-%%d" "$source"

        # --- Prune According to Profile Grid ---
        echo "--> Action: Applying retention policy..."
        borg prune -v --list \
            --keep-daily="${retention_ref[0]}" \
            --keep-weekly="${retention_ref[1]}" \
            --keep-monthly="${retention_ref[2]}" \
            "$repo_uri"

        # --- Weekly Structural Compaction ---
        if [ "$CURRENT_DAY" -eq 7 ]; then
            echo "--> Action: Compacting storage segments..."
            borg compact "$repo_uri"
        fi
    done
}

# Call profiles here
profile_files
profile_photos

echo "=== Backup Suite Finished Successfully ==="
