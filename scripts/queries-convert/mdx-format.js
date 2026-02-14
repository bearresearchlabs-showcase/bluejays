/**
 * MDX formatting for queries.md — compile markdown for display.
 * Uses @mdx-js/mdx (https://github.com/mdx-js/mdx) for the component era.
 * Plain markdown compiles to JS; no JSX required.
 */
import { compile } from '@mdx-js/mdx'

/**
 * Compile queries.md content to JavaScript (React function body).
 * Use for server-side rendering or client hydration.
 * @param {string} md - queries.md content
 * @param {object} [opts] - compile options
 * @returns {Promise<string>} Compiled JS code
 */
export async function compileMdx(md, opts = {}) {
  const result = await compile(md, {
    outputFormat: 'function-body',
    development: false,
    ...opts,
  })
  return String(result)
}
