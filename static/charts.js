let bmiChart = null;
let cholesterolChart = null;
let a1cChart = null;

const chartColors = {
    'Hospital A': { bg: 'rgba(59, 130, 246, 0.2)', border: 'rgb(59, 130, 246)' },
    'Hospital B': { bg: 'rgba(16, 185, 129, 0.2)', border: 'rgb(16, 185, 129)' },
    'Hospital C': { bg: 'rgba(249, 115, 22, 0.2)', border: 'rgb(249, 115, 22)' }
};

function renderCharts(chartData) {
    if (chartData.bmi && chartData.bmi.length > 0) {
        renderBMIChart(chartData.bmi);
    }
    
    if (chartData.cholesterol && chartData.cholesterol.length > 0) {
        renderCholesterolChart(chartData.cholesterol);
    }
    
    if (chartData.a1c && chartData.a1c.length > 0) {
        renderA1CChart(chartData.a1c);
    }
}

function renderBMIChart(data) {
    const ctx = document.getElementById('bmi-chart');
    if (!ctx) return;
    
    if (bmiChart) {
        bmiChart.destroy();
    }
    
    const datasets = groupByHospital(data);
    
    bmiChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [...new Set(data.map(d => d.date))].sort(),
            datasets: datasets.map(ds => ({
                label: ds.hospital,
                data: ds.data.map(d => ({ x: d.date, y: d.value })),
                backgroundColor: chartColors[ds.hospital]?.bg || 'rgba(0,0,0,0.1)',
                borderColor: chartColors[ds.hospital]?.border || 'rgb(0,0,0)',
                borderWidth: 2,
                tension: 0.3,
                fill: false,
                pointRadius: 5
            }))
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                annotation: {
                    annotations: {
                        normalRange: {
                            type: 'box',
                            yMin: 18.5,
                            yMax: 24.9,
                            backgroundColor: 'rgba(16, 185, 129, 0.1)',
                            borderColor: 'rgba(16, 185, 129, 0.3)',
                            borderWidth: 1
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    min: 15,
                    max: 40,
                    title: {
                        display: true,
                        text: 'BMI'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                }
            }
        }
    });
}

function renderCholesterolChart(data) {
    const ctx = document.getElementById('cholesterol-chart');
    if (!ctx) return;
    
    if (cholesterolChart) {
        cholesterolChart.destroy();
    }
    
    const datasets = groupByHospital(data);
    
    cholesterolChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [...new Set(data.map(d => d.date))].sort(),
            datasets: datasets.map(ds => ({
                label: ds.hospital,
                data: ds.data.map(d => ({ x: d.date, y: d.value })),
                backgroundColor: chartColors[ds.hospital]?.bg || 'rgba(0,0,0,0.1)',
                borderColor: chartColors[ds.hospital]?.border || 'rgb(0,0,0)',
                borderWidth: 2,
                tension: 0.3,
                fill: false,
                pointRadius: 5
            }))
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    min: 100,
                    max: 300,
                    title: {
                        display: true,
                        text: 'Total Cholesterol (mg/dL)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                }
            }
        }
    });
}

function renderA1CChart(data) {
    const ctx = document.getElementById('a1c-chart');
    if (!ctx) return;
    
    if (a1cChart) {
        a1cChart.destroy();
    }
    
    const datasets = groupByHospital(data);
    
    a1cChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [...new Set(data.map(d => d.date))].sort(),
            datasets: datasets.map(ds => ({
                label: ds.hospital,
                data: ds.data.map(d => ({ x: d.date, y: d.value })),
                backgroundColor: chartColors[ds.hospital]?.bg || 'rgba(0,0,0,0.1)',
                borderColor: chartColors[ds.hospital]?.border || 'rgb(0,0,0)',
                borderWidth: 2,
                tension: 0.3,
                fill: false,
                pointRadius: 5
            }))
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    min: 4,
                    max: 10,
                    title: {
                        display: true,
                        text: 'A1C (%)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                }
            }
        }
    });
}

function groupByHospital(data) {
    const hospitals = {};
    
    data.forEach(item => {
        const hospital = item.hospital || 'Unknown';
        if (!hospitals[hospital]) {
            hospitals[hospital] = [];
        }
        hospitals[hospital].push(item);
    });
    
    return Object.keys(hospitals).map(hospital => ({
        hospital: hospital,
        data: hospitals[hospital].sort((a, b) => a.date.localeCompare(b.date))
    }));
}
