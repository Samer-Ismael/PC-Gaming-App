// Show a popup with the IP address
window.onload = function() {
    const ipAddress = "{{ ip_address }}";  // Flask will inject the IP address here
    alert("This is the link to use on your phone: 'http://" + ipAddress + ":5000'");
}

function fetchMetrics() {
    fetch('/metrics')
        .then(response => response.json())
        .then(data => {
            document.getElementById('cpu-usage').textContent = data.cpu.usage;
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

setInterval(fetchMetrics, 2000);  // Fetch metrics every 2 seconds

document.addEventListener('DOMContentLoaded', () => {
    // Attach event listeners to buttons
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
