<script lang="ts">
  // Import the new ConsumptionGraph component
  import ConsumptionGraph from './lib/ConsumptionGraph.svelte';
</script>

<main>
  <h1>Energy Consumption</h1>
  
  <ConsumptionGraph />

  <p class="read-the-docs">
    Real-time data from your backend.
  </p>
</main>

<style>
  /* You can keep some of your global styles or adjust them */
  .read-the-docs {
    color: #888;
    margin-top: 2em;
    font-style: italic;
  }

  /* Ensure main content is centered */
  main {
    text-align: center;
    padding: 1em;
  }
</style>
