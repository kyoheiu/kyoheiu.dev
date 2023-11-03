import { defineCollection, z } from 'astro:content';

const blog = defineCollection({
	// Type-check frontmatter using a schema
	schema: z.object({
		title: z.string(),
		// Transform string to Date object
		date: z.date(),
		math: z.boolean().optional(),
		categories: z.array(z.string()),
		tags:z.array(z.string()),
	}),
});

export const collections = { blog };
