<script lang="ts">
  import ConsumptionGraph from './lib/ConsumptionGraph.svelte';
  import PowerDistribution from './lib/PowerDistribution.svelte';

  let timeRange = 1; // Default to 1 hour

  function setTimeRange(newRange: number) {
    timeRange = newRange;
  }
</script>

<main>
  <div class="time-range-selector">
    <button class:active={timeRange === 1} on:click={() => setTimeRange(1)}>1 Stunde</button>
    <button class:active={timeRange === 6} on:click={() => setTimeRange(6)}>6 Stunden</button>
    <button class:active={timeRange === 12} on:click={() => setTimeRange(12)}>12 Stunden</button>
    <button class:active={timeRange === 24} on:click={() => setTimeRange(24)}>24 Stunden</button>
    <button class:active={timeRange === 168} on:click={() => setTimeRange(168)}>1 Woche</button>
  </div>

  <PowerDistribution />

  <h1>Stromverbrauch</h1>
  <ConsumptionGraph 
    endpoint="house_consumption"
    chartTitle="Hausverbrauch (Watt)"
    yAxisTitle="Verbrauch (Watt)"
    lineColor="#ff3e00"
    fillColor="rgba(255, 62, 0, 0.1)"
    bind:timeRange
  />

  <h1>Solarstrom</h1>
  <ConsumptionGraph 
    endpoint="pv_power"
    chartTitle="Solarstrom (Watt)"
    yAxisTitle="Erzeugung (Watt)"
    lineColor="#42b883"
    fillColor="rgba(66, 184, 131, 0.1)"
    bind:timeRange
  />

  <h1>Batterie</h1>
  <ConsumptionGraph 
    endpoint="battery_power"
    chartTitle="Batterieladung (Watt)"
    yAxisTitle="Leistung (Watt)"
    lineColor="#007bff"
    fillColor="rgba(0, 123, 255, 0.1)"
    bind:timeRange
  />

  <h1>Netz</h1>
  <ConsumptionGraph 
    endpoint="grid_power"
    chartTitle="Netzbezug (Watt)"
    yAxisTitle="Leistung (Watt)"
    lineColor="#6f42c1"
    fillColor="rgba(111, 66, 193, 0.1)"
    bind:timeRange
  />

  <h1>Wallbox</h1>
  <ConsumptionGraph 
    endpoint="wallbox_consumption"
    chartTitle="Wallbox Verbrauch (Watt)"
    yAxisTitle="Verbrauch (Watt)"
    lineColor="#ffc107"
    fillColor="rgba(255, 193, 7, 0.1)"
    bind:timeRange
  />

  <h1>Batterie Ladestand</h1>
  <ConsumptionGraph 
    endpoint="battery_soc"
    chartTitle="Batterie Ladestand (%)"
    yAxisTitle="Ladestand (%)"
    unit="%"
    lineColor="#17a2b8"
    fillColor="rgba(23, 162, 184, 0.1)"
    bind:timeRange
  />

  <h1>Eigenverbrauch</h1>
  <ConsumptionGraph 
    endpoint="self_consumption"
    chartTitle="Eigenverbrauch (%)"
    yAxisTitle="Anteil (%)"
    unit="%"
    lineColor="#28a745"
    fillColor="rgba(40, 167, 69, 0.1)"
    bind:timeRange
  />

  <h1>Autarkiegrad</h1>
  <ConsumptionGraph 
    endpoint="self_sufficiency"
    chartTitle="Autarkiegrad (%)"
    yAxisTitle="Anteil (%)"
    unit="%"
    lineColor="#dc3545"
    fillColor="rgba(220, 53, 69, 0.1)"
    bind:timeRange
  />
</main>

<style>
  .time-range-selector {
    position: sticky;
    top: 0;
    background-color: #2a2a2a; /* Match graph background for consistency */
    padding-top: 1em;
    padding-bottom: 1em;
    z-index: 10;
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

  main {
    text-align: center;
    padding: 1em;
  }
</style>
