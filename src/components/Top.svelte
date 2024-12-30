<script lang="ts">
import Links from "./Link.svelte";
</script>

<div class="flex flex-col items-center pt-16">
  <div class="w-20 h-20">
    <img src="avatar.png" class="rounded-full" alt="my avatar" />
  </div>

  <!-- Title -->
  <h1 class="text-2xl m-2 mt-4">Kyohei Uto</h1>

  <!-- Short Bio -->
  <div class="text-center m-2 mb-6 w-48">
    Husband, father, and developer@algo-artis.
  </div>

  <Links />

  <div class="text-center mt-6 mb-2 w-48">
    Powered by Astro, illustration by my wife.
  </div>
</div>
