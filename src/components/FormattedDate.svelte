<script lang="ts">
  interface Props {
    date: Date;
  }

  export let date: Date;
</script>

<time class="text-slate-300" datetime={date.toISOString()}>
  {date.toLocaleDateString("en-us", {
    year: "numeric",
    month: "short",
    day: "numeric",
  })}
</time>
