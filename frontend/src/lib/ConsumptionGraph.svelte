<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { Chart, registerables } from 'chart.js';

  // This will hold the chart instance
  let chart: Chart | null = null;
  // This is the canvas element where the chart will be drawn
  let chartCanvas: HTMLCanvasElement;
  // Reactive variables to hold the state of our data fetching
  let consumptionData: { time: string; value: number }[] = [];
  let error: string | null = null;
  let isLoading = true;
  let intervalId: number;

  // Register all the necessary components for Chart.js
  Chart.register(...registerables);

  async function fetchData() {
    try {
      // Fetch data using the Vite proxy.
      const response = await fetch('/api/consumption');
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      
      if (!data || data.length === 0) {
        throw new Error("API returned empty or invalid data.");
      }

      // Just update the data here. The chart will be created reactively.
      consumptionData = data;

    } catch (e) {
      // Handle any errors during the fetch
      error = e.message;
      console.error("Failed to fetch or process consumption data:", e);
    } finally {
      // Set loading to false when the process is complete
      isLoading = false;
    }
  }

  // onMount is a lifecycle function that runs after the component is rendered to the DOM
  onMount(() => {
    fetchData(); // Fetch initial data
    intervalId = setInterval(fetchData, 60000); // Refresh every minute
  });

  // Reactive statement: This code runs whenever the variables it depends on change.
  // In this case, it runs when `chartCanvas` or `consumptionData` are updated.
  $: if (chartCanvas && consumptionData.length > 0) {
    createChart();
  }

  function createChart() {
    // We already check for chartCanvas and data in the reactive statement, but it's good practice.
    if (!chartCanvas || !consumptionData.length) return;

    // Destroy the old chart instance before creating a new one to prevent memory leaks
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
