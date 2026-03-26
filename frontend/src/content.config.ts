import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const authors = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/authors' }),
  schema: z.object({
    name: z.string(),
    slug: z.string(),
    image: z.string().optional(),
    order: z.number().optional(),
  }),
});

const books = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/books' }),
  schema: z.object({
    title: z.string(),
    author_name: z.string(),
    author_slug: z.string(),
    book_slug: z.string(),
    year: z.string().optional(),
    description: z.string().optional(),
    image: z.string().optional(),
    mia_url: z.string().optional(),
  }),
});

const episodes = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/episodes' }),
  schema: z.object({
    title: z.string(),
    author_name: z.string(),
    author_slug: z.string(),
    episode_slug: z.string(),
    book_slug: z.string().optional(),
    order: z.number().optional(),
    year: z.string().optional(),
    audio_url: z.string(),
    mia_url: z.string().optional(),
    timestamps: z.array(z.object({
      start: z.number(),
      end: z.number(),
      text: z.string(),
    })),
  }),
});

export const collections = { authors, books, episodes };
