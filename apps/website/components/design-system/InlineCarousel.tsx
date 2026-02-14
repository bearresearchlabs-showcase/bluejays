'use client'

import React, { useRef, useState } from 'react'

/**
 * Inline Carousel Component
 * A set of cards presented side-by-side for quick scanning.
 * Based on OpenAI Apps SDK UI guidelines.
 * 
 * When to use:
 * - Presenting a small list of similar items (3-8 items)
 * - Items have visual content and metadata
 */

interface CarouselItem {
  id: string
  image?: string
  title: string
  metadata?: string[]
  badge?: string
  onClick?: () => void
  actionLabel?: string
}

interface InlineCarouselProps {
  items: CarouselItem[]
  title?: string
  className?: string
}

export default function InlineCarousel({
  items,
  title,
  className = ''
}: InlineCarouselProps) {
  const scrollRef = useRef<HTMLDivElement>(null)
  const [canScrollLeft, setCanScrollLeft] = useState(false)
  const [canScrollRight, setCanScrollRight] = useState(true)

  const checkScroll = () => {
    if (!scrollRef.current) return
    const { scrollLeft, scrollWidth, clientWidth } = scrollRef.current
    setCanScrollLeft(scrollLeft > 0)
    setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 10)
  }

  const scroll = (direction: 'left' | 'right') => {
    if (!scrollRef.current) return
    const scrollAmount = scrollRef.current.clientWidth * 0.8
    scrollRef.current.scrollBy({
      left: direction === 'left' ? -scrollAmount : scrollAmount,
      behavior: 'smooth'
    })
  }

  React.useEffect(() => {
    checkScroll()
    const ref = scrollRef.current
    ref?.addEventListener('scroll', checkScroll)
    return () => ref?.removeEventListener('scroll', checkScroll)
  }, [items])

  return (
    <div className={`inline-carousel ${className}`} style={{ marginBottom: 'var(--spacing-6)' }}>
      {title && (
        <h3 style={{
          fontSize: 'var(--font-size-lg)',
          fontWeight: 'var(--font-weight-semibold)',
          marginBottom: 'var(--spacing-4)',
          color: 'var(--color-text-primary)'
        }}>
          {title}
        </h3>
      )}
      
      <div style={{ position: 'relative' }}>
        {canScrollLeft && (
          <button
            onClick={() => scroll('left')}
            style={{
              position: 'absolute',
              left: 0,
              top: '50%',
              transform: 'translateY(-50%)',
              zIndex: 10,
              background: 'var(--color-bg-primary)',
              border: '1px solid var(--color-border-primary)',
              borderRadius: 'var(--radius-full)',
              width: '32px',
              height: '32px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
              boxShadow: 'var(--shadow-md)'
            }}
            aria-label="Scroll left"
          >
            ←
          </button>
        )}
        
        <div
          ref={scrollRef}
          style={{
            display: 'flex',
            gap: 'var(--carousel-gap)',
            overflowX: 'auto',
            overflowY: 'hidden',
            scrollBehavior: 'smooth',
            scrollbarWidth: 'thin',
            padding: 'var(--spacing-2)',
            margin: '0 var(--spacing-2)'
          }}
          onScroll={checkScroll}
        >
          {items.map((item) => (
            <div
              key={item.id}
              onClick={item.onClick}
              style={{
                flex: '0 0 var(--carousel-item-width)',
                background: 'var(--color-bg-elevated)',
                border: '1px solid var(--color-border-primary)',
                borderRadius: 'var(--radius-lg)',
                overflow: 'hidden',
                cursor: item.onClick ? 'pointer' : 'default',
                transition: 'all var(--transition-base)',
                display: 'flex',
                flexDirection: 'column'
              }}
              onMouseEnter={(e) => {
                if (item.onClick) {
                  e.currentTarget.style.borderColor = 'var(--color-accent-primary)'
                  e.currentTarget.style.boxShadow = 'var(--shadow-md)'
                }
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'var(--color-border-primary)'
                e.currentTarget.style.boxShadow = 'none'
              }}
            >
              {item.image && (
                <div
                  style={{
                    width: '100%',
                    aspectRatio: '16/9',
                    background: 'var(--color-bg-secondary)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    overflow: 'hidden'
                  }}
                >
                  <img
                    src={item.image}
                    alt={item.title}
                    style={{
                      width: '100%',
                      height: '100%',
                      objectFit: 'cover'
                    }}
                  />
                </div>
              )}
              
              <div style={{ padding: 'var(--spacing-4)' }}>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'start',
                  marginBottom: 'var(--spacing-2)'
                }}>
                  <h4 style={{
                    fontSize: 'var(--font-size-base)',
                    fontWeight: 'var(--font-weight-semibold)',
                    color: 'var(--color-text-primary)',
                    margin: 0,
                    flex: 1
                  }}>
                    {item.title}
                  </h4>
                  {item.badge && (
                    <span style={{
                      padding: 'var(--spacing-1) var(--spacing-2)',
                      background: 'var(--color-bg-secondary)',
                      borderRadius: 'var(--radius-full)',
                      fontSize: 'var(--font-size-xs)',
                      fontWeight: 'var(--font-weight-medium)',
                      color: 'var(--color-text-secondary)',
                      whiteSpace: 'nowrap',
                      marginLeft: 'var(--spacing-2)'
                    }}>
                      {item.badge}
                    </span>
                  )}
                </div>
                
                {item.metadata && item.metadata.length > 0 && (
                  <div style={{
                    fontSize: 'var(--font-size-sm)',
                    color: 'var(--color-text-secondary)',
                    lineHeight: 'var(--line-height-relaxed)',
                    marginBottom: 'var(--spacing-3)'
                  }}>
                    {item.metadata.slice(0, 2).map((meta, idx) => (
                      <div key={idx}>{meta}</div>
                    ))}
                  </div>
                )}
                
                {item.actionLabel && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      item.onClick?.()
                    }}
                    style={{
                      width: '100%',
                      padding: 'var(--spacing-2) var(--spacing-4)',
                      background: 'var(--color-accent-primary)',
                      color: 'var(--color-bg-primary)',
                      border: 'none',
                      borderRadius: 'var(--radius-md)',
                      fontSize: 'var(--font-size-sm)',
                      fontWeight: 'var(--font-weight-medium)',
                      cursor: 'pointer',
                      transition: 'all var(--transition-base)'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = 'var(--color-accent-primary-hover)'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = 'var(--color-accent-primary)'
                    }}
                  >
                    {item.actionLabel}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
        
        {canScrollRight && (
          <button
            onClick={() => scroll('right')}
            style={{
              position: 'absolute',
              right: 0,
              top: '50%',
              transform: 'translateY(-50%)',
              zIndex: 10,
              background: 'var(--color-bg-primary)',
              border: '1px solid var(--color-border-primary)',
              borderRadius: 'var(--radius-full)',
              width: '32px',
              height: '32px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
              boxShadow: 'var(--shadow-md)'
            }}
            aria-label="Scroll right"
          >
            →
          </button>
        )}
      </div>
    </div>
  )
}
