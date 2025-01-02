<script lang="ts">
import {
	GithubSolid,
	CodeBranchOutline,
	PenNibOutline,
	CaptioningOutline,
	DiscordSolid,
	MailBoxOutline,
} from "flowbite-svelte-icons";
import styles from "./index.module.css";

type Link = {
	name: string;
	link: string;
};

const links: Link[] = [
	{
		name: "GitHub",
		link: "https://github.com/kyoheiu",
	},
	{
		name: "sourcehut",
		link: "https://git.sr.ht/~kyoheiu/",
	},
	{
		name: "blog (ja-JP)",
		link: "/blog",
	},
	{
		name: "Zenn (ja-JP)",
		link: "https://zenn.dev/kyoheiu",
	},
	{
		name: "TED Translation",
		link: "https://www.ted.com/profiles/14244197/translator",
	},
	{ name: "Discord@kyoheiu", link: "" },
	{ name: "im@kyoheiu.dev", link: "" },
];
</script>

<div class={styles.wrapper}>
{#each links as link}
  <a
    href={link.link}
    class={styles.link}
  >
    {#if link.name === "GitHub"}
      <GithubSolid class={styles.icon} />
    {:else if link.name === "sourcehut"}
      <CodeBranchOutline class={styles.icon} />
    {:else if link.name === "blog (ja-JP)"}
      <PenNibOutline class={styles.icon} />
    {:else if link.name === "Zenn (ja-JP)"}
      <PenNibOutline class={styles.icon} />
    {:else if link.name === "TED Translation"}
      <CaptioningOutline class={styles.icon} />
    {:else if link.name === "Discord@kyoheiu"}
      <DiscordSolid class= {styles.icon} />
    {:else if link.name === "im@kyoheiu.dev"}
      <MailBoxOutline class={styles.icon} />
    {/if}
    &nbsp;
    <span class="mt-1">{link.name}</span>
  </a>
{/each}
</div>
