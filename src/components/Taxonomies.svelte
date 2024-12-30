<script lang="ts">
import { TaxonomiesKind } from "../types";

export let taxonomies: string[];
export let kind: TaxonomiesKind;
</script>

<div class="flex flex-wrap space-x-2 text-slate-400 text-sm">
  {#if kind === TaxonomiesKind.Category}
    {#each taxonomies as t}
      <a href={`/blog/categories/${t}`}>/{t}</a>&ensp;
    {/each}
  {:else}
    {#each taxonomies as t}
      <a href={`/blog/tags/${t}`}>#{t}</a>&ensp;
    {/each}
  {/if}
</div>
