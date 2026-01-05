/**
 * PC Gaming App - Modern JavaScript
 * Enhanced with better error handling, async/await, and performance optimizations
 */

// Configuration
const CONFIG = {
    METRICS_UPDATE_INTERVAL: 1000, // 1 second
    AUDIO_UPDATE_INTERVAL: 2000, // 2 seconds
    UPDATE_CHECK_INTERVAL: 3600000, // 1 hour (backup check, main check is on startup)
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
            const response = await fetch(endpoint, {
                method: 'GET',
                cache: 'no-cache',
                signal: AbortSignal.timeout(5000) // 5 second timeout
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            // Suppress connection errors to reduce console spam
            // Only log errors that aren't connection/timeout related
            const isConnectionError = error.name === 'TypeError' || 
                                     error.name === 'AbortError' || 
                                     error.message?.includes('Failed to fetch') ||
                                     error.message?.includes('network') ||
                                     error.message?.includes('ERR_CONNECTION');
            
            if (!isConnectionError) {
                console.error(`Error fetching ${endpoint}:`, error);
            }
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
        try {
            const data = await api.fetchMetrics('/metrics/cpu');
            if (data) {
                utils.updateElement('cpu-usage', utils.formatNumber(data.usage), '%');
                utils.updateElement('cpu-frequency-current', utils.formatNumber(data['Frequency-curent'] || data['Frequency-current']), ' MHz');
                utils.updateElement('cpu-frequency-max', utils.formatNumber(data['Frequency-max']), ' MHz');
                utils.updateElement('cpu-temperature', utils.formatNumber(data.temperature), '°C');
                state.metrics.cpu = data;
            }
        } catch (error) {
            // Silently handle errors - metrics will show "Loading..." or previous values
        }
    },

    /**
     * Fetch and update RAM metrics
     */
    async updateRAM() {
        try {
            const data = await api.fetchMetrics('/metrics/ram');
            if (data) {
                utils.updateElement('ram-usage', utils.formatNumber(data.usage), '%');
                utils.updateElement('ram-total', utils.formatNumber(data.total), ' GB');
                utils.updateElement('ram-free', utils.formatNumber(data.free), ' GB');
                state.metrics.ram = data;
            }
        } catch (error) {
            // Silently handle errors
        }
    },

    /**
     * Fetch and update Disk metrics
     */
    async updateDisk() {
        try {
            const data = await api.fetchMetrics('/metrics/disk');
            if (data) {
                utils.updateElement('disk-usage', utils.formatNumber(data.usage), '%');
                utils.updateElement('disk-free', utils.formatNumber(data.free_space), ' GB');
                utils.updateElement('disk-read', utils.formatNumber(data.read_speed), ' MB');
                utils.updateElement('disk-write', utils.formatNumber(data.write_speed), ' MB');
                state.metrics.disk = data;
            }
        } catch (error) {
            // Silently handle errors
        }
    },

    /**
     * Fetch and update GPU metrics
     */
    async updateGPU() {
        try {
            const data = await api.fetchMetrics('/metrics/gpu');
            if (data) {
                utils.updateElement('gpu-name', data.name || 'N/A');
                utils.updateElement('gpu-temperature', utils.formatNumber(data.temperature), '°C');
                utils.updateElement('gpu-utilization', utils.formatNumber(data.utilization), '%');
                utils.updateElement('gpu-memory-used', utils.formatNumber(data.memory_used), ' MB');
                utils.updateElement('gpu-memory-total', utils.formatNumber(data.memory_total), ' MB');
                state.metrics.gpu = data;
            }
        } catch (error) {
            // Silently handle errors
        }
    },

    /**
     * Update all metrics
     */
    async updateAll() {
        // Use Promise.allSettled to continue even if some fail
        await Promise.allSettled([
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
            const response = await fetch('/speed_test');
            const data = await response.json();
            
            if (response.status === 503 || (data && data.available === false)) {
                // Speed test not available
                utils.showError('speed-test', 'Speed test feature is not available in this version.');
                utils.updateElement('down-speed', 'N/A', '');
                utils.updateElement('up-speed', 'N/A', '');
                utils.updateElement('ping', 'N/A', '');
            } else if (data && !data.error && data.download_speed) {
                // Success
                utils.updateElement('down-speed', utils.formatNumber(data.download_speed), ' Mbps');
                utils.updateElement('up-speed', utils.formatNumber(data.upload_speed), ' Mbps');
                utils.updateElement('ping', utils.formatNumber(data.ping), ' ms');
                utils.showSuccess('speed-test', 'Speed test completed!', 2000);
            } else {
                // Error from server
                const errorMsg = data.error || 'Speed test failed. Please try again.';
                utils.showError('speed-test', errorMsg);
                utils.updateElement('down-speed', 'Error', '');
                utils.updateElement('up-speed', 'Error', '');
                utils.updateElement('ping', 'Error', '');
            }
        } catch (error) {
            utils.showError('speed-test', 'Network error. Please check your connection and try again.');
            utils.updateElement('down-speed', 'Error', '');
            utils.updateElement('up-speed', 'Error', '');
            utils.updateElement('ping', 'Error', '');
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
                    // Make it more visible with animation
                    updateMessage.style.animation = 'pulse 2s ease-in-out infinite';
                    console.log('Update available! Check the green message at the top.');
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

// Process Manager
const processManager = {
    currentSort: 'cpu',
    
    async loadProcesses(sortBy = 'cpu') {
        try {
            const data = await api.fetchMetrics(`/processes?sort_by=${sortBy}&limit=15`);
            if (data && data.processes) {
                this.renderProcesses(data.processes);
            }
        } catch (error) {
            console.error('Error loading processes:', error);
            document.getElementById('processes-list').innerHTML = 
                '<p style="text-align: center; color: var(--text-muted);">Error loading processes</p>';
        }
    },
    
    renderProcesses(processes) {
        const container = document.getElementById('processes-list');
        if (!processes || processes.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: var(--text-muted);">No processes found</p>';
            return;
        }
        
        const html = processes.map(proc => `
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px; margin: 5px 0; background: rgba(255,255,255,0.05); border-radius: 8px;">
                <div style="flex: 1;">
                    <div style="font-weight: bold; color: var(--text-primary);">${proc.name}</div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary);">PID: ${proc.pid}</div>
                </div>
                <div style="text-align: right; margin-right: 15px;">
                    <div style="color: var(--accent-color);">CPU: ${proc.cpu_percent}%</div>
                    <div style="color: var(--accent-color);">RAM: ${proc.memory_percent}% (${proc.memory_mb} MB)</div>
                </div>
                <button onclick="processManager.killProcess(${proc.pid}, '${proc.name}')" 
                        style="padding: 5px 10px; background: rgba(220,53,69,0.8); border: none; border-radius: 5px; color: white; cursor: pointer; font-size: 0.85rem;"
                        title="Kill Process">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `).join('');
        
        container.innerHTML = html;
    },
    
    async killProcess(pid, name) {
        if (!confirm(`Are you sure you want to kill process "${name}" (PID: ${pid})?`)) {
            return;
        }
        
        try {
            const response = await fetch('/kill_process', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pid })
            });
            const data = await response.json();
            
            if (data.status === 'success') {
                alert(data.message);
                this.loadProcesses(this.currentSort);
            } else {
                alert(data.message || 'Failed to kill process');
            }
        } catch (error) {
            alert('Error killing process');
            console.error('Kill process error:', error);
        }
    },
    
    sortBy(sortBy) {
        this.currentSort = sortBy;
        document.getElementById('sort-cpu').classList.toggle('active', sortBy === 'cpu');
        document.getElementById('sort-memory').classList.toggle('active', sortBy === 'memory');
        this.loadProcesses(sortBy);
    }
};

// System Information
const systemInfo = {
    async load() {
        try {
            const data = await api.fetchMetrics('/system_info');
            if (data && !data.error) {
                this.render(data);
            }
        } catch (error) {
            console.error('Error loading system info:', error);
            document.getElementById('system-info-content').innerHTML = 
                '<p style="text-align: center; color: var(--text-muted);">Error loading system information</p>';
        }
    },
    
    render(data) {
        const container = document.getElementById('system-info-content');
        let html = '';
        
        if (data.os) {
            html += `<div style="margin-bottom: 1rem;">
                <h3 style="font-size: 1rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                    <i class="fas fa-desktop"></i> Operating System
                </h3>
                <p><strong>System:</strong> ${data.os.system} ${data.os.release}</p>
                <p><strong>Architecture:</strong> ${data.os.architecture}</p>
                <p><strong>Processor:</strong> ${data.os.processor || data.cpu?.model || 'Unknown'}</p>
            </div>`;
        }
        
        if (data.cpu) {
            html += `<div style="margin-bottom: 1rem;">
                <h3 style="font-size: 1rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                    <i class="fas fa-microchip"></i> CPU
                </h3>
                <p><strong>Physical Cores:</strong> ${data.cpu.physical_cores}</p>
                <p><strong>Logical Cores:</strong> ${data.cpu.logical_cores}</p>
                <p><strong>Frequency:</strong> ${data.cpu.min_frequency} - ${data.cpu.max_frequency}</p>
            </div>`;
        }
        
        if (data.memory) {
            html += `<div style="margin-bottom: 1rem;">
                <h3 style="font-size: 1rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                    <i class="fas fa-memory"></i> Memory
                </h3>
                <p><strong>Total:</strong> ${data.memory.total_gb} GB</p>
                <p><strong>Available:</strong> ${data.memory.available_gb} GB</p>
            </div>`;
        }
        
        if (data.motherboard) {
            html += `<div style="margin-bottom: 1rem;">
                <h3 style="font-size: 1rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                    <i class="fas fa-server"></i> Motherboard
                </h3>
                <p><strong>Manufacturer:</strong> ${data.motherboard.manufacturer}</p>
                <p><strong>Product:</strong> ${data.motherboard.product}</p>
            </div>`;
        }
        
        container.innerHTML = html || '<p style="text-align: center; color: var(--text-muted);">No system information available</p>';
    }
};

// Network Monitor
const networkMonitor = {
    async loadStats() {
        try {
            const data = await api.fetchMetrics('/network_stats');
            if (data && !data.error) {
                utils.updateElement('network-upload-speed', data.upload_speed_mbps || '0', '');
                utils.updateElement('network-download-speed', data.download_speed_mbps || '0', '');
                utils.updateElement('network-sent', data.bytes_sent_mb || '0', '');
                utils.updateElement('network-received', data.bytes_recv_mb || '0', '');
            }
        } catch (error) {
            console.error('Error loading network stats:', error);
        }
    },
    
    async loadConnections() {
        try {
            const data = await api.fetchMetrics('/network_connections?limit=20');
            if (data && data.connections) {
                this.renderConnections(data.connections);
            }
        } catch (error) {
            console.error('Error loading connections:', error);
            document.getElementById('network-connections-list').innerHTML = 
                '<p style="text-align: center; color: var(--text-muted);">Error loading connections</p>';
        }
    },
    
    renderConnections(connections) {
        const container = document.getElementById('network-connections-list');
        if (!connections || connections.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: var(--text-muted);">No active connections</p>';
            return;
        }
        
        const html = connections.map(conn => `
            <div style="padding: 8px; margin: 3px 0; background: rgba(255,255,255,0.03); border-radius: 5px; font-size: 0.9rem;">
                <div><strong>${conn.process_name || 'Unknown'}</strong> (PID: ${conn.pid || 'N/A'})</div>
                <div style="color: var(--text-secondary); font-size: 0.85rem;">
                    ${conn.local_address} → ${conn.remote_address}
                </div>
                <div style="color: var(--accent-color); font-size: 0.8rem;">Status: ${conn.status}</div>
            </div>
        `).join('');
        
        container.innerHTML = html;
    }
};

// Make processManager globally available
window.processManager = processManager;

// Screenshot Manager
const screenshot = {
    async capture() {
        try {
            const container = document.getElementById('screenshot-container');
            
            if (!container) {
                console.error('Screenshot container not found');
                alert('Screenshot container not found');
                return;
            }
            
            container.style.display = 'block';
            container.innerHTML = '<p style="text-align: center; color: var(--text-muted); padding: 20px;"><i class="fas fa-spinner fa-spin"></i> Capturing screenshot...</p>';
            
            const data = await api.fetchMetrics('/screenshot');
            
            if (data && data.image) {
                // Create image element
                const img = document.createElement('img');
                img.id = 'screenshot-image';
                img.src = 'data:image/png;base64,' + data.image;
                img.style.maxWidth = '100%';
                img.style.borderRadius = '8px';
                img.style.border = '2px solid rgba(255,255,255,0.1)';
                img.alt = 'Screenshot';
                
                // Create download button
                const downloadBtn = document.createElement('button');
                downloadBtn.id = 'download-screenshot';
                downloadBtn.className = 'remote-button';
                downloadBtn.style.marginTop = '0.5rem';
                downloadBtn.style.width = '100%';
                downloadBtn.innerHTML = '<i class="fas fa-download"></i> Download';
                downloadBtn.addEventListener('click', () => screenshot.download());
                
                // Update container
                container.innerHTML = '';
                container.appendChild(img);
                container.appendChild(downloadBtn);
            } else if (data && !data.available) {
                container.innerHTML = `<p style="text-align: center; color: var(--text-muted); padding: 20px;">${data.error || 'Screenshot feature not available'}</p>`;
            } else if (data && data.error) {
                container.innerHTML = `<p style="text-align: center; color: var(--text-muted); padding: 20px;">Error: ${data.error}</p>`;
            } else {
                container.innerHTML = '<p style="text-align: center; color: var(--text-muted); padding: 20px;">Failed to capture screenshot. Please try again.</p>';
            }
        } catch (error) {
            const container = document.getElementById('screenshot-container');
            if (container) {
                container.innerHTML = `<p style="text-align: center; color: var(--text-muted); padding: 20px;">Error: ${error.message || 'Failed to capture screenshot'}</p>`;
            }
            console.error('Screenshot error:', error);
        }
    },
    
    download() {
        const img = document.getElementById('screenshot-image');
        if (!img || !img.src) {
            alert('No screenshot available to download. Please capture a screenshot first.');
            return;
        }
        
        try {
            const link = document.createElement('a');
            link.href = img.src;
            link.download = `screenshot-${Date.now()}.png`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } catch (error) {
            console.error('Download error:', error);
            alert('Failed to download screenshot. You can right-click the image and save it manually.');
        }
    }
};

// Clipboard Manager
const clipboard = {
    async load() {
        try {
            const data = await api.fetchMetrics('/clipboard');
            if (data && data.content !== undefined) {
                document.getElementById('clipboard-content').textContent = data.content || '(empty)';
            }
        } catch (error) {
            console.error('Error loading clipboard:', error);
            document.getElementById('clipboard-content').textContent = 'Error loading clipboard';
        }
    },
    
    async set() {
        const text = document.getElementById('clipboard-input').value;
        try {
            const response = await fetch('/clipboard', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            const data = await response.json();
            if (data.status === 'success') {
                alert('Clipboard updated!');
                this.load();
                document.getElementById('clipboard-input').value = '';
            } else {
                alert('Failed to set clipboard');
            }
        } catch (error) {
            alert('Error setting clipboard');
            console.error('Set clipboard error:', error);
        }
    }
};

// App Launcher
const appLauncher = {
    async loadCommonApps() {
        try {
            const data = await api.fetchMetrics('/apps/common');
            if (data && data.apps) {
                const container = document.getElementById('common-apps');
                container.innerHTML = data.apps.map(app => `
                    <button onclick="appLauncher.launch('${app.path.replace(/'/g, "\\'")}')" 
                            class="remote-button" style="font-size: 0.85rem; padding: 8px;">
                        <i class="fas fa-play"></i> ${app.name}
                    </button>
                `).join('');
            }
        } catch (error) {
            console.error('Error loading apps:', error);
        }
    },
    
    async launch(appPath) {
        try {
            const response = await fetch('/apps/launch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ app: appPath })
            });
            const data = await response.json();
            if (data.status === 'success') {
                alert(data.message);
            } else {
                alert(data.message || 'Failed to launch app');
            }
    } catch (error) {
            alert('Error launching app');
            console.error('Launch app error:', error);
        }
    },
    
    launchCustom() {
        const appPath = document.getElementById('custom-app-input').value;
        if (appPath) {
            this.launch(appPath);
            document.getElementById('custom-app-input').value = '';
        }
    }
};

// File Explorer
const fileExplorer = {
    currentPath: '~',
    
    async load(path = null) {
        if (!path) path = this.currentPath;
        try {
            const data = await api.fetchMetrics(`/files/list?path=${encodeURIComponent(path)}`);
            if (data && data.items) {
                this.currentPath = data.path;
                document.getElementById('file-explorer-path').value = data.path;
                this.render(data.items);
            }
        } catch (error) {
            console.error('Error loading files:', error);
            document.getElementById('file-explorer-list').innerHTML = 
                '<p style="text-align: center; color: var(--text-muted);">Error loading files</p>';
        }
    },
    
    render(items) {
        const container = document.getElementById('file-explorer-list');
        const breadcrumb = document.getElementById('breadcrumb-path');
        
        if (!items || items.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: var(--text-muted); padding: 20px;">Empty directory</p>';
            return;
        }
        
        // Update breadcrumb
        if (breadcrumb) {
            breadcrumb.textContent = this.currentPath || '~';
            // Make sure breadcrumb container is visible
            const breadcrumbContainer = document.getElementById('file-explorer-breadcrumb');
            if (breadcrumbContainer) {
                breadcrumbContainer.style.display = 'flex';
            }
        }
        
        const html = items.map(item => {
            const icon = item.is_dir ? 'fa-folder' : 'fa-file';
            const iconColor = item.is_dir ? '#4CAF50' : '#2196F3';
            const size = item.is_dir ? 'Folder' : this.formatSize(item.size);
            const itemPath = item.path.replace(/'/g, "\\'").replace(/"/g, '&quot;');
            const itemName = item.name.replace(/'/g, "\\'").replace(/"/g, '&quot;');
            
            // Use data attributes for better security and mobile support
            return `
                <div class="file-explorer-item" 
                     data-path="${itemPath}"
                     data-is-dir="${item.is_dir}"
                     data-name="${itemName}">
                    <i class="fas ${icon} file-explorer-item-icon" style="color: ${iconColor};"></i>
                    <div class="file-explorer-item-info">
                        <div class="file-explorer-item-name">${itemName}</div>
                        <div class="file-explorer-item-details">${size}</div>
                    </div>
                    ${!item.is_dir ? '<i class="fas fa-download file-explorer-item-action"></i>' : '<i class="fas fa-chevron-right file-explorer-item-action"></i>'}
                </div>
            `;
        }).join('');
        
        container.innerHTML = html;
        
        // Add click event listeners to all items
        container.querySelectorAll('.file-explorer-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const path = item.getAttribute('data-path');
                const isDir = item.getAttribute('data-is-dir') === 'true';
                
                if (isDir) {
                    this.load(path);
                } else {
                    this.download(path);
                }
            });
        });
    },
    
    formatSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
        return (bytes / (1024 * 1024 * 1024)).toFixed(1) + ' GB';
    },
    
    download(filePath) {
        window.open(`/files/download?path=${encodeURIComponent(filePath)}`, '_blank');
    },
    
    goToPath() {
        const path = document.getElementById('file-explorer-path').value;
        this.load(path);
    },
    
    goBack() {
        const current = this.currentPath;
        
        // Get parent directory by removing the last part
        const parts = current.split(/[/\\]/).filter(p => p);
        
        // If we're at root or only one level deep, go to home
        if (parts.length <= 1) {
            this.load('~');
            return;
        }
        
        // Remove last part to get parent
        parts.pop();
        const parent = parts.length > 0 ? parts.join('/') : '/';
        this.load(parent);
    },
    
    goHome() {
        this.load('~');
    }
};

// Make functions globally available
window.screenshot = screenshot;
window.clipboard = clipboard;
window.appLauncher = appLauncher;
window.fileExplorer = fileExplorer;

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Display app version
    displayAppVersion();
    
    // Wait a moment for server to be ready, then start metrics updates
    setTimeout(() => {
        metrics.updateAll();
        setInterval(() => metrics.updateAll(), CONFIG.METRICS_UPDATE_INTERVAL);
    }, 1000); // Wait 1 second for server to be ready
    
    // Start audio controls updates
    audio.updateControls();
    setInterval(() => audio.updateControls(), CONFIG.AUDIO_UPDATE_INTERVAL);
    
    // Check for updates on startup
    updater.checkForUpdates();
    
    // Also check periodically (every 1 hour) as backup
    setInterval(() => updater.checkForUpdates(), CONFIG.UPDATE_CHECK_INTERVAL);
    
    // Initialize remote control features
    clipboard.load();
    appLauncher.loadCommonApps();
    fileExplorer.load('~');
    
    // Set up remote control event listeners
    const takeScreenshotBtn = document.getElementById('take-screenshot');
    if (takeScreenshotBtn) {
        takeScreenshotBtn.addEventListener('click', () => screenshot.capture());
    }
    
    // Download screenshot button will be added dynamically after screenshot is taken
    document.getElementById('set-clipboard').addEventListener('click', () => clipboard.set());
    document.getElementById('refresh-clipboard').addEventListener('click', () => clipboard.load());
    document.getElementById('launch-custom-app').addEventListener('click', () => appLauncher.launchCustom());
    const fileExplorerGo = document.getElementById('file-explorer-go');
    const fileExplorerBack = document.getElementById('file-explorer-back');
    const fileExplorerHome = document.getElementById('file-explorer-home');
    
    if (fileExplorerGo) {
        fileExplorerGo.addEventListener('click', () => fileExplorer.goToPath());
    }
    if (fileExplorerBack) {
        fileExplorerBack.addEventListener('click', () => fileExplorer.goBack());
    }
    if (fileExplorerHome) {
        fileExplorerHome.addEventListener('click', () => fileExplorer.goHome());
    }
    
    // Allow Enter key in inputs
    document.getElementById('custom-app-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') appLauncher.launchCustom();
    });
    document.getElementById('file-explorer-path').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') fileExplorer.goToPath();
    });
    
    // Load new features
    processManager.loadProcesses('cpu');
    systemInfo.load();
    networkMonitor.loadStats();
    networkMonitor.loadConnections();
    
    // Update new features periodically
    setInterval(() => networkMonitor.loadStats(), 2000);
    setInterval(() => networkMonitor.loadConnections(), 10000);
    setInterval(() => processManager.loadProcesses(processManager.currentSort), 5000);
    
    // Add click handler for update message
    const updateMessage = document.getElementById('update-message');
    if (updateMessage) {
        updateMessage.addEventListener('click', () => {
            updater.updateApp();
        });
    }
    
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
    
    // Exit app button
    document.getElementById('exit-app').addEventListener('click', () => {
        system.showConfirmation(
            '🚪 Close the application? This will terminate the Monitor.exe process.',
            async () => {
                try {
                    // Send exit request - the server will terminate itself
                    await fetch('/exit', { method: 'POST' });
                    // Show message while waiting for exit
                    alert('Application is closing...');
                } catch (error) {
                    // Even if request fails, the server might still be closing
                    console.error('Error closing app:', error);
                    // Try to close window as fallback
                    setTimeout(() => {
                        window.close();
                    }, 1000);
                }
            }
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
