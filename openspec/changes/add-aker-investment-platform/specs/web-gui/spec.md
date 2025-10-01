# Web GUI Specification

## Overview

The Aker Investment Platform web GUI provides a comprehensive multi-page interface for market screening, property analysis, portfolio management, and investment reporting. The interface prioritizes clarity, data visualization, and efficient workflow for real estate investment analysis.

## Architecture

### Technology Stack

- **Framework**: Streamlit (rapid prototyping) or Dash/Plotly (production)
- **Visualization**: Plotly, Mapbox GL JS, Folium
- **Styling**: Custom CSS with professional finance theme
- **Data Tables**: AG Grid or React-Table
- **Export**: PDF (ReportLab), Excel (openpyxl), CSV

### Design Principles

1. **Data-First**: Prioritize clear presentation of metrics and insights
2. **Responsive**: Mobile-friendly, tablet-optimized
3. **Performance**: Lazy loading, caching, progressive rendering
4. **Accessibility**: WCAG 2.1 AA compliance
5. **Trust**: Professional color palette (blues, grays), clear typography

## Page Structure

### Navigation

The system SHALL provide a consistent navigation structure across all pages.

#### Scenario: Global navigation bar

- **WHEN** user visits any page
- **THEN** the system displays a fixed top navigation bar
- **AND** highlights the current active page
- **AND** provides quick access to: Dashboard, Markets, Portfolio, Reports, Settings

#### Scenario: Mobile navigation

- **WHEN** user accesses the platform on mobile device (<768px width)
- **THEN** the system displays a hamburger menu
- **AND** provides collapsible navigation drawer
- **AND** maintains all navigation functionality

---

## Requirements

### Requirement: Dashboard Page

The system SHALL provide a comprehensive dashboard with key metrics, recent activity, and quick actions.

#### Scenario: Dashboard overview

- **WHEN** user navigates to the dashboard
- **THEN** the system displays:
  - Total portfolio value and ROI
  - Active markets being tracked (count)
  - Recent screening results (last 7 days)
  - Market performance summary (top 5 markets by score)
  - Cache performance metrics (hit rate, recent activity)

#### Scenario: Quick actions

- **WHEN** user is on dashboard
- **THEN** the system provides quick action buttons:
  - "Screen New Markets" (opens market screening)
  - "Run Analysis" (opens analysis wizard)
  - "Generate Report" (opens report builder)
  - "Refresh Data" (triggers cache warming)

#### Scenario: Interactive charts

- **WHEN** user views dashboard
- **THEN** the system displays interactive charts:
  - Portfolio value over time (line chart)
  - Market score distribution (histogram)
  - Risk-adjusted returns (scatter plot)
  - Geographic distribution (choropleth map)

---

### Requirement: Market Screening Page

The system SHALL provide an interface for screening and filtering markets based on investment criteria.

#### Scenario: Market search and filter

- **WHEN** user navigates to market screening page
- **THEN** the system displays:
  - Search bar for market name (autocomplete enabled)
  - Filter panel with sliders for:
    - Supply constraint score (0-100)
    - Innovation employment score (0-100)
    - Urban convenience score (0-100)
    - Risk multiplier (0.7-1.3)
  - "Apply Filters" and "Reset" buttons

#### Scenario: Screening results table

- **WHEN** user applies filters or searches
- **THEN** the system displays a sortable table with columns:
  - Market name (clickable link to details)
  - State
  - Composite score
  - Supply constraint score
  - Jobs score
  - Urban score
  - Outdoor score
  - Risk multiplier
  - Actions (View Details, Add to Portfolio)
- **AND** allows sorting by any column
- **AND** supports pagination (50 results per page)

#### Scenario: Batch screening

- **WHEN** user clicks "Screen Multiple Markets"
- **THEN** the system displays file upload interface
- **AND** accepts CSV with market list
- **AND** shows progress bar during processing
- **AND** displays results in table upon completion

#### Scenario: Export screening results

- **WHEN** user clicks "Export" on results table
- **THEN** the system provides format options: CSV, Excel, PDF
- **AND** generates downloadable file with all visible columns
- **AND** includes filter criteria in export metadata

---

### Requirement: Market Details Page

The system SHALL provide detailed analysis and visualizations for individual markets.

#### Scenario: Market overview section

- **WHEN** user views market details
- **THEN** the system displays:
  - Market name, state, CBSA code
  - Composite score (large, prominent display)
  - Risk-adjusted score
  - Score breakdown (supply, jobs, urban, outdoor)
  - Risk assessment summary

#### Scenario: Interactive score visualization

- **WHEN** user views market details
- **THEN** the system displays:
  - Radar chart showing score components
  - Risk multiplier gauge chart
  - Score percentile vs. all markets (bar chart)
  - Confidence intervals (if available)

#### Scenario: Map visualization

- **WHEN** user views market details
- **THEN** the system displays an interactive map showing:
  - Market boundary (if available)
  - Nearby amenities (POI from OSM)
  - Points of interest (urban centers, outdoor access)
  - Risk zones (flood, wildfire, seismic)
- **AND** allows zoom, pan, layer toggling

#### Scenario: Data source transparency

- **WHEN** user views market details
- **THEN** the system displays "Data Sources" section with:
  - List of data sources used (Census, BLS, OSM, etc.)
  - Last updated timestamp for each source
  - Data quality indicators
  - Links to source documentation

#### Scenario: Historical trends

- **WHEN** user views market details
- **THEN** the system displays time-series charts for:
  - Employment growth (last 5 years)
  - Building permits (last 5 years)
  - Population growth (last 10 years)
  - Median income trends

---

### Requirement: Portfolio Management Page

The system SHALL provide an interface for managing tracked markets and investment portfolios.

#### Scenario: Portfolio overview

- **WHEN** user navigates to portfolio page
- **THEN** the system displays:
  - Total markets tracked (count)
  - Average composite score
  - Portfolio-wide risk metrics
  - Total estimated market value

#### Scenario: Portfolio markets table

- **WHEN** user views portfolio
- **THEN** the system displays a table with:
  - Market name (clickable)
  - Date added
  - Current score
  - Score change since added
  - Investment status (Prospect, Committed, Active)
  - Notes field (editable)
  - Actions (View Details, Remove, Export)

#### Scenario: Add market to portfolio

- **WHEN** user clicks "Add Market"
- **THEN** the system displays search modal
- **AND** allows market selection from screening results
- **AND** prompts for investment status and notes
- **AND** adds market to portfolio on confirmation

#### Scenario: Portfolio comparison

- **WHEN** user selects multiple markets (checkbox)
- **THEN** the system enables "Compare" button
- **AND** clicking displays side-by-side comparison table
- **AND** shows score differences highlighted
- **AND** displays comparative charts (radar, bar)

#### Scenario: Portfolio alerts

- **WHEN** user views portfolio
- **THEN** the system displays alerts for:
  - Markets with significant score changes (>5 points)
  - New risk factors detected
  - Data source updates available
- **AND** allows dismissing or acknowledging alerts

---

### Requirement: Reports Page

The system SHALL provide a report generation and management interface.

#### Scenario: Report templates

- **WHEN** user navigates to reports page
- **THEN** the system displays available templates:
  - Market Analysis Report (single market)
  - Portfolio Summary Report (all tracked markets)
  - Comparative Market Analysis (2-5 markets)
  - Risk Assessment Report (market or portfolio)
  - Executive Summary (high-level overview)

#### Scenario: Generate report

- **WHEN** user selects report template
- **THEN** the system displays configuration wizard with steps:
  1. Select markets (dropdown or search)
  2. Choose sections (checkboxes for components)
  3. Configure options (date range, detail level)
  4. Preview report (scrollable preview)
  5. Generate final report (PDF, Excel, HTML)

#### Scenario: Report preview

- **WHEN** user previews report
- **THEN** the system displays:
  - Scrollable report preview with styling
  - Page count and estimated file size
  - Section navigation (table of contents)
  - Edit button to return to configuration

#### Scenario: Report history

- **WHEN** user views reports page
- **THEN** the system displays list of generated reports:
  - Report name
  - Date generated
  - Markets included
  - File size
  - Actions (Download, Regenerate, Delete)

#### Scenario: Scheduled reports

- **WHEN** user clicks "Schedule Report"
- **THEN** the system displays scheduling interface:
  - Frequency (daily, weekly, monthly)
  - Day/time selection
  - Email recipients (comma-separated)
  - Report format (PDF, Excel)
  - Active/inactive toggle

---

### Requirement: Settings Page

The system SHALL provide configuration and account management interface.

#### Scenario: User profile

- **WHEN** user navigates to settings
- **THEN** the system displays profile section with:
  - Name (editable)
  - Email (editable)
  - Organization (editable)
  - Role/title (editable)
  - "Save Changes" button

#### Scenario: API configuration

- **WHEN** user views settings
- **THEN** the system displays API keys section:
  - Census API key (masked, with reveal button)
  - BLS API key (masked)
  - Other API keys as needed
  - "Test Connection" button for each
  - Status indicators (connected, error, not configured)

#### Scenario: Cache settings

- **WHEN** user views settings
- **THEN** the system displays cache configuration:
  - Memory cache size (slider, 128-512MB)
  - SQLite cache path (text input)
  - TTL policies (dropdown per source)
  - "Clear Cache" button (with confirmation)
  - Cache statistics summary

#### Scenario: Display preferences

- **WHEN** user views settings
- **THEN** the system displays preferences:
  - Theme (Light, Dark, Auto)
  - Default map style (Street, Satellite, Terrain)
  - Number format (US, European)
  - Date format (MM/DD/YYYY, DD/MM/YYYY, YYYY-MM-DD)
  - Results per page (25, 50, 100)

#### Scenario: Export preferences

- **WHEN** user views settings
- **THEN** the system displays export options:
  - Default export format (CSV, Excel, PDF)
  - Include metadata in exports (checkbox)
  - Logo upload for PDF reports
  - Report footer text (textarea)

---

### Requirement: Data Management Page

The system SHALL provide an interface for managing data sources and cache.

#### Scenario: Data source status

- **WHEN** user navigates to data management
- **THEN** the system displays table of data sources:
  - Source name (Census, BLS, OSM, etc.)
  - Status (Active, Error, Rate Limited)
  - Last updated timestamp
  - Cache hit rate
  - Actions (Refresh, Clear Cache, Configure)

#### Scenario: Cache warming

- **WHEN** user clicks "Warm Cache"
- **THEN** the system displays cache warming interface:
  - Market selection (upload CSV or select from portfolio)
  - Data sources to warm (checkboxes)
  - "Start Warming" button
  - Progress bar during operation
  - Completion summary (markets warmed, time taken, cache hits)

#### Scenario: Cache inspection

- **WHEN** user clicks "Inspect Cache"
- **THEN** the system displays cache browser:
  - Search bar for cache keys
  - List of recent cache entries
  - Entry details (key, size, TTL, last accessed)
  - "View Data" button (shows JSON in modal)
  - "Delete" button (with confirmation)

#### Scenario: Data refresh

- **WHEN** user clicks "Refresh Data Source"
- **THEN** the system prompts for confirmation
- **AND** clears cache for that source
- **AND** re-fetches data for tracked markets
- **AND** displays progress and results

---

### Requirement: Help & Documentation Page

The system SHALL provide comprehensive help and documentation.

#### Scenario: User guide

- **WHEN** user navigates to help page
- **THEN** the system displays sections:
  - Getting Started
  - Market Screening Guide
  - Understanding Scores
  - Risk Assessment
  - Report Generation
  - API Configuration
  - Troubleshooting

#### Scenario: Interactive tutorials

- **WHEN** user clicks "Take Tutorial"
- **THEN** the system launches interactive walkthrough
- **AND** highlights UI elements with tooltips
- **AND** provides step-by-step instructions
- **AND** allows skipping or completing tutorial

#### Scenario: FAQ section

- **WHEN** user views help page
- **THEN** the system displays collapsible FAQ items:
  - What data sources are used?
  - How is the composite score calculated?
  - How often is data updated?
  - What do risk multipliers mean?
  - How do I interpret the scoring?

#### Scenario: Contact support

- **WHEN** user clicks "Contact Support"
- **THEN** the system displays contact form:
  - Subject (dropdown: Bug, Feature Request, Question)
  - Message (textarea)
  - Attachment upload (optional)
  - "Send" button
  - Email confirmation on submission

---

## Visual Design Requirements

### Requirement: Color Palette and Typography

The system SHALL use a professional, trust-inspiring design language.

#### Scenario: Primary color palette

- **WHEN** rendering any page
- **THEN** the system uses:
  - Primary: #1E40AF (Blue 800) - main actions, links
  - Secondary: #059669 (Green 600) - positive indicators, success
  - Warning: #D97706 (Amber 600) - alerts, caution
  - Danger: #DC2626 (Red 600) - errors, high risk
  - Neutral: #6B7280 (Gray 500) - text, borders
  - Background: #F9FAFB (Gray 50) - page background

#### Scenario: Typography

- **WHEN** rendering text
- **THEN** the system uses:
  - Headings: Inter (sans-serif), bold, sizes 24-36px
  - Body: Inter (sans-serif), regular, 14-16px
  - Monospace: JetBrains Mono, 12-14px (for data, code)
  - Line height: 1.5 for readability

#### Scenario: Score visualization colors

- **WHEN** displaying scores
- **THEN** the system uses color gradient:
  - 0-40: #DC2626 (Red) - Poor
  - 41-60: #D97706 (Orange) - Fair
  - 61-80: #2563EB (Blue) - Good
  - 81-100: #059669 (Green) - Excellent

---

### Requirement: Responsive Design

The system SHALL provide optimal experience across all device sizes.

#### Scenario: Desktop layout (>1024px)

- **WHEN** viewing on desktop
- **THEN** the system displays:
  - Side navigation bar (fixed left, 240px)
  - Main content area (fluid width)
  - Multi-column layouts where appropriate
  - Data tables with all columns visible

#### Scenario: Tablet layout (768px-1024px)

- **WHEN** viewing on tablet
- **THEN** the system displays:
  - Collapsible side navigation
  - Single or two-column layouts
  - Horizontally scrollable tables
  - Touch-optimized controls (larger buttons)

#### Scenario: Mobile layout (<768px)

- **WHEN** viewing on mobile
- **THEN** the system displays:
  - Hamburger menu navigation
  - Single-column stacked layouts
  - Card-based design for lists
  - Swipeable carousels for charts
  - Bottom navigation bar for main actions

---

### Requirement: Performance and Loading States

The system SHALL provide clear feedback during data loading and processing.

#### Scenario: Page load skeleton

- **WHEN** page is loading
- **THEN** the system displays skeleton screens:
  - Gray placeholder boxes for content
  - Pulsing animation to indicate loading
  - Matches layout of loaded content

#### Scenario: Progressive data loading

- **WHEN** loading large datasets (>100 markets)
- **THEN** the system:
  - Loads and displays first 50 results immediately
  - Lazy loads remaining results on scroll
  - Shows "Loading more..." indicator
  - Maintains scroll position

#### Scenario: Operation feedback

- **WHEN** user triggers long operation (cache warming, report generation)
- **THEN** the system displays:
  - Modal or banner with progress bar
  - Percentage complete
  - Estimated time remaining
  - Cancel button (if applicable)
  - Success message on completion

---

## Accessibility Requirements

### Requirement: Keyboard Navigation

The system SHALL be fully operable via keyboard.

#### Scenario: Tab navigation

- **WHEN** user presses Tab key
- **THEN** the system moves focus to next interactive element
- **AND** displays visible focus indicator
- **AND** follows logical tab order (top-to-bottom, left-to-right)

#### Scenario: Keyboard shortcuts

- **WHEN** user presses keyboard shortcuts
- **THEN** the system responds:
  - `Ctrl+K` or `Cmd+K`: Open search
  - `/`: Focus search bar
  - `Esc`: Close modal or cancel operation
  - `Ctrl+S` or `Cmd+S`: Save/export current view

---

### Requirement: Screen Reader Support

The system SHALL provide descriptive labels and ARIA attributes for assistive technologies.

#### Scenario: Semantic HTML

- **WHEN** rendering page structure
- **THEN** the system uses semantic HTML5 elements:
  - `<nav>` for navigation
  - `<main>` for main content
  - `<article>` for market cards
  - `<table>` for data tables
  - `<button>` for actions (not `<div>` with click handlers)

#### Scenario: ARIA labels

- **WHEN** rendering interactive elements
- **THEN** the system provides:
  - `aria-label` for icon-only buttons
  - `aria-describedby` for form fields with help text
  - `aria-live` for dynamic content updates
  - `role` attributes where semantic HTML insufficient

---

## Security and Authentication

### Requirement: User Authentication

The system SHALL require authentication for all pages except public landing page.

#### Scenario: Login page

- **WHEN** unauthenticated user accesses platform
- **THEN** the system redirects to login page
- **AND** displays email/password fields
- **AND** provides "Remember Me" checkbox
- **AND** includes "Forgot Password" link

#### Scenario: Session management

- **WHEN** user logs in successfully
- **THEN** the system creates session token
- **AND** stores token in httpOnly cookie
- **AND** maintains session for 24 hours
- **AND** requires re-authentication after expiry

#### Scenario: Logout

- **WHEN** user clicks "Logout"
- **THEN** the system invalidates session token
- **AND** clears all cookies
- **AND** redirects to login page
- **AND** prevents back button access to authenticated pages

---

## Integration Requirements

### Requirement: Backend API Integration

The system SHALL integrate with the Python backend via REST API.

#### Scenario: API endpoint structure

- **WHEN** GUI makes API requests
- **THEN** the system uses endpoints:
  - `GET /api/markets` - List markets
  - `GET /api/markets/{id}` - Market details
  - `POST /api/markets/screen` - Screen markets
  - `GET /api/portfolio` - Portfolio markets
  - `POST /api/reports/generate` - Generate report
  - `GET /api/cache/stats` - Cache statistics

#### Scenario: Error handling

- **WHEN** API request fails
- **THEN** the system displays user-friendly error message
- **AND** logs technical details to console
- **AND** provides retry button
- **AND** maintains UI state (no data loss)

#### Scenario: Loading states

- **WHEN** API request is in progress
- **THEN** the system shows loading indicator
- **AND** disables form submission (prevent duplicate requests)
- **AND** displays timeout warning after 30 seconds

---

## Export and Reporting

### Requirement: PDF Report Generation

The system SHALL generate professional PDF reports with charts and tables.

#### Scenario: PDF report structure

- **WHEN** user generates PDF report
- **THEN** the system includes:
  - Cover page with logo, title, date, author
  - Executive summary (1 page)
  - Methodology section
  - Market analysis sections (one per market)
  - Charts and visualizations (embedded as images)
  - Data tables (formatted)
  - Footer with page numbers
  - Appendix with data sources

#### Scenario: Chart rendering in PDF

- **WHEN** including charts in PDF
- **THEN** the system:
  - Renders charts as high-resolution PNG (300 DPI)
  - Maintains color scheme and styling
  - Includes chart legends and labels
  - Fits charts to page width

---

## Testing and Quality Assurance

### Requirement: Browser Compatibility

The system SHALL function correctly across modern browsers.

#### Scenario: Supported browsers

- **WHEN** user accesses platform
- **THEN** the system supports:
  - Chrome 90+ (full support)
  - Firefox 88+ (full support)
  - Safari 14+ (full support)
  - Edge 90+ (full support)
- **AND** displays warning for unsupported browsers

#### Scenario: Feature detection

- **WHEN** browser lacks required feature
- **THEN** the system provides fallback or graceful degradation
- **AND** maintains core functionality
- **AND** informs user of limited functionality

---

## Implementation Priority

### Phase 1: Core Pages (MVP)

1. Dashboard (basic metrics)
2. Market Screening (search, filter, results table)
3. Market Details (scores, basic charts)
4. Settings (API keys, basic config)

### Phase 2: Portfolio & Reports

5. Portfolio Management (add, remove, track)
6. Reports (basic templates, PDF generation)
7. Data Management (cache inspection, warming)

### Phase 3: Enhanced Features

8. Advanced visualizations (interactive maps, complex charts)
9. Scheduled reports and alerts
10. Help & Documentation
11. Performance optimizations
12. Mobile-specific enhancements
