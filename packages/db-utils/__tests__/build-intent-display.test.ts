/**
 * TDD/BDD tests for buildIntentDisplay (intent-focused natural language query descriptions)
 */

import { buildIntentDisplay, type QueryForIntent } from '../src/build-intent-display'

describe('buildIntentDisplay', () => {
  describe('Given a query with natural_language_query', () => {
    it('When natural_language_query is present and non-empty, Then returns it trimmed', () => {
      const q: QueryForIntent = {
        natural_language_query: '  I want to analyze weather station coverage by forecast office  ',
        description: 'Technical description',
      }
      expect(buildIntentDisplay(q)).toBe('I want to analyze weather station coverage by forecast office')
    })

    it('When natural_language_query is present, Then ignores other fields', () => {
      const q: QueryForIntent = {
        natural_language_query: 'Show top credit cards by rewards',
        use_case: 'Use case',
        business_value: 'Business value',
        purpose: 'Purpose',
        description: 'Description',
      }
      expect(buildIntentDisplay(q)).toBe('Show top credit cards by rewards')
    })
  })

  describe('Given a query with intent but no natural_language_query', () => {
    it('When intent is present and non-empty, Then returns it trimmed', () => {
      const q: QueryForIntent = {
        intent: '  Analyze forecast accuracy by boundary  ',
        description: 'Technical',
      }
      expect(buildIntentDisplay(q)).toBe('Analyze forecast accuracy by boundary')
    })
  })

  describe('Given a query with use_case, business_value, purpose, description', () => {
    it('When no natural_language_query or intent, Then combines use_case + business_value + purpose + description', () => {
      const q: QueryForIntent = {
        use_case: 'Custom Weather Impact Modeling',
        business_value: 'Forecast accuracy report by boundary',
        purpose: 'Insurance risk assessment',
        description: 'Spatial aggregations and CTEs',
      }
      const result = buildIntentDisplay(q)
      expect(result).toContain('Custom Weather Impact Modeling')
      expect(result).toContain('Forecast accuracy report by boundary')
      expect(result).toContain('Insurance risk assessment')
      expect(result).toContain('Spatial aggregations and CTEs')
    })

    it('When description duplicates use_case, Then does not add redundant description', () => {
      const q: QueryForIntent = {
        use_case: 'Weather modeling',
        description: 'Weather modeling with CTEs',
      }
      const result = buildIntentDisplay(q)
      expect(result).toBe('Weather modeling')
    })
  })

  describe('Given a query with only description', () => {
    it('When only description exists, Then returns description', () => {
      const q: QueryForIntent = {
        description: 'Enterprise-level spatial forecast analysis',
      }
      expect(buildIntentDisplay(q)).toBe('Enterprise-level spatial forecast analysis')
    })
  })

  describe('Given empty or missing fields', () => {
    it('When all fields are empty, Then returns empty string', () => {
      expect(buildIntentDisplay({})).toBe('')
    })

    it('When all fields are whitespace, Then returns empty string', () => {
      const q: QueryForIntent = {
        natural_language_query: '   ',
        intent: '  ',
        description: '  ',
      }
      expect(buildIntentDisplay(q)).toBe('')
    })
  })
})
