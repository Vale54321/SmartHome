<script lang="ts">
  import { onMount, onDestroy } from 'svelte';

  interface PowerData {
    house_consumption: number;
    pv_power: number;
    battery_power: number;
    grid_power: number;
  }

  let powerData: PowerData | null = null;
  let error: string | null = null;
  let intervalId: number;

  async function fetchData() {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/now`);
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      powerData = await response.json();
    } catch (e) {
      if (e instanceof Error) {
        error = e.message;
      } else {
        error = String(e);
      }
      console.error("Failed to fetch power distribution data:", e);
    }
  }

  onMount(() => {
    fetchData();
    intervalId = setInterval(fetchData, 2000); // Fetch every 5 seconds
  });

  onDestroy(() => {
    clearInterval(intervalId);
  });

  // Derived calculations for visualization
  $: sources = (() => {
    if (!powerData) return [];

    const { house_consumption, pv_power, battery_power, grid_power } = powerData;
    const sources = [];

    // Solar contribution (power directly used from PV)
    const solar_to_house = Math.max(0, pv_power - Math.max(0, -grid_power) - Math.max(0, -battery_power));
    if (solar_to_house > 0) {
      sources.push({ name: 'Solar', value: solar_to_house, color: '#42b883' });
    }

    // Battery contribution (discharging)
    if (battery_power > 0) {
      sources.push({ name: 'Batterie', value: battery_power, color: '#007bff' });
    }

    // Grid contribution (drawing from grid)
    if (grid_power > 0) {
      sources.push({ name: 'Netz', value: grid_power, color: '#6f42c1' });
    }

    return sources;
  })();

  $: totalSourcePower = sources.reduce((acc, s) => acc + s.value, 0);
</script>

<div class="power-distribution-container">
  <h3>Aktueller Strommix ({powerData?.house_consumption.toFixed(0) ?? 0} W)</h3>
  {#if error}
    <p class="error">Daten konnten nicht geladen werden: {error}</p>
  {:else if powerData}
    <div class="power-bar">
      {#each sources as source}
        {@const percentage = totalSourcePower > 0 ? (source.value / totalSourcePower) * 100 : 0}
        <div class="power-segment" style="width: {percentage}%; background-color: {source.color};">
          <div class="label">
            {source.name}<br/>
            {source.value.toFixed(0)} W
          </div>
        </div>
      {/each}
    </div>
  {:else}
    <p>Lade Daten...</p>
  {/if}
</div>

<style>
  .power-distribution-container {
    max-width: 900px;
    margin: 2em auto;
    padding: 1em;
    background-color: #2a2a2a;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    color: #fff;
  }

  h3 {
    text-align: center;
    margin-top: 0;
  }

  .power-bar {
    display: flex;
    width: 100%;
    height: 60px;
    background-color: #1e1e1e;
    border-radius: 4px;
    overflow: hidden;
  }

  .power-segment {
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    color: white;
    font-weight: bold;
    transition: width 0.5s ease-in-out;
    white-space: nowrap;
    overflow: hidden;
  }

  .power-segment .label {
      padding: 0 10px;
  }

  .error {
    color: #ff8a8a;
  }
</style>
