async function fetchMetrics() {
    const response = await fetch('/metrics');
    const data = await response.json();
    
    // CPU
    document.getElementById('cpu_usage').textContent = data.cpu.usage.toFixed(2);
    document.getElementById('cpu_temp').textContent = data.cpu.temperature;

    // RAM
    document.getElementById('ram_usage').textContent = data.ram.usage_percent.toFixed(2);
    document.getElementById('ram_total').textContent = data.ram.total_gb.toFixed(2);
    document.getElementById('ram_free').textContent = data.ram.free_gb.toFixed(2);

    // Disk
    document.getElementById('disk_usage').textContent = data.disk.usage_percent.toFixed(2);
    document.getElementById('disk_free').textContent = data.disk.free_gb.toFixed(2);

    // GPU
    if (data.gpu !== "Unavailable") {
        document.getElementById('gpu_name').textContent = data.gpu.name;
        document.getElementById('gpu_temp').textContent = data.gpu.temperature;
        document.getElementById('gpu_utilization').textContent = data.gpu.utilization.gpu_percent;
    } else {
        document.getElementById('gpu_name').textContent = "Unavailable";
        document.getElementById('gpu_temp').textContent = "Unavailable";
        document.getElementById('gpu_utilization').textContent = "Unavailable";
    }
}

setInterval(fetchMetrics, 300);
