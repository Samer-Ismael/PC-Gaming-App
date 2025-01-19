

function fetchMetrics() {
    fetch('/metrics')
        .then(response => response.json())
        .then(data => {
            document.getElementById('cpu-usage').textContent = data.cpu.usage;
            document.getElementById('cpu-frequency-current').textContent = `${data.cpu["Frequency-curent"]}`;
            document.getElementById('cpu-frequency-max').textContent = `${data.cpu["Frequency-max"]}`;
            document.getElementById('cpu-temperature').textContent = data.cpu.temperature;
            document.getElementById('ram-usage').textContent = data.ram.usage;
            document.getElementById('ram-total').textContent = data.ram.total;
            document.getElementById('ram-free').textContent = data.ram.free;
            document.getElementById('disk-usage').textContent = data.disk.usage;
            document.getElementById('disk-free').textContent = data.disk.free_space;
            document.getElementById('gpu-name').textContent = data.gpu.name;
            document.getElementById('gpu-temperature').textContent = data.gpu.temperature;
            document.getElementById('gpu-utilization').textContent = data.gpu.utilization;
        })
        .catch(error => console.error('Error fetching metrics:', error));
}

setInterval(fetchMetrics, 1000);  

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('increase-volume').addEventListener('click', () => {
        fetch('/volume/increase', { method: 'POST' })
            .then(response => response.json())
            .then(data => console.log(data.message))
            .catch(error => console.error('Error:', error));
    });

    document.getElementById('decrease-volume').addEventListener('click', () => {
        fetch('/volume/decrease', { method: 'POST' })
            .then(response => response.json())
            .then(data => console.log(data.message))
            .catch(error => console.error('Error:', error));
    });

    document.getElementById('mute').addEventListener('click', () => {
        fetch('/volume/mute', { method: 'POST' })
            .then(response => response.json())
            .then(data => console.log(data.message))
            .catch(error => console.error('Error:', error));
    });

    document.getElementById('unmute').addEventListener('click', () => {
        fetch('/volume/unmute', { method: 'POST' })
            .then(response => response.json())
            .then(data => console.log(data.message))
            .catch(error => console.error('Error:', error));
    });
});

document.getElementById("clear-cache").addEventListener("click", () => {
    const loadingMessage = document.getElementById("loading-message");

    loadingMessage.style.display = "block";
    loadingMessage.textContent = "Please wait, clearing memory..."; 

    fetch("/clear_cache", { method: "POST" })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                loadingMessage.textContent = "Cleaning Done!";
                
                setTimeout(() => {
                    loadingMessage.style.display = "none";
                }, 2000);
            } else {
                alert(data.message || "Failed to clear memory.");
                loadingMessage.style.display = "none";
            }
        })
        .catch(err => {
            loadingMessage.style.display = "none"; 

            console.error("Error clearing cache:", err);
            alert("An error occurred while clearing memory.");
        });
});


document.getElementById("clear-temp-files").addEventListener("click", () => {
    const diskLoadingMessage = document.getElementById("disk-loading-message");
    diskLoadingMessage.style.display = "block";
    diskLoadingMessage.textContent = "Please wait, clearing temporary files..."; 

    fetch("/clear_temp_files", { method: "POST" })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                diskLoadingMessage.textContent = "Temporary files cleared successfully!";
                setTimeout(() => {
                    diskLoadingMessage.style.display = "none";
                }, 2000);
            } else {
                diskLoadingMessage.textContent = "Failed to clear temporary files.";
                setTimeout(() => {
                    diskLoadingMessage.style.display = "none";
                }, 2000);
            }
        })
        .catch(err => {
            diskLoadingMessage.style.display = "none";
            console.error("Error clearing temp files:", err);
            alert("An error occurred while clearing temp files.");
        });
});

document.getElementById('start-speed-test').addEventListener('click', function() {
    document.getElementById('speed-test').style.display = 'block';
    document.getElementById('down-speed').textContent = '...';
    document.getElementById('up-speed').textContent = '...';
    document.getElementById('ping').textContent = '...';

    fetch('/speed_test')
        .then(response => response.json())
        .then(data => {
            document.getElementById('speed-test').style.display = 'none';

            if (data.download_speed && data.upload_speed) {
                document.getElementById('down-speed').textContent = data.download_speed + ' Mbps';
                document.getElementById('up-speed').textContent = data.upload_speed + ' Mbps';
                document.getElementById('ping').textContent = data.ping + ' ms';
            } else {
                document.getElementById('down-speed').textContent = 'Error';
                document.getElementById('up-speed').textContent = 'Error';
                document.getElementById('ping').textContent = 'Error';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('speed-test').style.display = 'none';
            document.getElementById('down-speed').textContent = 'Error';
            document.getElementById('up-speed').textContent = 'Error';
            document.getElementById('ping').textContent = 'Error';
        });
});

function checkForUpdates() {
    fetch('/check-update')
        .then(response => response.json())
        .then(data => {
            if (data === true) {
                document.getElementById('update-button').style.display = 'block';
            } else {
                document.getElementById('update-button').style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error checking for updates:', error);
        });
}

function updateApp() {
    fetch('/update', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            console.log(data.status);
            alert(data.status);
        })
        .catch(error => {
            console.error('Error during the update process:', error);
            alert('An error occurred while updating the app.');
        });
}

setInterval(checkForUpdates, 30000); // 30 seconds