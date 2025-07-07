<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { Chart, registerables } from 'chart.js';

  let chart: Chart | null = null;

  let chartCanvas: HTMLCanvasElement;

  let consumptionData: { time: string; value: number }[] = [];
  let error: string | null = null;
  let isLoading = true;
  let intervalId: number;
  let timeRange = 1; // Default to 1 hour

  // Register all the necessary components for Chart.js
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
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/consumption?range=${timeRange}&aggregate=${aggregate}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      
      if (!data || data.length === 0) {
        throw new Error("API returned empty or invalid data.");
      }

      consumptionData = data;

    } catch (e) {
      error = e.message;
      console.error("Failed to fetch or process consumption data:", e);
    } finally {
      isLoading = false;
    }
  }

  function setTimeRange(newRange: number) {
    timeRange = newRange;
    fetchData();
  }

  onMount(() => {
    fetchData();
    intervalId = setInterval(fetchData, 60000);
  });

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
          label: 'House Consumption (Watts)',
          data: values,
          borderColor: '#ff3e00',
          backgroundColor: 'rgba(255, 62, 0, 0.1)',
          fill: true,
          tension: 0.4,
          pointBackgroundColor: '#ff3e00',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: '#ff3e00'
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
              text: 'Consumption (Watts)'
            }
          },
          x: {
            title: {
              display: true,
              text: 'Time'
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
                  label += context.parsed.y.toFixed(2) + ' W';
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

<div class="time-range-selector">
  <button class:active={timeRange === 1} on:click={() => setTimeRange(1)}>1 Hour</button>
  <button class:active={timeRange === 6} on:click={() => setTimeRange(6)}>6 Hours</button>
  <button class:active={timeRange === 12} on:click={() => setTimeRange(12)}>12 Hours</button>
  <button class:active={timeRange === 24} on:click={() => setTimeRange(24)}>24 Hours</button>
  <button class:active={timeRange === 168} on:click={() => setTimeRange(168)}>1 Week</button>
</div>

<div class="graph-container">
  {#if isLoading}
    <p>Loading consumption data...</p>
  {:else if error}
    <p class="error">Could not fetch data: {error}</p>
  {:else}
    <canvas bind:this={chartCanvas}></canvas>
  {/if}
</div>

<!-- Data logging section -->
{#if consumptionData.length > 0}
  <div class="data-log">
    <h3>Raw Data Received:</h3>
    <pre><code>{JSON.stringify(consumptionData, null, 2)}</code></pre>
  </div>
{/if}


<style>
  .time-range-selector {
    display: flex;
    justify-content: center;
    margin-bottom: 1em;
  }

  .time-range-selector button {
    background-color: #3a3a3a;
    color: #fff;
    border: 1px solid #ff3e00;
    padding: 0.5em 1em;
    margin: 0 0.5em;
    cursor: pointer;
    border-radius: 4px;
    transition: background-color 0.3s;
  }

  .time-range-selector button:hover,
  .time-range-selector button.active {
    background-color: #ff3e00;
  }

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
