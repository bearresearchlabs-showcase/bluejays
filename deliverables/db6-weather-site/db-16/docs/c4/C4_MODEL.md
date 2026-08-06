# C4 Model Architecture - db-16 Flood Risk Assessment for M&A Due Diligence

**Database:** db-16 - Flood Risk Assessment Database  
**Purpose:** M&A Due Diligence for Real Estate Acquisitions  
**Created:** 2026-02-06

## Overview

This document contains C4 model architecture diagrams for db-16, a flood risk assessment system designed for large real estate firms specializing in Mergers & Acquisitions (M&A). The diagrams model the system at multiple levels of abstraction, focusing on M&A use cases.

## C4 Model Levels

1. **Level 1: System Context** - High-level view showing users and external systems
2. **Level 2: Container** - Applications and services within the system
3. **Level 3: Component** - Components within containers
4. **Level 4: Code** - Classes and functions (optional, for key components)

---

## Level 1: System Context Diagram

```plantuml
@startuml db16_system_context
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

LAYOUT_WITH_LEGEND()

title System Context - db-16 Flood Risk Assessment for M&A Due Diligence

Person(m_a_analyst, "M&A Analyst", "Conducts flood risk due diligence\non acquisition targets")
Person(m_a_manager, "M&A Manager", "Makes acquisition decisions\nbased on risk assessments")
Person(portfolio_manager, "Portfolio Manager", "Manages real estate\ninvestment portfolios")

System(db16_system, "Flood Risk Assessment System", "Comprehensive flood risk assessment\nfor M&A due diligence workflows")

System_Ext(fema_api, "FEMA API", "National Flood Hazard Layer\nflood zone data")
System_Ext(noaa_api, "NOAA API", "Sea level rise projections\nand high tide flooding data")
System_Ext(usgs_api, "USGS API", "Streamflow data from\n7,000+ gauges")
System_Ext(nasa_api, "NASA API", "Flood model predictions\nand inundation extents")

Rel(m_a_analyst, db16_system, "Conducts pre-acquisition\nrisk assessments", "HTTPS")
Rel(m_a_manager, db16_system, "Reviews risk reports\nfor acquisition decisions", "HTTPS")
Rel(portfolio_manager, db16_system, "Analyzes portfolio-level\nrisk metrics", "HTTPS")

Rel(db16_system, fema_api, "Retrieves flood zone\nboundaries and BFEs", "REST API")
Rel(db16_system, noaa_api, "Retrieves sea level rise\nprojections", "REST API")
Rel(db16_system, usgs_api, "Retrieves streamflow\nobservations", "REST API")
Rel(db16_system, nasa_api, "Retrieves flood model\npredictions", "REST API")

@enduml
```

**M&A Use Cases:**
- Pre-acquisition flood risk due diligence
- Acquisition target risk scoring
- Portfolio-level risk analysis
- Financial impact assessment for acquisition pricing

---

## Level 2: Container Diagram

```plantuml
@startuml db16_container
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

LAYOUT_WITH_LEGEND()

title Container Diagram - db-16 Flood Risk Assessment System

Person(m_a_analyst, "M&A Analyst")
Person(m_a_manager, "M&A Manager")

System_Ext(fema_api, "FEMA API")
System_Ext(noaa_api, "NOAA API")
System_Ext(usgs_api, "USGS API")
System_Ext(nasa_api, "NASA API")

Container(web_app, "Web Application", "React/TypeScript", "Provides M&A risk assessment\ninterface and dashboards")
Container(api_service, "API Service", "Python/FastAPI", "RESTful API for risk assessment\nqueries and data operations")
Container(spatial_engine, "Spatial Analysis Engine", "PostGIS/GeoPandas", "Performs spatial joins and\ngeographic analysis")
Container(risk_calculator, "Risk Calculator", "Python", "Multi-factor risk scoring\nand financial impact modeling")
ContainerDb(database, "Flood Risk Database", "PostgreSQL/Databricks/Databricks", "Stores flood risk data:\nFEMA zones, NOAA projections,\nUSGS streamflow, NASA models")
ContainerDb(blob_storage, "Blob Storage", "S3/Azure Blob/GCS", "Stores spatial data files\nand flood model outputs")

Rel(m_a_analyst, web_app, "Uses", "HTTPS")
Rel(m_a_manager, web_app, "Uses", "HTTPS")
Rel(web_app, api_service, "Makes API calls", "HTTPS/REST")
Rel(api_service, spatial_engine, "Uses for spatial analysis", "Python API")
Rel(api_service, risk_calculator, "Uses for risk scoring", "Python API")
Rel(api_service, database, "Reads and writes", "SQL")
Rel(spatial_engine, database, "Queries spatial data", "PostGIS/SQL")
Rel(risk_calculator, database, "Reads risk data", "SQL")
Rel(api_service, blob_storage, "Stores/retrieves files", "S3 API")
Rel(api_service, fema_api, "Retrieves flood zones", "REST API")
Rel(api_service, noaa_api, "Retrieves sea level data", "REST API")
Rel(api_service, usgs_api, "Retrieves streamflow", "REST API")
Rel(api_service, nasa_api, "Retrieves flood models", "REST API")

@enduml
```

**M&A Use Cases:**
- Web application for M&A teams to input property locations and view risk assessments
- API service for programmatic risk queries during due diligence
- Spatial engine for identifying flood zones intersecting acquisition targets
- Risk calculator for multi-factor risk scoring to inform acquisition pricing

---

## Level 3: Component Diagram - API Service

```plantuml
@startuml db16_component_api
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

LAYOUT_WITH_LEGEND()

title Component Diagram - API Service (db-16)

Container(api_service, "API Service", "Python/FastAPI")

Component(property_api, "Property API", "FastAPI Router", "Handles property location\nqueries and CRUD operations")
Component(risk_assessment_api, "Risk Assessment API", "FastAPI Router", "Generates comprehensive\nflood risk assessments")
Component(portfolio_api, "Portfolio API", "FastAPI Router", "Aggregates portfolio-level\nrisk metrics for M&A")
Component(spatial_service, "Spatial Service", "Python Service", "Performs spatial joins\nand geographic queries")
Component(risk_scoring_service, "Risk Scoring Service", "Python Service", "Calculates multi-factor\nrisk scores")
Component(financial_impact_service, "Financial Impact Service", "Python Service", "Estimates flood damage costs\nand insurance premiums")
Component(data_ingestion_service, "Data Ingestion Service", "Python Service", "Ingests data from FEMA,\nNOAA, USGS, NASA APIs")
Component(query_executor, "Query Executor", "SQLAlchemy", "Executes complex SQL queries\nfor risk assessments")

ContainerDb(database, "Flood Risk Database", "PostgreSQL/Databricks/Databricks")
System_Ext(fema_api, "FEMA API")
System_Ext(noaa_api, "NOAA API")
System_Ext(usgs_api, "USGS API")
System_Ext(nasa_api, "NASA API")

Rel(property_api, spatial_service, "Uses")
Rel(property_api, query_executor, "Uses")
Rel(risk_assessment_api, spatial_service, "Uses")
Rel(risk_assessment_api, risk_scoring_service, "Uses")
Rel(risk_assessment_api, financial_impact_service, "Uses")
Rel(risk_assessment_api, query_executor, "Uses")
Rel(portfolio_api, risk_scoring_service, "Uses")
Rel(portfolio_api, query_executor, "Uses")
Rel(spatial_service, query_executor, "Uses")
Rel(risk_scoring_service, query_executor, "Uses")
Rel(financial_impact_service, query_executor, "Uses")
Rel(query_executor, database, "Reads and writes", "SQL")
Rel(data_ingestion_service, fema_api, "Retrieves data", "REST API")
Rel(data_ingestion_service, noaa_api, "Retrieves data", "REST API")
Rel(data_ingestion_service, usgs_api, "Retrieves data", "REST API")
Rel(data_ingestion_service, nasa_api, "Retrieves data", "REST API")
Rel(data_ingestion_service, query_executor, "Writes data", "SQL")

@enduml
```

**M&A Use Cases:**
- Property API: Input acquisition target property locations
- Risk Assessment API: Generate comprehensive flood risk reports for due diligence
- Portfolio API: Aggregate risk metrics for entire acquisition target portfolios
- Financial Impact Service: Estimate costs to inform acquisition pricing

---

## Level 3: Component Diagram - Database Schema

```plantuml
@startuml db16_component_database
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

LAYOUT_WITH_LEGEND()

title Component Diagram - Database Schema (db-16)

ContainerDb(database, "Flood Risk Database", "PostgreSQL/Databricks/Databricks")

ComponentDb(fema_zones_table, "FEMA Flood Zones", "Table", "FEMA National Flood Hazard Layer\nflood zone boundaries and BFEs")
ComponentDb(properties_table, "Real Estate Properties", "Table", "Property locations and characteristics\nfor acquisition targets")
ComponentDb(sea_level_table, "NOAA Sea Level Rise", "Table", "Sea level rise projections\nand high tide flooding")
ComponentDb(streamflow_gauges_table, "USGS Streamflow Gauges", "Table", "Streamflow gauge locations\nand flood stage info")
ComponentDb(streamflow_obs_table, "USGS Streamflow Observations", "Table", "Real-time and historical\nstreamflow measurements")
ComponentDb(flood_models_table, "NASA Flood Models", "Table", "Flood model predictions\nand inundation extents")
ComponentDb(risk_assessments_table, "Flood Risk Assessments", "Table", "Comprehensive risk assessments\nfor M&A due diligence")
ComponentDb(portfolio_risk_table, "Portfolio Risk Summaries", "Table", "Aggregated risk metrics\nby portfolio")
ComponentDb(intersections_table, "Property-Flood Zone Intersections", "Table", "Spatial relationships between\nproperties and flood zones")
ComponentDb(historical_events_table, "Historical Flood Events", "Table", "Historical flood event records\nfor risk analysis")

Rel(properties_table, intersections_table, "Spatial join")
Rel(fema_zones_table, intersections_table, "Spatial join")
Rel(properties_table, risk_assessments_table, "Generates")
Rel(sea_level_table, risk_assessments_table, "Used in")
Rel(streamflow_obs_table, risk_assessments_table, "Used in")
Rel(flood_models_table, risk_assessments_table, "Used in")
Rel(risk_assessments_table, portfolio_risk_table, "Aggregates to")
Rel(historical_events_table, risk_assessments_table, "Used in")

@enduml
```

**M&A Use Cases:**
- Properties table stores acquisition target locations
- Risk assessments table stores due diligence reports
- Portfolio risk summaries aggregate deal-level metrics
- Spatial intersections identify flood zone exposure

---

## Level 4: Code Diagram - Risk Scoring Service

```plantuml
@startuml db16_code_risk_scoring
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

LAYOUT_WITH_LEGEND()

title Code Diagram - Risk Scoring Service (db-16)

Component(risk_scoring_service, "Risk Scoring Service", "Python Service")

Component(fema_scorer, "FEMA Risk Scorer", "Python Class", "Calculates FEMA flood zone\nrisk scores (0-100)")
Component(sea_level_scorer, "Sea Level Rise Scorer", "Python Class", "Calculates sea level rise\nrisk projections")
Component(streamflow_scorer, "Streamflow Scorer", "Python Class", "Calculates streamflow-based\nflood risk")
Component(nasa_model_scorer, "NASA Model Scorer", "Python Class", "Calculates NASA flood model\nrisk scores")
Component(multi_factor_aggregator, "Multi-Factor Aggregator", "Python Class", "Combines multiple risk factors\ninto composite score")
Component(temporal_projector, "Temporal Projector", "Python Class", "Projects risk across time\nhorizons (5, 20, 50, 100 years)")
Component(financial_calculator, "Financial Calculator", "Python Class", "Estimates flood damage costs\nand insurance premiums")

Rel(risk_scoring_service, fema_scorer, "Uses")
Rel(risk_scoring_service, sea_level_scorer, "Uses")
Rel(risk_scoring_service, streamflow_scorer, "Uses")
Rel(risk_scoring_service, nasa_model_scorer, "Uses")
Rel(risk_scoring_service, multi_factor_aggregator, "Uses")
Rel(risk_scoring_service, temporal_projector, "Uses")
Rel(risk_scoring_service, financial_calculator, "Uses")
Rel(multi_factor_aggregator, fema_scorer, "Aggregates")
Rel(multi_factor_aggregator, sea_level_scorer, "Aggregates")
Rel(multi_factor_aggregator, streamflow_scorer, "Aggregates")
Rel(multi_factor_aggregator, nasa_model_scorer, "Aggregates")
Rel(temporal_projector, sea_level_scorer, "Uses projections")
Rel(financial_calculator, multi_factor_aggregator, "Uses risk scores")

@enduml
```

**M&A Use Cases:**
- FEMA scorer evaluates current flood zone risk
- Sea level rise scorer projects long-term coastal risk
- Multi-factor aggregator combines all risk sources
- Financial calculator estimates acquisition pricing impact

---

## M&A Use Case Flows

### Use Case 1: Pre-Acquisition Risk Assessment

```plantuml
@startuml db16_usecase_preacquisition
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Dynamic.puml

title M&A Use Case: Pre-Acquisition Risk Assessment

Person(m_a_analyst, "M&A Analyst")
Container(web_app, "Web Application")
Container(api_service, "API Service")
ContainerDb(database, "Flood Risk Database")

Rel(m_a_analyst, web_app, "1. Inputs property location")
Rel(web_app, api_service, "2. Requests risk assessment")
Rel(api_service, database, "3. Queries flood zones, sea level, streamflow, NASA models")
Rel(database, api_service, "4. Returns risk data")
Rel(api_service, web_app, "5. Returns comprehensive risk report")
Rel(web_app, m_a_analyst, "6. Displays risk score, projections, financial impact")

@enduml
```

### Use Case 2: Portfolio-Level Risk Analysis

```plantuml
@startuml db16_usecase_portfolio
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Dynamic.puml

title M&A Use Case: Portfolio-Level Risk Analysis

Person(m_a_manager, "M&A Manager")
Container(web_app, "Web Application")
Container(api_service, "API Service")
ContainerDb(database, "Flood Risk Database")

Rel(m_a_manager, web_app, "1. Selects acquisition target portfolio")
Rel(web_app, api_service, "2. Requests portfolio risk summary")
Rel(api_service, database, "3. Aggregates risk metrics across all properties")
Rel(database, api_service, "4. Returns portfolio risk summary")
Rel(api_service, web_app, "5. Returns aggregated metrics")
Rel(web_app, m_a_manager, "6. Displays portfolio risk score, geographic clustering, deal risk assessment")

@enduml
```

### Use Case 3: Comparative Risk Analysis

```plantuml
@startuml db16_usecase_comparative
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Dynamic.puml

title M&A Use Case: Comparative Risk Analysis

Person(m_a_manager, "M&A Manager")
Container(web_app, "Web Application")
Container(api_service, "API Service")
ContainerDb(database, "Flood Risk Database")

Rel(m_a_manager, web_app, "1. Selects multiple acquisition targets")
Rel(web_app, api_service, "2. Requests comparative risk analysis")
Rel(api_service, database, "3. Retrieves risk assessments for all targets")
Rel(database, api_service, "4. Returns risk data for all targets")
Rel(api_service, web_app, "5. Returns side-by-side comparison")
Rel(web_app, m_a_manager, "6. Displays ranked targets by risk, identifies lowest-risk opportunities")

@enduml
```

---

## Summary

The C4 model for db-16 demonstrates:

1. **System Context**: M&A users interacting with flood risk assessment system and external data sources
2. **Container**: Web app, API service, spatial engine, risk calculator, and databases
3. **Component**: Detailed API services, database schema, and risk scoring components
4. **Code**: Risk scoring service implementation details

All diagrams focus on M&A use cases:
- Pre-acquisition due diligence
- Portfolio-level risk analysis
- Comparative risk analysis
- Financial impact assessment

---
**Last Updated:** 2026-02-06  
**Version:** 1.0
