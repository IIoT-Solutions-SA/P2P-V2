# **Use Case Submission – Legacy System Integration**

---

## **1\. Basic Information Section**

**Title**  
 Legacy System Integration

**Subtitle**  
 Connecting legacy and 3D printing machines to enable real-time data streaming and monitoring

**Description/Executive Summary**  
 This use case focuses on integrating legacy machines and 3D printers into the Smart Factory’s digital infrastructure. By connecting older systems to the network and streaming their data to an MQTT broker, the factory achieved real-time monitoring, improved visibility, and the ability to include non-digital assets in predictive analytics. This integration modernized outdated equipment without costly replacements.

**Category**  
 Factory Automation

**Factory Name**  
 KACST Smart Factory

---

## **2\. Location Information**

**City**  
 Riyadh

**Geographic Coordinates**  
 Latitude: 24.559903 | Longitude: 46.869228

---

## **3\. Business Challenge**

**Industry Context**  
 Many manufacturing facilities operate a mix of modern and legacy equipment. While newer machines often provide native connectivity, legacy systems typically run in isolation, limiting visibility, integration with ERP/MES, and predictive analytics capabilities. This creates a barrier to achieving a fully connected and efficient production environment.

**Specific Problems**

1. Legacy machines produced no real-time data for monitoring

2. 3D printers lacked integration with the factory’s MES and ERP systems

3. Manual logging from operators was time-consuming and error-prone

**Financial Loss/Impact**  
 Estimated SAR 750,000 annual inefficiencies from downtime, unplanned stoppages, and missed optimization opportunities

---

## **4\. Solution Overview**

**Selection Criteria**

1. Non-intrusive connectivity method for older equipment

2. Standard protocol support (MQTT) for easy integration

3. Scalable solution covering both legacy machines and 3D printers

**Selected Vendor**  
 IIoT Solutions (with KACST)

**Technology Components**

* Retrofit IoT sensor kits and gateways for legacy machines

* MQTT broker for real-time data streaming

* Middleware APIs for integrating with MES/ERP dashboards

  ---

  ## **5\. Project Teams**

**Internal Team Members**

* **Role**: Project Lead, **Name**: Aadil Feroze, **Title**: CTO  
* **Role**: Simulation Architect, **Name**: Amro Abouzied, **Title**: Solutions Architect  
* **Role**: Simulation Engineer, **Name**: Abdurrahman Bajabir, **Title**: Production Engineer

  ---

  ## **6\. Implementation Details**

**Implementation Time**  
 5 months

**Total Budget**  
 SAR 487,500

**Methodology**  
 Stepwise integration with initial pilots, network testing, and staged rollout across multiple legacy machines and 3D printers

**Implementation Phases**

* **Phase Name**: Assessment & Design

  * Duration: 4 weeks

  * Objectives: Identify connectivity gaps, design retrofit solutions

  * Key Activities: Equipment survey, interface design, integration planning

  * Budget: SAR 75,000

* **Phase Name**: Pilot Integration

  * Duration: 6 weeks

  * Objectives: Connect one CNC and one 3D printer to MQTT broker

  * Key Activities: Sensor installation, gateway configuration, streaming validation

  * Budget: SAR 110,000

* **Phase Name**: Full Rollout

  * Duration: 10 weeks

  * Objectives: Connect all targeted legacy and 3D printing machines

  * Key Activities: Retrofit deployment, MES/ERP integration, operator training

  * Budget: SAR 302,500

    ---

    ## **7\. Results & Impact**

**Quantitative Results**

* Machine Connectivity: Baseline 65% (only modern machines connected) → Current 100% (legacy \+ 3D printers included)

* Data Availability: Baseline 0% real-time visibility for legacy systems → Current 95% continuous streaming

* Downtime Detection Speed: Baseline average 2 hrs → Current \<15 min (87% faster detection)

**Qualitative Impacts**  
 Improved confidence in older machines, reduced manual logging, extended asset life by digitally enabling legacy equipment

**ROI Metrics**

* ROI Percentage: 170% 3-year ROI

* Annual Savings: SAR 487,500

* Total Investment: SAR 487,500

* Three-Year ROI: SAR 1,312,500

  ---

  ## **8\. Challenges & Solutions**

**Challenge Name**: Hardware Compatibility

* Description: Older machines lacked standard ports and interfaces for IoT gateways

* Solution: Custom retrofit kits and modular sensor attachments were developed

* Outcome: Achieved seamless data acquisition from 90% of targeted legacy assets

**Challenge Name**: Network Integration

* Description: Initial attempts to stream large data sets caused latency in the factory network

* Solution: Optimized MQTT topics and applied edge preprocessing before data transmission

* Outcome: Stable real-time data flow with no noticeable network slowdown

  ---

  ## **9\. Technical Architecture**

**System Overview**  
 A retrofit IoT solution enabling non-digital machines to communicate with modern digital infrastructure using MQTT for real-time data streaming and integration with MES/ERP.

**Architecture Components**

* Data Layer: Retrofit IoT sensors, gateways, MQTT broker

* Application Layer: Middleware APIs, integration with MES/ERP, data preprocessing engine

* Presentation Layer: Real-time dashboards, MES/ERP analytics modules

**Security Measures**

* End-to-end encryption for MQTT data streams

* Secure gateway authentication and role-based access

* Routine vulnerability assessments and firmware updates

**Scalability Design**

* Modular gateway design to support additional legacy machines

* Auto-scaling cloud infrastructure for growing data volume

* Load balancing to manage high data throughput

  ---

  ## **10\. Future Roadmap**

* **Timeline**: Q3 2026

* **Initiative**: Predictive Analytics Integration

* **Description**: Use real-time data from retrofitted legacy machines to train predictive models for maintenance forecasting

* **Expected Benefit**: Reduce unplanned downtime by an additional 15% and improve asset utilization

  ---

  ## **11\. Lessons Learned**

**Category**: Technical  
 **Lesson Title**: Retrofitting requires tailored solutions  
 **Description**: A one-size-fits-all approach failed during early pilots, as machines varied in interfaces and compatibility.  
 **Recommendation**: Plan for modular retrofit kits and allow flexibility in gateway configurations.

---

## **12\. Contact Information & Media**

**Contact Person**  
 Abdulrahman Bajabir

**Contact Title**  
 Smart Factory Project Engineer

**Images**

* Retrofit sensor kit installed on legacy machine

* MQTT data stream dashboard

* Side-by-side comparison of connected vs non-connected machines

  ---

  ## **13\. Tags & Classification**

**Industry Tags**  
 Electronics Manufacturing

**Technology Tags**  
 IoT Sensors, MQTT, Retrofit Integration, Factory Automation

* 

