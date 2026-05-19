# Copies files to appropriate system locations and enabled systemd timer

BIN_DIR    := $(HOME)/.local/bin
SYSTEMD_DIR := $(HOME)/.config/systemd/user

.PHONY: all install

all: install

install:
	mkdir -p $(BIN_DIR) $(SYSTEMD_DIR)
	cp ./borg-runner.sh $(BIN_DIR)/borg-runner.sh
	chmod +x $(BIN_DIR)/borg-runner.sh
	cp ./systemd/* $(SYSTEMD_DIR)/

	systemctl --user daemon-reload
	systemctl --user enable --now borg-runner.timer
