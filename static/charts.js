/**
 * Evexia Health Metrics Visualization
 * Refined Luxury Wellness Color Palette
 */

let bmiChart = null;
let cholesterolChart = null;
let a1cChart = null;

// Luxury wellness color palette - sage, gold, warm bronze
const chartColors = {
    'Hospital A': {
        bg: 'rgba(93, 130, 104, 0.15)',
        border: 'rgb(93, 130, 104)'  // Sage green
    },
    'Hospital B': {
        bg: 'rgba(201, 160, 72, 0.15)',
        border: 'rgb(201, 160, 72)'  // Warm gold
    },
    'Hospital C': {
        bg: 'rgba(107, 91, 79, 0.15)',
        border: 'rgb(107, 91, 79)'   // Warm bronze
    }
};

// Global Chart.js defaults for consistent styling
Chart.defaults.font.family = "'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.color = '#635a53';
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.legend.labels.padding = 20;

// Shared chart options for consistency
const sharedOptions = {
    responsive: true,
    maintainAspectRatio: true,
    interaction: {
        intersect: false,
        mode: 'index'
    },
    plugins: {
        legend: {
            position: 'bottom',
            labels: {
                font: {
                    weight: 500
                }
            }
        },
        tooltip: {
            backgroundColor: 'rgba(61, 56, 53, 0.95)',
            titleFont: {
                family: "'Plus Jakarta Sans', sans-serif",
                size: 13,
                weight: 600
            },
            bodyFont: {
                family: "'Plus Jakarta Sans', sans-serif",
                size: 12
            },
            padding: 12,
            cornerRadius: 8,
            displayColors: true,
            boxPadding: 4
        }
    },
    scales: {
        x: {
            grid: {
                color: 'rgba(216, 208, 200, 0.5)',
                drawBorder: false
            },
            ticks: {
                font: {
                    size: 11
                }
            }
        },
        y: {
            grid: {
                color: 'rgba(216, 208, 200, 0.5)',
                drawBorder: false
            },
            ticks: {
                font: {
                    size: 11
                }
            }
        }
    },
    elements: {
        line: {
            tension: 0.4,
            borderWidth: 2.5
        },
        point: {
            radius: 4,
            hoverRadius: 6,
            borderWidth: 2,
            backgroundColor: '#ffffff'
        }
    }
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
                backgroundColor: chartColors[ds.hospital]?.bg || 'rgba(150, 139, 125, 0.15)',
                borderColor: chartColors[ds.hospital]?.border || 'rgb(150, 139, 125)',
                fill: false,
                pointBackgroundColor: '#ffffff',
                pointBorderColor: chartColors[ds.hospital]?.border || 'rgb(150, 139, 125)'
            }))
        },
        options: {
            ...sharedOptions,
            plugins: {
                ...sharedOptions.plugins,
                annotation: {
                    annotations: {
                        normalRange: {
                            type: 'box',
                            yMin: 18.5,
                            yMax: 24.9,
                            backgroundColor: 'rgba(93, 130, 104, 0.08)',
                            borderColor: 'rgba(93, 130, 104, 0.2)',
                            borderWidth: 1
                        }
                    }
                }
            },
            scales: {
                ...sharedOptions.scales,
                y: {
                    ...sharedOptions.scales.y,
                    beginAtZero: false,
                    min: 15,
                    max: 40,
                    title: {
                        display: true,
                        text: 'BMI',
                        font: {
                            weight: 600,
                            size: 12
                        },
                        color: '#3d3835'
                    }
                },
                x: {
                    ...sharedOptions.scales.x,
                    title: {
                        display: true,
                        text: 'Date',
                        font: {
                            weight: 600,
                            size: 12
                        },
                        color: '#3d3835'
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
                backgroundColor: chartColors[ds.hospital]?.bg || 'rgba(150, 139, 125, 0.15)',
                borderColor: chartColors[ds.hospital]?.border || 'rgb(150, 139, 125)',
                fill: false,
                pointBackgroundColor: '#ffffff',
                pointBorderColor: chartColors[ds.hospital]?.border || 'rgb(150, 139, 125)'
            }))
        },
        options: {
            ...sharedOptions,
            scales: {
                ...sharedOptions.scales,
                y: {
                    ...sharedOptions.scales.y,
                    beginAtZero: false,
                    min: 100,
                    max: 300,
                    title: {
                        display: true,
                        text: 'Total Cholesterol (mg/dL)',
                        font: {
                            weight: 600,
                            size: 12
                        },
                        color: '#3d3835'
                    }
                },
                x: {
                    ...sharedOptions.scales.x,
                    title: {
                        display: true,
                        text: 'Date',
                        font: {
                            weight: 600,
                            size: 12
                        },
                        color: '#3d3835'
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
                backgroundColor: chartColors[ds.hospital]?.bg || 'rgba(150, 139, 125, 0.15)',
                borderColor: chartColors[ds.hospital]?.border || 'rgb(150, 139, 125)',
                fill: false,
                pointBackgroundColor: '#ffffff',
                pointBorderColor: chartColors[ds.hospital]?.border || 'rgb(150, 139, 125)'
            }))
        },
        options: {
            ...sharedOptions,
            scales: {
                ...sharedOptions.scales,
                y: {
                    ...sharedOptions.scales.y,
                    beginAtZero: false,
                    min: 4,
                    max: 10,
                    title: {
                        display: true,
                        text: 'A1C (%)',
                        font: {
                            weight: 600,
                            size: 12
                        },
                        color: '#3d3835'
                    }
                },
                x: {
                    ...sharedOptions.scales.x,
                    title: {
                        display: true,
                        text: 'Date',
                        font: {
                            weight: 600,
                            size: 12
                        },
                        color: '#3d3835'
                    }
                }
            }
        }
    });
}

// Mini chart for dashboard - simplified version for the home view
let bmiChartMini = null;

function renderMiniBMIChart(data) {
    const ctx = document.getElementById('bmi-chart-mini');
    if (!ctx) return;

    if (bmiChartMini) {
        bmiChartMini.destroy();
    }

    // Flatten all data points regardless of hospital
    const allPoints = data.sort((a, b) => a.date.localeCompare(b.date));

    bmiChartMini = new Chart(ctx, {
        type: 'line',
        data: {
            labels: allPoints.map(d => d.date),
            datasets: [{
                data: allPoints.map(d => d.value),
                borderColor: 'rgb(93, 130, 104)',
                backgroundColor: 'rgba(93, 130, 104, 0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 3,
                pointBackgroundColor: '#ffffff',
                pointBorderColor: 'rgb(93, 130, 104)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(61, 56, 53, 0.95)',
                    titleFont: { size: 12, weight: 600 },
                    bodyFont: { size: 11 },
                    padding: 8,
                    cornerRadius: 6,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return `BMI: ${context.parsed.y.toFixed(1)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: false,
                    grid: { display: false }
                },
                y: {
                    display: false,
                    grid: { display: false }
                }
            },
            elements: {
                line: {
                    tension: 0.4,
                    borderWidth: 2
                },
                point: {
                    radius: 3,
                    hoverRadius: 5
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
