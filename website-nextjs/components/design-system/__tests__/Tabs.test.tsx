import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import { Tabs, TabList, Tab, TabPanel } from '../navigation/Tabs'

describe('Tabs Component', () => {
  it('renders tabs with tab list and panels', () => {
    render(
      <Tabs value="1">
        <TabList>
          <Tab value="1" label="Tab 1" />
          <Tab value="2" label="Tab 2" />
        </TabList>
        <TabPanel value="1">Content 1</TabPanel>
        <TabPanel value="2">Content 2</TabPanel>
      </Tabs>
    )
    
    expect(screen.getByText('Tab 1')).toBeInTheDocument()
    expect(screen.getByText('Tab 2')).toBeInTheDocument()
    expect(screen.getByText('Content 1')).toBeInTheDocument()
  })

  it('only renders active tab panel', () => {
    render(
      <Tabs value="1">
        <TabList>
          <Tab value="1" label="Tab 1" />
          <Tab value="2" label="Tab 2" />
        </TabList>
        <TabPanel value="1">Content 1</TabPanel>
        <TabPanel value="2">Content 2</TabPanel>
      </Tabs>
    )
    
    expect(screen.getByText('Content 1')).toBeInTheDocument()
    expect(screen.queryByText('Content 2')).not.toBeInTheDocument()
  })

  it('calls onChange when tab is clicked', () => {
    const handleChange = jest.fn()
    render(
      <Tabs value="1" onChange={handleChange}>
        <TabList>
          <Tab value="1" label="Tab 1" />
          <Tab value="2" label="Tab 2" />
        </TabList>
        <TabPanel value="1">Content 1</TabPanel>
        <TabPanel value="2">Content 2</TabPanel>
      </Tabs>
    )
    
    const tab2 = screen.getByText('Tab 2')
    fireEvent.click(tab2)
    
    expect(handleChange).toHaveBeenCalledWith('2')
  })

  it('marks active tab as selected', () => {
    render(
      <Tabs value="2">
        <TabList>
          <Tab value="1" label="Tab 1" />
          <Tab value="2" label="Tab 2" />
        </TabList>
        <TabPanel value="1">Content 1</TabPanel>
        <TabPanel value="2">Content 2</TabPanel>
      </Tabs>
    )
    
    const tab2 = screen.getByText('Tab 2').closest('button')!
    expect(tab2.className).toContain('tab')
    expect(tab2.className).toContain('tab-selected')
  })

  it('does not call onChange when disabled tab is clicked', () => {
    const handleChange = jest.fn()
    render(
      <Tabs value="1" onChange={handleChange}>
        <TabList>
          <Tab value="1" label="Tab 1" />
          <Tab value="2" label="Tab 2" disabled />
        </TabList>
        <TabPanel value="1">Content 1</TabPanel>
        <TabPanel value="2">Content 2</TabPanel>
      </Tabs>
    )
    
    const tab2 = screen.getByText('Tab 2')
    fireEvent.click(tab2)
    
    expect(handleChange).not.toHaveBeenCalled()
  })

  it('renders tabs with icons', () => {
    render(
      <Tabs value="1">
        <TabList>
          <Tab value="1" label="Tab 1" icon={<span data-testid="icon">★</span>} />
        </TabList>
        <TabPanel value="1">Content</TabPanel>
      </Tabs>
    )
    
    expect(screen.getByTestId('icon')).toBeInTheDocument()
  })
})
