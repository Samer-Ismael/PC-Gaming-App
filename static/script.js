/**
 * PC Gaming App - Modern JavaScript
 * Enhanced with better error handling, async/await, and performance optimizations
 */

// Configuration
const CONFIG = {
    METRICS_UPDATE_INTERVAL: 1000, // 1 second
    AUDIO_UPDATE_INTERVAL: 2000, // 2 seconds
    UPDATE_CHECK_INTERVAL: 900000, // 15 minutes
    ANIMATION_DURATION: 500
};

// State management
const state = {
    metrics: {
        cpu: {},
        ram: {},
        disk: {},
        gpu: {}
    },
    isSpeedTestRunning: false
};

// Utility functions
const utils = {
    /**
     * Update element text with animation
     */
    updateElement(id, value, suffix = '') {
        const element = document.getElementById(id);
        if (!element) return;
        
        const currentValue = element.textContent.replace(suffix, '').trim();
        const newValue = String(value) + suffix;
        
        if (currentValue !== newValue.replace(suffix, '').trim()) {
            element.classList.add('updated');
            element.textContent = newValue;
            
            setTimeout(() => {
                element.classList.remove('updated');
            }, CONFIG.ANIMATION_DURATION);
        } else {
            element.textContent = newValue;
        }
    },

    /**
     * Format number with proper decimals
     */
    formatNumber(value, decimals = 2) {
        if (value === null || value === undefined || value === 'Unavailable' || value === 'N/A') {
            return 'N/A';
        }
        const num = parseFloat(value);
        return isNaN(num) ? 'N/A' : num.toFixed(decimals);
    },

    /**
     * Show loading message
     */
    showLoading(id, message) {
        const element = document.getElementById(id);
        if (element) {
            element.style.display = 'block';
            element.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${message}`;
        }
    },

    /**
     * Hide loading message
     */
    hideLoading(id) {
        const element = document.getElementById(id);
        if (element) {
            element.style.display = 'none';
        }
    },

    /**
     * Show success message
     */
    showSuccess(id, message, duration = 2000) {
        const element = document.getElementById(id);
        if (element) {
            element.style.display = 'block';
            element.innerHTML = `<i class="fas fa-check-circle"></i> ${message}`;
            element.style.color = '#38ef7d';
            
            setTimeout(() => {
                this.hideLoading(id);
            }, duration);
        }
    },

    /**
     * Show error message
     */
    showError(id, message) {
        const element = document.getElementById(id);
        if (element) {
            element.style.display = 'block';
            element.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
            element.style.color = '#ee0979';
        }
    }
};

// API functions
const api = {
    /**
     * Fetch metrics with error handling
     */
    async fetchMetrics(endpoint) {
        try {
            const response = await fetch(endpoint);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`Error fetching ${endpoint}:`, error);
            return null;
        }
    },

    /**
     * Send POST request
     */
    async postRequest(endpoint, data = {}) {
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            return await response.json();
        } catch (error) {
            console.error(`Error posting to ${endpoint}:`, error);
            throw error;
        }
    }
};

// Metrics fetching
const metrics = {
    /**
     * Fetch and update CPU metrics
     */
    async updateCPU() {
        const data = await api.fetchMetrics('/metrics/cpu');
        if (data) {
            utils.updateElement('cpu-usage', utils.formatNumber(data.usage), '%');
            utils.updateElement('cpu-frequency-current', utils.formatNumber(data['Frequency-curent'] || data['Frequency-current']), ' MHz');
            utils.updateElement('cpu-frequency-max', utils.formatNumber(data['Frequency-max']), ' MHz');
            utils.updateElement('cpu-temperature', utils.formatNumber(data.temperature), '°C');
            state.metrics.cpu = data;
        }
    },

    /**
     * Fetch and update RAM metrics
     */
    async updateRAM() {
        const data = await api.fetchMetrics('/metrics/ram');
        if (data) {
            utils.updateElement('ram-usage', utils.formatNumber(data.usage), '%');
            utils.updateElement('ram-total', utils.formatNumber(data.total), ' GB');
            utils.updateElement('ram-free', utils.formatNumber(data.free), ' GB');
            state.metrics.ram = data;
        }
    },

    /**
     * Fetch and update Disk metrics
     */
    async updateDisk() {
        const data = await api.fetchMetrics('/metrics/disk');
        if (data) {
            utils.updateElement('disk-usage', utils.formatNumber(data.usage), '%');
            utils.updateElement('disk-free', utils.formatNumber(data.free_space), ' GB');
            utils.updateElement('disk-read', utils.formatNumber(data.read_speed), ' MB');
            utils.updateElement('disk-write', utils.formatNumber(data.write_speed), ' MB');
            state.metrics.disk = data;
        }
    },

    /**
     * Fetch and update GPU metrics
     */
    async updateGPU() {
        const data = await api.fetchMetrics('/metrics/gpu');
        if (data) {
            utils.updateElement('gpu-name', data.name || 'N/A');
            utils.updateElement('gpu-temperature', utils.formatNumber(data.temperature), '°C');
            utils.updateElement('gpu-utilization', utils.formatNumber(data.utilization), '%');
            utils.updateElement('gpu-memory-used', utils.formatNumber(data.memory_used), ' MB');
            utils.updateElement('gpu-memory-total', utils.formatNumber(data.memory_total), ' MB');
            state.metrics.gpu = data;
        }
    },

    /**
     * Update all metrics
     */
    async updateAll() {
        await Promise.all([
            this.updateCPU(),
            this.updateRAM(),
            this.updateDisk(),
            this.updateGPU()
        ]);
    }
};

// Speed test
const speedTest = {
    async run() {
        if (state.isSpeedTestRunning) return;
        
        state.isSpeedTestRunning = true;
        utils.showLoading('speed-test', 'Please wait, testing the connection...');
        
        // Reset values
        utils.updateElement('down-speed', '—', ' Mbps');
        utils.updateElement('up-speed', '—', ' Mbps');
        utils.updateElement('ping', '—', ' ms');
        
        try {
            const data = await api.fetchMetrics('/speed_test');
            
            if (data && !data.error) {
                utils.updateElement('down-speed', utils.formatNumber(data.download_speed), ' Mbps');
                utils.updateElement('up-speed', utils.formatNumber(data.upload_speed), ' Mbps');
                utils.updateElement('ping', utils.formatNumber(data.ping), ' ms');
                utils.showSuccess('speed-test', 'Speed test completed!', 2000);
            } else {
                utils.showError('speed-test', 'Speed test failed. Please try again.');
            }
        } catch (error) {
            utils.showError('speed-test', 'Error running speed test.');
            console.error('Speed test error:', error);
        } finally {
            state.isSpeedTestRunning = false;
        }
    }
};

// Audio controls
const audio = {
    /**
     * Update volume controls
     */
    async updateControls() {
        try {
            const data = await api.fetchMetrics('/get_audio_sessions');
            if (!data || !data.sessions) return;
            
            const container = document.getElementById('volume-controls-container');
            if (!container) return;
            
            if (data.sessions.length === 0) {
                container.innerHTML = '<p style="text-align: center; color: var(--text-muted);">No active audio sessions</p>';
                return;
            }
            
            container.innerHTML = data.sessions.map(session => `
                <div class="volume-buttons">
                    <i class="${session.icon} pc-icon"></i>
                    <span style="flex: 1; color: var(--text-primary); font-weight: 500;">${session.name}</span>
                    <span style="color: var(--text-secondary); font-size: 0.9rem; margin-right: 0.5rem;">${Math.round(session.volume || 0)}%</span>
                    <button onclick="audio.adjustVolume('${session.name}', 0.1)" title="Increase">
                        <i class="fas fa-plus"></i>
                    </button>
                    <button onclick="audio.adjustVolume('${session.name}', -0.1)" title="Decrease">
                        <i class="fas fa-minus"></i>
                    </button>
                    <button onclick="audio.toggleMute('${session.name}', ${session.muted})" title="${session.muted ? 'Unmute' : 'Mute'}">
                        <i class="fas fa-${session.muted ? 'volume-mute' : 'volume-up'}"></i>
                    </button>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error updating audio controls:', error);
        }
    },

    /**
     * Adjust volume for an app
     */
    async adjustVolume(appName, delta) {
        try {
            const sessions = await api.fetchMetrics('/get_audio_sessions');
            const session = sessions?.sessions?.find(s => s.name === appName);
            
            if (!session) return;
            
            const currentVolume = (session.volume || 0) / 100;
            const newVolume = Math.max(0, Math.min(1, currentVolume + delta));
            
            await api.postRequest('/set_volume', {
                app_name: appName,
                level: newVolume
            });
            
            // Refresh controls
            setTimeout(() => this.updateControls(), 300);
        } catch (error) {
            console.error('Error adjusting volume:', error);
        }
    },

    /**
     * Toggle mute for an app
     */
    async toggleMute(appName, currentMuted) {
        try {
            await api.postRequest('/set_volume', {
                app_name: appName,
                level: currentMuted ? 0.5 : 0
            });
            
            // Refresh controls
            setTimeout(() => this.updateControls(), 300);
        } catch (error) {
            console.error('Error toggling mute:', error);
        }
    }
};

// System actions
const system = {
    /**
     * Show confirmation modal
     */
    showConfirmation(message, onConfirm) {
        const modal = document.createElement('div');
        modal.classList.add('modal-overlay');
        
        modal.innerHTML = `
            <div class="modal">
                <p>${message}</p>
                <div class="modal-buttons">
                    <button class="yes-button" id="confirm-yes">Yes</button>
                    <button class="no-button" id="confirm-no">No</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        document.getElementById('confirm-yes').addEventListener('click', () => {
            onConfirm();
            document.body.removeChild(modal);
        });
        
        document.getElementById('confirm-no').addEventListener('click', () => {
            document.body.removeChild(modal);
        });
    },

    /**
     * Execute system action
     */
    async executeAction(endpoint, actionName) {
        try {
            await api.postRequest(endpoint);
            alert(`${actionName} initiated successfully!`);
        } catch (error) {
            alert(`Failed to ${actionName.toLowerCase()}. Please try again.`);
            console.error(`Error executing ${actionName}:`, error);
        }
    }
};

// Media commands
function sendCommand(command) {
    api.postRequest(`/media/${command}`)
        .then(data => {
            console.log(`Media command ${command} executed:`, data);
        })
        .catch(error => {
            console.error(`Error executing media command:`, error);
        });
}

// Update check
const updater = {
    async checkForUpdates() {
        try {
            const response = await fetch('/check-update');
            if (!response.ok) {
                return; // Silently fail if check fails
            }
            
            const data = await response.json();
            const updateMessage = document.getElementById('update-message');
            
            // Only show message if update is actually available (boolean true)
            if (updateMessage) {
                if (data === true) {
                    updateMessage.style.display = 'block';
                } else {
                    updateMessage.style.display = 'none';
                }
            }
        } catch (error) {
            // Silently fail - don't spam console with update check errors
            // console.error('Error checking for updates:', error);
        }
    },

    async updateApp() {
        try {
            const response = await api.postRequest('/update');
            alert(response.status || 'Update initiated. The app will restart.');
        } catch (error) {
            alert('An error occurred while updating the app.');
            console.error('Update error:', error);
        }
    }
};

// Cache clearing
const cache = {
    async clearCache() {
        utils.showLoading('loading-message', 'Please wait, clearing memory...');
        
        try {
            const response = await fetch('/clear_cache', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();
            
            if (data.status === 'success') {
                utils.showSuccess('loading-message', data.message || 'Memory cleared successfully!', 3000);
            } else {
                let errorMsg = data.message || 'Failed to clear memory.';
                if (data.requires_admin) {
                    errorMsg += ' Please run the application as administrator.';
                }
                utils.showError('loading-message', errorMsg);
            }
        } catch (error) {
            utils.showError('loading-message', 'An error occurred while clearing memory.');
            console.error('Error clearing cache:', error);
        }
    },

    async clearTempFiles() {
        utils.showLoading('disk-loading-message', 'Please wait, clearing temporary files...');
        
        try {
            const response = await fetch('/clear_temp_files', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();
            
            if (data.status === 'success') {
                const message = data.message || 'Temporary files cleared successfully!';
                utils.showSuccess('disk-loading-message', message, 3000);
            } else {
                utils.showError('disk-loading-message', data.message || 'Failed to clear temporary files.');
            }
        } catch (error) {
            utils.showError('disk-loading-message', 'An error occurred while clearing temp files.');
            console.error('Error clearing temp files:', error);
        }
    }
};

// App version
async function displayAppVersion() {
    try {
        const data = await api.fetchMetrics('/get-app-version');
        if (data && data.version) {
            document.getElementById('app-version').textContent = `App Version: ${data.version}`;
        }
    } catch (error) {
        console.error('Error fetching app version:', error);
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Display app version
    displayAppVersion();
    
    // Start metrics updates
    metrics.updateAll();
    setInterval(() => metrics.updateAll(), CONFIG.METRICS_UPDATE_INTERVAL);
    
    // Start audio controls updates
    audio.updateControls();
    setInterval(() => audio.updateControls(), CONFIG.AUDIO_UPDATE_INTERVAL);
    
    // Check for updates
    updater.checkForUpdates();
    setInterval(() => updater.checkForUpdates(), CONFIG.UPDATE_CHECK_INTERVAL);
    
    // System action buttons
    document.getElementById('off').addEventListener('click', () => {
        system.showConfirmation(
            '⚠️ Are you sure you want to shutdown your system? This action cannot be undone.',
            () => system.executeAction('/shutdown', 'Shutdown')
        );
    });
    
    document.getElementById('restart').addEventListener('click', () => {
        system.showConfirmation(
            '🔄 Are you sure you want to restart your system? All unsaved work will be lost.',
            () => system.executeAction('/restart', 'Restart')
        );
    });
    
    document.getElementById('logout').addEventListener('click', () => {
        system.showConfirmation(
            '🚪 Are you sure you want to logout? Make sure you saved your work!',
            () => system.executeAction('/logout', 'Logout')
        );
    });
    
    document.getElementById('Lock').addEventListener('click', () => {
        system.showConfirmation(
            '🔒 Lock your computer?',
            () => system.executeAction('/lock', 'Lock')
        );
    });
    
    // Cache clearing
    document.getElementById('clear-cache').addEventListener('click', () => {
        cache.clearCache();
    });
    
    document.getElementById('clear-temp-files').addEventListener('click', () => {
        cache.clearTempFiles();
    });
    
    // Speed test
    document.getElementById('start-speed-test').addEventListener('click', () => {
        speedTest.run();
    });
});

// Make functions globally available
window.sendCommand = sendCommand;
window.audio = audio;
