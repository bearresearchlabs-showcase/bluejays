'use client'

import React, { useState } from 'react'
import { List, ListItem, ListItemText, ListItemButton } from '../data-display/List'
import TextField from '../forms/TextField'
import Checkbox from '../forms/Checkbox'
import Button from '../Button'
import { Stack } from '../layout/Stack'
import { Paper } from '../layout/Paper'
import { clsx } from '../utils'

/**
 * TransferList Component
 * Dual list transfer component
 */

export interface TransferListItem {
  id: string | number
  label: string
  disabled?: boolean
}

export interface TransferListProps {
  leftItems: TransferListItem[]
  rightItems: TransferListItem[]
  onTransfer?: (items: TransferListItem[], direction: 'left' | 'right') => void
  leftTitle?: string
  rightTitle?: string
  searchable?: boolean
  className?: string
}

export function TransferList({
  leftItems: initialLeftItems,
  rightItems: initialRightItems,
  onTransfer,
  leftTitle = 'Available',
  rightTitle = 'Selected',
  searchable = false,
  className,
}: TransferListProps) {
  const [leftItems, setLeftItems] = useState(initialLeftItems)
  const [rightItems, setRightItems] = useState(initialRightItems)
  const [leftSelected, setLeftSelected] = useState<Set<string | number>>(new Set())
  const [rightSelected, setRightSelected] = useState<Set<string | number>>(new Set())
  const [leftSearch, setLeftSearch] = useState('')
  const [rightSearch, setRightSearch] = useState('')

  const filteredLeftItems = leftItems.filter((item) =>
    searchable ? item.label.toLowerCase().includes(leftSearch.toLowerCase()) : true
  )
  const filteredRightItems = rightItems.filter((item) =>
    searchable ? item.label.toLowerCase().includes(rightSearch.toLowerCase()) : true
  )

  const handleTransfer = (direction: 'left' | 'right') => {
    if (direction === 'right') {
      const itemsToTransfer = leftItems.filter((item) => leftSelected.has(item.id))
      setLeftItems(leftItems.filter((item) => !leftSelected.has(item.id)))
      setRightItems([...rightItems, ...itemsToTransfer])
      setLeftSelected(new Set())
      onTransfer?.(itemsToTransfer, 'right')
    } else {
      const itemsToTransfer = rightItems.filter((item) => rightSelected.has(item.id))
      setRightItems(rightItems.filter((item) => !rightSelected.has(item.id)))
      setLeftItems([...leftItems, ...itemsToTransfer])
      setRightSelected(new Set())
      onTransfer?.(itemsToTransfer, 'left')
    }
  }

  const handleSelectAll = (side: 'left' | 'right') => {
    const items = side === 'left' ? filteredLeftItems : filteredRightItems
    const selected = side === 'left' ? leftSelected : rightSelected
    const setSelected = side === 'left' ? setLeftSelected : setRightSelected

    const allSelected = items.every((item) => selected.has(item.id))
    if (allSelected) {
      setSelected(new Set())
    } else {
      setSelected(new Set(items.map((item) => item.id)))
    }
  }

  const handleToggleItem = (side: 'left' | 'right', id: string | number) => {
    const selected = side === 'left' ? leftSelected : rightSelected
    const setSelected = side === 'left' ? setLeftSelected : setRightSelected

    const newSelected = new Set(selected)
    if (newSelected.has(id)) {
      newSelected.delete(id)
    } else {
      newSelected.add(id)
    }
    setSelected(newSelected)
  }

  const renderList = (side: 'left' | 'right') => {
    const items = side === 'left' ? filteredLeftItems : filteredRightItems
    const selected = side === 'left' ? leftSelected : rightSelected
    const title = side === 'left' ? leftTitle : rightTitle
    const search = side === 'left' ? leftSearch : rightSearch
    const setSearch = side === 'left' ? setLeftSearch : setRightSearch
    const allSelected = items.length > 0 && items.every((item) => selected.has(item.id))

    return (
      <Paper elevation={1} style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: '300px' }}>
        <div style={{ padding: 'var(--spacing-4)', borderBottom: '1px solid var(--color-border-primary)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: searchable ? 'var(--spacing-2)' : 0 }}>
            <h3 style={{ fontSize: 'var(--font-size-base)', fontWeight: 'var(--font-weight-medium)', margin: 0 }}>
              {title}
            </h3>
            <Checkbox checked={allSelected} onChange={() => handleSelectAll(side)} />
          </div>
          {searchable && (
            <TextField
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search..."
              size="sm"
              fullWidth
            />
          )}
        </div>
        <div style={{ flex: 1, overflowY: 'auto' }}>
          <List dense>
            {items.map((item) => (
              <ListItemButton
                key={item.id}
                onClick={() => !item.disabled && handleToggleItem(side, item.id)}
                selected={selected.has(item.id)}
              >
                <Checkbox checked={selected.has(item.id)} disabled={item.disabled} />
                <ListItemText primary={item.label} />
              </ListItemButton>
            ))}
          </List>
        </div>
      </Paper>
    )
  }

  return (
    <Stack direction="row" spacing={2} className={clsx('transfer-list', className)}>
      {renderList('left')}
      <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 'var(--spacing-2)' }}>
        <Button
          variant="primary"
          size="sm"
          onClick={() => handleTransfer('right')}
          disabled={leftSelected.size === 0}
        >
          ›
        </Button>
        <Button
          variant="primary"
          size="sm"
          onClick={() => handleTransfer('left')}
          disabled={rightSelected.size === 0}
        >
          ‹
        </Button>
      </div>
      {renderList('right')}
    </Stack>
  )
}
