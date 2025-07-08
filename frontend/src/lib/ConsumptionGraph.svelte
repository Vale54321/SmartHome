<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { Chart, registerables } from 'chart.js';

  export let endpoint: string;
  export let chartTitle: string;
  export let yAxisTitle: string;
  export let timeRange: number;
  export let unit = 'W';
  export let lineColor = '#ff3e00';
  export let fillColor = 'rgba(255, 62, 0, 0.1)';

  let chart: Chart | null = null;

  let chartCanvas: HTMLCanvasElement;

  let consumptionData: { time: string; value: number }[] = [];
  let error: string | null = null;
  let isLoading = true;
  let intervalId: number;

  Chart.register(...registerables);

  async function fetchData() {
    isLoading = true;
    try {
      let aggregate = 1; // Default to 1 minute
      if (timeRange > 1 && timeRange <= 6) {
        aggregate = 5; // 5 minutes for 6h range
      } else if (timeRange > 6 && timeRange <= 12) {
        aggregate = 10; // 10 minutes for 12h range
      } else if (timeRange > 12 && timeRange <= 24) {
        aggregate = 15; // 15 minutes for 24h range
      } else if (timeRange > 24) {
        aggregate = 60; // 1 hour for 1 week range
      }
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/${endpoint}?range=${timeRange}&aggregate=${aggregate}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      
      if (!data || data.length === 0) {
        throw new Error("API returned empty or invalid data.");
      }

      consumptionData = data;

    } catch (e) {
      if (e instanceof Error) {
        error = e.message;
      } else {
        error = String(e);
      }
      console.error("Failed to fetch or process consumption data:", e);
    } finally {
      isLoading = false;
    }
  }

  onMount(() => {
    fetchData();
    intervalId = setInterval(fetchData, 60000);
  });

  let initialMount = true;
  $: if (timeRange) {
    if (!initialMount) {
      fetchData();
    }
    initialMount = false;
  }

  $: if (chartCanvas && consumptionData.length > 0) {
    createChart();
  }

  function createChart() {
    if (!chartCanvas || !consumptionData.length) return;

    if (chart) {
      chart.destroy();
    }

    const labels = consumptionData.map(d => {
        const date = new Date(d.time);
        return date.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
    });
    const values = consumptionData.map(d => d.value);

    chart = new Chart(chartCanvas, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: chartTitle,
          data: values,
          borderColor: lineColor,
          backgroundColor: fillColor,
          fill: true,
          tension: 0.4,
          pointBackgroundColor: lineColor,
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: lineColor
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: false,
            title: {
              display: true,
              text: yAxisTitle
            },
            min: unit === '%' ? 0 : undefined,
            max: unit === '%' ? 100 : undefined
          },
          x: {
            title: {
              display: true,
              text: 'Zeit'
            }
          }
        },
        plugins: {
          legend: {
            position: 'top',
          },
          tooltip: {
            enabled: true,
            callbacks: {
              label: function(context) {
                let label = context.dataset.label || '';
                if (label) {
                  label += ': ';
                }
                if (context.parsed.y !== null) {
                  label += context.parsed.y.toFixed(2) + ` ${unit}`;
                }
                return label;
              }
            }
          }
        }
      }
    });
  }

  // Clean up the chart when the component is destroyed
  onDestroy(() => {
    if (chart) {
      chart.destroy();
    }
    if (intervalId) {
      clearInterval(intervalId);
    }
  });
</script>

<div class="graph-container">
  {#if isLoading}
    <p>Lade Verbrauchsdaten...</p>
  {:else if error}
    <p class="error">Daten konnten nicht geladen werden: {error}</p>
  {:else}
    <canvas bind:this={chartCanvas}></canvas>
  {/if}
</div>

<style>
  .graph-container {
    height: 60vh;
    width: 100%;
    max-width: 900px;
    margin: 2em auto;
    padding: 1em;
    background-color: #2a2a2a;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  }

  .error {
    color: #ff8a8a;
  }

  .data-log {
    max-width: 900px;
    margin: 2em auto;
    padding: 1em;
    background-color: #2a2a2a;
    border-radius: 8px;
    text-align: left;
    color: #ccc;
  }

  .data-log h3 {
    margin-top: 0;
    color: #ff3e00;
  }

  .data-log pre {
    white-space: pre-wrap;
    word-wrap: break-word;
    background-color: #1e1e1e;
    padding: 1em;
    border-radius: 4px;
  }
</style>
