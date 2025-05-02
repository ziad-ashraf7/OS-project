document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const generateBtn = document.getElementById('generateBtn');
    const algorithmBtns = document.querySelectorAll('.btn-algorithm');
    const processTableBody = document.getElementById('processTableBody');
    const metricsTableBody = document.getElementById('metricsTableBody');
    const averagesContainer = document.getElementById('averagesContainer');
    const numProcessesInput = document.getElementById('numProcesses');
    const timeQuantumInput = document.getElementById('timeQuantum');

    let processes = [];
   // let ganttChart = null;

    // Initialize Gantt Chart
    const ctx = document.getElementById('ganttChart').getContext('2d');
    initializeGanttChart();

    // Event Listeners
    generateBtn.addEventListener('click', generateProcesses);
    algorithmBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            runAlgorithm(this.dataset.algorithm);
        });
    });

    // Add the file upload event listener
    document.getElementById('uploadBtn').addEventListener('click', uploadFile);

    function uploadFile() {
        const fileInput = document.getElementById('processFile');
        const file = fileInput.files[0];
        const downloadBtn = document.getElementById('downloadBtn');

        if (!file) {
            showError('Please select a file first');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showError(data.error);
            } else {
                processes = data.processes;
                updateProcessTable();

                // Enable download button
                if (data.download_url) {
                    downloadBtn.href = data.download_url;
                    downloadBtn.classList.remove('d-none');
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('File upload failed: ' + error.message);
        });
    }

    // Functions
function generateProcesses() {
    const numProcesses = parseInt(numProcessesInput.value);

    if (isNaN(numProcesses)) {
        showError('Please enter a valid number');
        return;
    }

    generateBtn.disabled = true;
    generateBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Generating...';

    fetch('/generate_processes', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            num_processes: numProcesses
        })
    })
    .then(async response => {
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            throw new Error('Server returned non-JSON response');
        }

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Server error');
        }

        processes = data.processes;
        updateProcessTable();
    })
    .catch(error => {
        console.error('Error:', error);
        showError(error.message || 'Failed to generate processes');
    })
    .finally(() => {
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<i class="bi bi-shuffle"></i> Generate Random Processes';
    });
}
    function runAlgorithm(algorithm) {
    if (processes.length === 0) {
        showError('Please generate processes first');
        return;
    }

    const timeQuantum = timeQuantumInput.value;

    // لا نقوم بتغيير النص هنا بعد الآن أو تعطيل الأزرار
    // إنما نترك الأزرار كما هي دون أي تغيير في النص أو الإيقاف

    fetch('/run_algorithm', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            algorithm: algorithm,
            processes: processes,
            time_quantum: timeQuantum
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Algorithm response:', data); // Debug log
        if (data.error) {
            showError(data.error);
        } else {
            updateResults(data);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('Failed to run algorithm: ' + error.message);
    });
}


    function updateProcessTable() {
        processTableBody.innerHTML = '';

        processes.forEach(process => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${process.pid}</td>
                <td>${process.arrival_time}</td>
                <td>${process.burst_time}</td>
                <td>${process.priority}</td>
            `;
            processTableBody.appendChild(row);
        });
    }

    function updateResults(data) {
        // Update metrics table
        metricsTableBody.innerHTML = data.metrics.map(metric => ` 
            <tr>
                <td>${metric.pid}</td>
                <td>${metric.waiting_time.toFixed(2)}</td>
                <td>${metric.turnaround_time.toFixed(2)}</td>
                <td>${metric.response_time !== null ? metric.response_time.toFixed(2) : 'N/A'}</td>
            </tr>
        `).join('');

        // Update averages display
        averagesContainer.innerHTML = `
            <h4 class="h6">Algorithm: ${data.algorithm}</h4>
            <div class="averages-display">
                <div>Average Waiting Time: <strong>${data.averages.waiting_time.toFixed(2)}</strong></div>
                <div>Average Turnaround Time: <strong>${data.averages.turnaround_time.toFixed(2)}</strong></div>
                <div>Average Response Time: <strong>${data.averages.response_time !== null ? data.averages.response_time.toFixed(2) : 'N/A'}</strong></div>
            </div>
        `;

        // Update Gantt chart
        updateGanttChart(data.gantt_chart, data.algorithm);
    }

    function initializeGanttChart() {
        ganttChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Process Execution'],
                datasets: []
            },
            options: {
                indexAxis: 'y',
                scales: {
                    x: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Time Units',
                            color: '#ffffff'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#ffffff',
                            stepSize: 1
                        }
                    },
                    y: {
                        display: false
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const start = context.dataset.startTimes[context.dataIndex];
                                const end = start + context.raw;
                                return `P${context.dataset.label}: ${start} to ${end}`;
                            }
                        }
                    },
                    title: {
                        display: true,
                        text: 'Gantt Chart',
                        color: '#ffffff',
                        font: {
                            size: 16
                        }
                    }
                },
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

function updateGanttChart(ganttData, algorithm) {
    if (window.ganttChart) {
        window.ganttChart.destroy();
    }

    const ctx = document.getElementById('ganttChart').getContext('2d');

    // Process data for the Gantt chart
    const labels = [];
    const data = [];
    const backgroundColors = {
        1: '#4B0082',  // Deep Purple for P1
        2: '#2E86C1',  // Blue for P2
        3: '#27AE60',  // Green for P3
        4: '#F1C40F',  // Yellow for P4
        5: '#E74C3C'   // Red for P5
    };

    ganttData.forEach((segment) => {
        const [pid, start, end] = segment;
        labels.push(`P${pid}`);
        data.push({
            x: start,
            x2: end,
            y: 0
        });
    });

    const maxEndTime = Math.max(...ganttData.map(item => item[2]));

    window.ganttChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: ganttData.map(([pid]) => backgroundColors[pid] || '#808080'),
                borderWidth: 0,
                barPercentage: 1.0,
                categoryPercentage: 1.0
            }]
        },
        options: {
            indexAxis: 'y',
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    min: 0,
                    max: maxEndTime + 5,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        stepSize: 5,
                        color: '#ffffff'
                    }
                },
                y: {
                    display: false
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: `${algorithm} Scheduling Gantt Chart`,
                    color: '#ffffff',
                    font: {
                        size: 16
                    }
                }
            },
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 500,
                onComplete: function() {
                    const chart = this;
                    const ctx = chart.ctx;
                    ctx.save();
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillStyle = '#ffffff';
                    ctx.font = 'bold 14px Arial';

                    chart.data.datasets.forEach((dataset, i) => {
                        const meta = chart.getDatasetMeta(i);
                        meta.data.forEach((bar, index) => {
                            const [pid] = ganttData[index];
                            ctx.fillText(
                                `P${pid}`,
                                bar.x + (bar.width / 2),
                                bar.y
                            );
                        });
                    });
                    ctx.restore();
                }
            }
        }
    });
}

function generateFancyColors(count) {
    const colors = [];
    const hueStep = 360 / count;

    for (let i = 0; i < count; i++) {
        const hue = i * hueStep;
        // Create gradient-like colors
        colors.push(`linear-gradient(45deg, hsl(${hue}, 80%, 60%), hsl(${hue + 30}, 80%, 60%))`);
    }

    return colors;
}
    function showError(message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

        // Insert at the top of the container
        document.querySelector('.container-fluid').prepend(alertDiv);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }, 5000);
    }
});
