<script lang="ts">
import { TaxonomiesKind } from "../../types";
import styles from "./index.module.css";

export let taxonomies: string[];
export let kind: TaxonomiesKind;
</script>

<div class={styles.taxonomy}>
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
