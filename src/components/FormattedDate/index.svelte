<script lang="ts">
import styles from "./index.module.css";

interface Props {
	date: Date;
}

export let date: Date;
</script>

<time class={styles.date} datetime={date.toISOString()}>
  {date.toLocaleDateString("en-us", {
    year: "numeric",
    month: "short",
    day: "numeric",
  })}
</time>
