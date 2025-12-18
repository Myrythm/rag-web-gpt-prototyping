<template>
  <div 
    class="markdown-content" 
    v-html="renderedMarkdown"
  ></div>
</template>

<script setup>
import { computed } from 'vue';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

const props = defineProps({
  content: {
    type: String,
    required: true
  }
});

// Configure marked for better rendering
marked.setOptions({
  breaks: true,
  gfm: true,
  headerIds: false,
  mangle: false
});

// Custom renderer for better styling (marked v17+ API)
const renderer = new marked.Renderer();

// Customize code blocks - marked v17+ passes an object with { text, lang }
renderer.code = ({ text, lang }) => {
  const language = lang || 'text';
  // Escape HTML in code to prevent XSS and rendering issues
  const escapedCode = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
  return `<pre><code class="language-${language}">${escapedCode}</code></pre>`;
};

// Customize inline code - marked v17+ passes an object with { text }
renderer.codespan = ({ text }) => {
  return `<code class="inline-code">${text}</code>`;
};

marked.use({ renderer });

const renderedMarkdown = computed(() => {
  try {
    // Remove citation markers [ref:N] from the content before rendering
    const cleanContent = props.content.replace(/\s*\[ref:\d+\]/g, '');
    // Parse markdown to HTML
    const rawHtml = marked.parse(cleanContent);
    // Sanitize HTML to prevent XSS attacks
    return DOMPurify.sanitize(rawHtml);
  } catch (error) {
    console.error('Markdown rendering error:', error);
    return props.content;
  }
});
</script>

<style scoped>
.markdown-content {
  @apply leading-relaxed text-[15px];
}

/* Headings */
.markdown-content :deep(h1) {
  @apply text-xl md:text-2xl font-bold mt-4 mb-3 text-white;
}

.markdown-content :deep(h2) {
  @apply text-lg md:text-xl font-bold mt-3 mb-2 text-white;
}

.markdown-content :deep(h3) {
  @apply text-base md:text-lg font-semibold mt-3 mb-2 text-gray-100;
}

.markdown-content :deep(h4),
.markdown-content :deep(h5),
.markdown-content :deep(h6) {
  @apply text-sm md:text-base font-semibold mt-2 mb-1 text-gray-100;
}

/* Paragraphs */
.markdown-content :deep(p) {
  @apply mb-3 last:mb-0;
}

/* Lists */
.markdown-content :deep(ul) {
  @apply list-disc list-inside mb-3 space-y-1 ml-2;
}

.markdown-content :deep(ol) {
  @apply list-decimal list-inside mb-3 space-y-1 ml-2;
}

.markdown-content :deep(li) {
  @apply ml-2;
}

.markdown-content :deep(li > ul),
.markdown-content :deep(li > ol) {
  @apply mt-1 ml-4;
}

/* Code blocks */
.markdown-content :deep(pre) {
  @apply bg-gray-900/80 border border-gray-700/50 rounded-lg p-3 md:p-4 mb-3 overflow-x-auto;
}

.markdown-content :deep(pre code) {
  @apply text-sm font-mono text-gray-100 block;
}

/* Inline code */
.markdown-content :deep(.inline-code),
.markdown-content :deep(code:not(pre code)) {
  @apply bg-gray-700/50 text-blue-300 px-1.5 py-0.5 rounded text-sm font-mono;
}

/* Links */
.markdown-content :deep(a) {
  @apply text-blue-400 hover:text-blue-300 underline transition-colors;
}

/* Blockquotes */
.markdown-content :deep(blockquote) {
  @apply border-l-4 border-blue-500/50 pl-4 italic text-gray-300 my-3;
}

/* Horizontal rule */
.markdown-content :deep(hr) {
  @apply border-t border-gray-700/50 my-4;
}

/* Tables */
.markdown-content :deep(table) {
  @apply w-full border-collapse mb-3;
}

.markdown-content :deep(th) {
  @apply bg-gray-700/50 border border-gray-600/50 px-3 py-2 text-left font-semibold;
}

.markdown-content :deep(td) {
  @apply border border-gray-700/50 px-3 py-2;
}

/* Strong and emphasis */
.markdown-content :deep(strong) {
  @apply font-bold text-white;
}

.markdown-content :deep(em) {
  @apply italic;
}

/* Images */
.markdown-content :deep(img) {
  @apply max-w-full h-auto rounded-lg my-2;
}
</style>
