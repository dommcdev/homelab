# Copies files to appropriate system locations and enabled systemd timer

BIN_DIR     := $(HOME)/.local/bin
SYSTEMD_DIR := $(HOME)/.config/systemd/user

.PHONY: all install

all: install

install:
	@echo "Creating symlinks for Borg backup configuration..."
	mkdir -p $(BIN_DIR) $(SYSTEMD_DIR)

	chmod +x $(CURDIR)/borg-runner.sh
	ln -sf $(CURDIR)/borg-runner.sh $(BIN_DIR)/borg-runner.sh

	for file in $(CURDIR)/systemd/*; do \
		ln -sf $$file $(SYSTEMD_DIR)/; \
	done

	systemctl --user daemon-reload
	systemctl --user enable --now borg-runner.timer

#borg init --encryption=repokey-blake2 ssh://kabigon/mnt/storage/backups/files-backup
#borg init --encryption=repokey-blake2 /mnt/storage/backups/files-backup
