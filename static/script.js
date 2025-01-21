

function fetchMetrics() {
    // Fetch CPU metrics
    fetch('/metrics/cpu')
        .then(response => response.json())
        .then(data => {
            document.getElementById('cpu-usage').textContent = data.usage;
            document.getElementById('cpu-frequency-current').textContent = `${data["Frequency-curent"]}`;
            document.getElementById('cpu-frequency-max').textContent = `${data["Frequency-max"]}`;
            document.getElementById('cpu-temperature').textContent = data.temperature;
        })
        .catch(error => console.error('Error fetching CPU metrics:', error));

    // Fetch RAM metrics
    fetch('/metrics/ram')
        .then(response => response.json())
        .then(data => {
            document.getElementById('ram-usage').textContent = data.usage;
            document.getElementById('ram-total').textContent = data.total;
            document.getElementById('ram-free').textContent = data.free;
        })
        .catch(error => console.error('Error fetching RAM metrics:', error));

    // Fetch Disk metrics
    fetch('/metrics/disk')
        .then(response => response.json())
        .then(data => {
            document.getElementById('disk-usage').textContent = data.usage;
            document.getElementById('disk-free').textContent = data.free_space;
            document.getElementById('disk-read').textContent = data.read_speed;
            document.getElementById('disk-write').textContent = data.write_speed;
        })
        .catch(error => console.error('Error fetching Disk metrics:', error));

    // Fetch GPU metrics
    fetch('/metrics/gpu')
        .then(response => response.json())
        .then(data => {
            document.getElementById('gpu-name').textContent = data.name;
            document.getElementById('gpu-temperature').textContent = data.temperature;
            document.getElementById('gpu-utilization').textContent = data.utilization;
            document.getElementById('gpu-memory-used').textContent = data.memory_used;
            document.getElementById('gpu-memory-total').textContent = data.memory_total;
        })
        .catch(error => console.error('Error fetching GPU metrics:', error));
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
                document.getElementById('update-message').style.display = 'block';
            } else {
                document.getElementById('update-message').style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error checking for updates:', error);
        });
}

setInterval(checkForUpdates, 900000);

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

function displayAppVersion() {
    fetch('/get-app-version')
        .then(response => response.json())
        .then(data => {
            document.getElementById('app-version').innerText = `App Version: ${data.version}`;
        })
        .catch(error => {
            console.error('Error fetching app version:', error);
        });
}

window.onload = function() {
    displayAppVersion();
};






function showConfirmation(message, onConfirm) {
    const modal = document.createElement("div");
    modal.classList.add("modal-overlay");

    modal.innerHTML = `
        <div class="modal">
            <p>${message}</p>
            <div class="modal-buttons">
                <button id="confirm-yes" class="yes-button">Yes</button>
                <button id="confirm-no" class="no-button">No</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    document.getElementById("confirm-yes").addEventListener("click", () => {
        onConfirm(); 
        document.body.removeChild(modal);
    });

    document.getElementById("confirm-no").addEventListener("click", () => {
        document.body.removeChild(modal);
    });
}

document.getElementById("off").addEventListener("click", function () {
    showConfirmation("Are you sure you want to shut down?", () => {
        sendRequest("/shutdown");
    });
});

document.getElementById("restart").addEventListener("click", function () {
    showConfirmation("Are you sure you want to restart?", () => {
        sendRequest("/restart");
    });
});

document.getElementById("logout").addEventListener("click", function () {
    showConfirmation("Are you sure you want to log out?", () => {
        sendRequest("/logout");
    });
});

function sendRequest(endpoint) {
    fetch(endpoint, {
        method: "POST",
    })
        .then(response => {
            if (response.ok) {
                alert("Action successful!");
            } else {
                alert("Failed to complete the action. Please try again.");
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("An error occurred. Please try again.");
        });
}



// Select the container and all draggable cards
const container = document.getElementById('card-container');
const cards = document.querySelectorAll('.card');

// Add drag event listeners to each card
cards.forEach(card => {
    card.addEventListener('dragstart', dragStart);
    card.addEventListener('dragend', dragEnd);
});

// Add dragover and drop event listeners to the container
container.addEventListener('dragover', dragOver);
container.addEventListener('drop', drop);

let draggedCard = null;

// When dragging starts
function dragStart(event) {
    draggedCard = this; // Save the dragged card
    setTimeout(() => this.classList.add('dragging'), 0);
}

// When dragging ends
function dragEnd() {
    this.classList.remove('dragging');
    draggedCard = null;
}

// When dragging over the container
function dragOver(event) {
    event.preventDefault(); // Prevent default to allow drop
    const afterElement = getDragAfterElement(container, event.clientY);
    if (afterElement == null) {
        container.appendChild(draggedCard);
    } else {
        container.insertBefore(draggedCard, afterElement);
    }
}

// When dropping inside the container
function drop(event) {
    event.preventDefault();
    if (draggedCard) {
        draggedCard.classList.remove('dragging');
    }
}

// Helper function to determine the position to insert the card
function getDragAfterElement(container, y) {
    const draggableElements = [...container.querySelectorAll('.card:not(.dragging)')];

    return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;
        if (offset < 0 && offset > closest.offset) {
            return { offset: offset, element: child };
        } else {
            return closest;
        }
    }, { offset: Number.NEGATIVE_INFINITY }).element;
}
