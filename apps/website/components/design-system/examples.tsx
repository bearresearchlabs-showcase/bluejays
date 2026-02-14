'use client'

/**
 * Design System Examples
 * Demonstrates usage of all design system components
 * Based on OpenAI Apps SDK UI Guidelines
 */

import React, { useState } from 'react'
import {
  InlineCard,
  InlineCarousel,
  Badge,
  Button,
  StatsCard,
  FullscreenView,
  PictureInPicture
} from './index'

export function DesignSystemExamples() {
  const [showFullscreen, setShowFullscreen] = useState(false)
  const [showPiP, setShowPiP] = useState(false)

  const carouselItems = [
    {
      id: 'db6',
      title: 'Weather Database',
      metadata: ['11 tables', '30 queries'],
      badge: 'Large',
      actionLabel: 'View',
      onClick: () => console.log('View db6')
    },
    {
      id: 'db7',
      title: 'Maritime Database',
      metadata: ['14 tables', '30 queries'],
      badge: 'Medium',
      actionLabel: 'View',
      onClick: () => console.log('View db7')
    },
    {
      id: 'db8',
      title: 'Job Market Database',
      metadata: ['13 tables', '30 queries'],
      badge: 'Medium',
      actionLabel: 'View',
      onClick: () => console.log('View db8')
    }
  ]

  return (
    <div style={{ padding: 'var(--spacing-8)', maxWidth: '1200px', margin: '0 auto' }}>
      <h1 style={{ fontSize: 'var(--font-size-4xl)', marginBottom: 'var(--spacing-8)' }}>
        Design System Examples
      </h1>

      {/* Inline Card Examples */}
      <section style={{ marginBottom: 'var(--spacing-12)' }}>
        <h2 style={{ fontSize: 'var(--font-size-2xl)', marginBottom: 'var(--spacing-6)' }}>
          Inline Cards
        </h2>
        
        <InlineCard
          title="Database Statistics"
          actions={[
            { label: 'View Details', onClick: () => {}, primary: true },
            { label: 'Export', onClick: () => {} }
          ]}
        >
          <div>
            <StatsCard value={10} label="Total Databases" />
          </div>
        </InlineCard>

        <InlineCard
          title="Quick Actions"
          expandable
          onExpand={() => setShowFullscreen(true)}
        >
          <p style={{ color: 'var(--color-text-secondary)' }}>
            Click expand to view fullscreen experience
          </p>
        </InlineCard>
      </section>

      {/* Carousel Example */}
      <section style={{ marginBottom: 'var(--spacing-12)' }}>
        <h2 style={{ fontSize: 'var(--font-size-2xl)', marginBottom: 'var(--spacing-6)' }}>
          Inline Carousel
        </h2>
        
        <InlineCarousel
          title="Available Databases"
          items={carouselItems}
        />
      </section>

      {/* Badge Examples */}
      <section style={{ marginBottom: 'var(--spacing-12)' }}>
        <h2 style={{ fontSize: 'var(--font-size-2xl)', marginBottom: 'var(--spacing-6)' }}>
          Badges
        </h2>
        
        <div style={{ display: 'flex', gap: 'var(--spacing-4)', flexWrap: 'wrap' }}>
          <Badge variant="default">Default</Badge>
          <Badge variant="success">Success</Badge>
          <Badge variant="warning">Warning</Badge>
          <Badge variant="error">Error</Badge>
          <Badge variant="info">Info</Badge>
          <Badge variant="default" size="sm">Small</Badge>
        </div>
      </section>

      {/* Button Examples */}
      <section style={{ marginBottom: 'var(--spacing-12)' }}>
        <h2 style={{ fontSize: 'var(--font-size-2xl)', marginBottom: 'var(--spacing-6)' }}>
          Buttons
        </h2>
        
        <div style={{ display: 'flex', gap: 'var(--spacing-4)', flexWrap: 'wrap', alignItems: 'center' }}>
          <Button variant="primary" size="md">Primary</Button>
          <Button variant="secondary" size="md">Secondary</Button>
          <Button variant="ghost" size="md">Ghost</Button>
          <Button variant="primary" size="sm">Small</Button>
          <Button variant="primary" size="lg">Large</Button>
          <Button variant="primary" disabled>Disabled</Button>
          <Button variant="primary" fullWidth>Full Width</Button>
        </div>
      </section>

      {/* Stats Card Examples */}
      <section style={{ marginBottom: 'var(--spacing-12)' }}>
        <h2 style={{ fontSize: 'var(--font-size-2xl)', marginBottom: 'var(--spacing-6)' }}>
          Stats Cards
        </h2>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--spacing-4)' }}>
          <StatsCard value={10} label="Databases" />
          <StatsCard value={131} label="Tables" trend={{ value: 5, direction: 'up' }} />
          <StatsCard value={300} label="Queries" trend={{ value: 2, direction: 'down' }} />
        </div>
      </section>

      {/* Fullscreen Example */}
      {showFullscreen && (
        <FullscreenView
          title="Fullscreen Experience"
          onClose={() => setShowFullscreen(false)}
        >
          <div style={{ padding: 'var(--spacing-6)' }}>
            <h3 style={{ fontSize: 'var(--font-size-xl)', marginBottom: 'var(--spacing-4)' }}>
              Immersive Content
            </h3>
            <p style={{ color: 'var(--color-text-secondary)', lineHeight: 'var(--line-height-relaxed)' }}>
              This is a fullscreen view for rich, multi-step workflows or detailed content exploration.
              The ChatGPT composer remains accessible for continued conversation.
            </p>
          </div>
        </FullscreenView>
      )}

      {/* Picture-in-Picture Example */}
      {showPiP && (
        <PictureInPicture
          title="Live Session"
          onClose={() => setShowPiP(false)}
          pinned={true}
        >
          <div style={{ padding: 'var(--spacing-4)' }}>
            <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)' }}>
              This PiP widget stays visible while conversation continues.
              Perfect for games, live collaboration, or ongoing sessions.
            </p>
          </div>
        </PictureInPicture>
      )}

      <section style={{ marginBottom: 'var(--spacing-12)' }}>
        <h2 style={{ fontSize: 'var(--font-size-2xl)', marginBottom: 'var(--spacing-6)' }}>
          Display Modes
        </h2>
        
        <div style={{ display: 'flex', gap: 'var(--spacing-4)' }}>
          <Button onClick={() => setShowFullscreen(true)}>
            Open Fullscreen
          </Button>
          <Button onClick={() => setShowPiP(true)}>
            Open Picture-in-Picture
          </Button>
        </div>
      </section>
    </div>
  )
}
