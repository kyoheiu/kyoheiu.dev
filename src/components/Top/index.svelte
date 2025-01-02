<script lang="ts">
import Links from "../Links/index.svelte";
import styles from "./index.module.css";
</script>

<div class={styles.top}>
    <img src="avatar.png" class={styles.img} alt="my avatar" width=80 height=80 />

  <!-- Title -->
  <div class={styles.name}>Kyohei Uto</div>

  <!-- Short Bio -->
  <div class={styles.bio}>
    Husband, father, and developer@algo-artis.
  </div>

  <Links />

  <div class={styles.footer}>
    Powered by Astro, illustration by my wife.
  </div>
</div>

