/**
 * Utility functions for the frontend.
 *
 * Small, pure helper functions used across components.
 */

/**
 * Format an ISO date string into a human-readable format.
 *
 * @param {string} isoString - ISO 8601 date string
 * @returns {string} Formatted date (e.g., "Jun 8, 2026, 10:30 PM")
 */
export function formatDate(isoString) {
  if (!isoString) return '—'
  return new Date(isoString).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  })
}

/**
 * Get CSS class for a severity level.
 *
 * @param {'Critical' | 'High' | 'Medium' | 'Low'} severity
 * @returns {string} Tailwind color class
 */
export function severityColor(severity) {
  const map = {
    Critical: 'text-severity-critical',
    High: 'text-severity-high',
    Medium: 'text-severity-medium',
    Low: 'text-severity-low',
  }
  return map[severity] || 'text-gray-400'
}

/**
 * Capitalize the first letter of a string.
 *
 * @param {string} str
 * @returns {string}
 */
export function capitalize(str) {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1)
}

/**
 * Truncate a string to a maximum length with ellipsis.
 *
 * @param {string} str
 * @param {number} maxLength
 * @returns {string}
 */
export function truncate(str, maxLength = 80) {
  if (!str || str.length <= maxLength) return str || ''
  return str.slice(0, maxLength) + '…'
}
