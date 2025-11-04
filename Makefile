# =====================================================
# AirPol SIM7000 - Makefile
# Air pollution monitoring device with SIM7000 modem
# =====================================================

.ONESHELL:
.DEFAULT_GOAL := help

# =====================================================
# Configuration Variables
# =====================================================
PROJECT_NAME := airpol-sim7000

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
MAGENTA := \033[0;35m
CYAN := \033[0;36m
NC := \033[0m # No Color

# =====================================================
# Development Commands
# =====================================================

.PHONY: install
install: ## Install firmware to RPI-RP2 device
	@echo "$(GREEN)Installing firmware to device...$(NC)"
	@DEVICE=$$(lsblk -o NAME,LABEL -ln | grep RPI-RP2 | awk '{print $$1}' | sed 's/^└─//' | sed 's/^/\/dev\//' | head -1); \
	if [ -z "$$DEVICE" ]; then \
		echo "$(RED)RPI-RP2 device not found! Is it connected in bootloader mode?$(NC)"; \
		exit 1; \
	fi; \
	echo "$(GREEN)Found device: $$DEVICE$(NC)"; \
	MOUNT_POINT=$$(lsblk -n -o MOUNTPOINT $$DEVICE | grep -v '^$$'); \
	if [ -z "$$MOUNT_POINT" ]; then \
		echo "$(YELLOW)Device not mounted, mounting...$(NC)"; \
		udisksctl mount -b $$DEVICE >/dev/null 2>&1 || true; \
		MOUNT_POINT=$$(lsblk -n -o MOUNTPOINT $$DEVICE | grep -v '^$$'); \
	fi; \
	if [ -z "$$MOUNT_POINT" ]; then \
		echo "$(RED)Failed to mount device!$(NC)"; \
		exit 1; \
	fi; \
	echo "$(GREEN)Mounted at: $$MOUNT_POINT$(NC)"; \
	echo "$(GREEN)Copying firmware file...$(NC)"; \
	sudo cp firmware/rp2_230719_ckldiv_2.uf2 "$$MOUNT_POINT/" && \
	echo "$(GREEN)Firmware copied, syncing...$(NC)"; \
	sync; \
	echo "$(YELLOW)Unmounting device...$(NC)"; \
	udisksctl unmount -b $$DEVICE >/dev/null 2>&1 || sudo umount "$$MOUNT_POINT" 2>/dev/null || true; \
	echo "$(YELLOW)Rebooting device...$(NC)"; \
	sleep 1; \
	echo "$(GREEN)Firmware installed successfully! Device will reboot.$(NC)"

.PHONY: monitor
monitor: ## Monitor serial output from device
	@echo "$(CYAN)Detecting MicroPython device...$(NC)"
	@DEVICE=$$(mpremote connect list 2>/dev/null | grep -i "MicroPython" | head -1 | awk '{print $$1}'); \
	if [ -z "$$DEVICE" ]; then \
		echo "$(RED)No MicroPython device found! Is the device connected?$(NC)"; \
		exit 1; \
	fi; \
	echo "$(GREEN)Found device: $$DEVICE$(NC)"; \
	echo "$(CYAN)Starting serial monitor...$(NC)"; \
	mpremote connect $$DEVICE


.PHONY: upload
upload: ## Upload main.py and src/ contents to device
	@echo "$(CYAN)Detecting MicroPython device...$(NC)"
	@DEVICE=$$(mpremote connect list 2>/dev/null | grep -i "MicroPython" | head -1 | awk '{print $$1}'); \
	if [ -z "$$DEVICE" ]; then \
		echo "$(RED)No MicroPython device found! Is the device connected?$(NC)"; \
		exit 1; \
	fi; \
	echo "$(GREEN)Found device: $$DEVICE$(NC)"; \
	echo "$(CYAN)Uploading files to device...$(NC)"; \
	if [ -f "main.py" ]; then \
		echo "$(YELLOW)Uploading main.py to root...$(NC)"; \
		mpremote connect $$DEVICE fs cp main.py :/ || exit 1; \
	fi; \
	if [ -d "src" ]; then \
		echo "$(YELLOW)Uploading src/ directory...$(NC)"; \
		mpremote connect $$DEVICE fs cp -r src :/ || exit 1; \
	fi; \
	echo "$(GREEN)All files uploaded successfully!$(NC)"

# =====================================================
# Help & Documentation
# =====================================================
.PHONY: help
help: ## Show this help message
	@echo "$(BLUE)═══════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)  $(PROJECT_NAME) - Makefile Commands$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(YELLOW)Development:$(NC)"
	@awk 'BEGIN {FS = ":.*##"; printf ""} /^[a-zA-Z_-]+:.*?##/ { if ($$1 ~ /^(monitor|install|run)/) printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)Production:$(NC)"
	@awk 'BEGIN {FS = ":.*##"; printf ""} /^[a-zA-Z_-]+:.*?##/ { if ($$1 ~ /^(upload)/) printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(BLUE)For detailed information, see README.md$(NC)"