# **Use Case Demanufacturing Workstation**

---

## **1\. Basic Information Section**

**Title**  
 Demanufacturing Workstation

**Subtitle**  
 Guided teardown and diagnostics recover usable parts, reduce waste, and speed repairs

**Description/Executive Summary**  
 This use case introduces a demanufacturing workstation that supports structured drone disassembly, fault isolation, and parts grading. Operators follow step-by-step digital instructions on an ESD-safe bench while vision checks, barcode/RFID capture, and functional test fixtures identify failed components. Usable parts are graded (A/B/C), labeled, and returned to stock; failed items are quarantined with root-cause evidence. The approach cuts scrap, lowers spare-parts spend, and accelerates repair turnaround.

**Category**  
 Sustainability

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
 Repair, returns, and non-conforming builds create a steady flow of units needing teardown and triage. Without standardized disassembly and diagnostics, shops over-scrap assemblies, buy unnecessary spares, and extend turnaround time—hurting availability and margins.

**Specific Problems**

* Unstructured teardown causing damaged recoverable parts

* Limited traceability of what failed, why, and which lots were affected

* High spare-parts procurement spend due to low reuse rate

* Long mean time to diagnose (MTTD) and repair due to manual checks

**Financial Loss/Impact**  
 Estimated SAR 900,000 annually from excess scrap, avoidable spare-parts purchases, and extended repair cycles

---

## **4\. Solution Overview**

**Selection Criteria**

* Step-by-step digital teardown instructions with poka-yoke and e-signoff

* Integrated electrical/functional test fixtures for key modules (FCU, ESC, motors, battery, sensors)

* Parts identification via barcode/RFID \+ vision to prevent mix-ups

* Automatic grading (A/B/C), labeling, and return-to-stock workflow tied to ERP/MES

**Selected Vendor**  
 IIoT Solutions

**Technology Components**

* ESD-safe benches with grounded mats, wrist straps, and ionizers

* Smart torque drivers with data capture for fastener removal/installation

* Vision camera for part presence/ID and cosmetic checks

* Barcode/RFID scanners for serial/lot capture; calibrated scales for weight checks

* Modular test rigs (power, communication, sensor, motor/ESC) with automated pass/fail

* Edge gateway with rules engine; MES/ERP connectors; label printer for graded parts

---

## **5\. Project Teams**

**Internal Team Members**

* Role: Project Lead | Name: Aadil Feroze | Title: CTO

* Role: Simulation Architect | Name: Amro Abouzied | Title: Solutions Architect

* Role: Simulation Engineer | Name: Abdurrahman Bajabir | Title: Production Engineer

---

## **6\. Implementation Details**

**Implementation Time**  
 4 months

**Total Budget**  
 SAR 420,000

**Methodology**  
 Iterative deployment: define teardown flows, stand up fixtures, validate tests on golden/failed samples, then roll out line-wide with operator training and closed-loop reporting.

**Implementation Phases**

* **Phase Name**: Process Design & Fixture Specification

  * Duration: 4 weeks

  * Objectives: Map teardown flows; specify electrical and mechanical tests

  * Key Activities: SOP authoring, fixture design, sample library creation

  * Budget: SAR 90,000

* **Phase Name**: Pilot Bench & Test Development

  * Duration: 6 weeks

  * Objectives: Build one bench; develop/validate test scripts and grading rules

  * Key Activities: Fixture build, vision & barcode setup, MES integration, operator trials

  * Budget: SAR 150,000

* **Phase Name**: Scale-Up & Training

  * Duration: 6 weeks

  * Objectives: Add benches; standardize grading/labeling; train operators & QA

  * Key Activities: Multi-bench install, label templates, dashboards, kaizen cycles

  * Budget: SAR 180,000

---

## **7\. Results & Impact**

**Quantitative Results**

* Parts Recovery Yield: 45% → 80% (35-pt increase)

* Mean Time to Diagnose (MTTD): 120 min → 45 min (62% faster)

* Spare-Parts Procurement Cost: −35% year-over-year

* Scrap Weight: −40% for teardown population

**Qualitative Impacts**  
 Higher confidence in repair decisions, better supplier feedback via defect evidence, and improved sustainability through reuse.

**ROI Metrics**

* ROI Percentage: 210% 3-year ROI

* Annual Savings: SAR 420,000

* Total Investment: SAR 420,000

* Three-Year ROI: SAR 1,260,000

---

## **8\. Challenges & Solutions**

**Challenge Name**: Damage During Teardown

* **Description**: Early teardowns occasionally damaged connectors and flex cables.

* **Solution**: Added tool-specific steps, torque/sequence guidance, and connector fixtures.

* **Outcome**: Secondary damage incidents reduced by 85%.

**Challenge Name**: Inconsistent Grading Criteria

* **Description**: Different shifts graded parts differently.

* **Solution**: Standardized A/B/C rubric with photos, auto-linked to test results.

* **Outcome**: Inter-shift grading variance cut to \<5%.

---

## **9\. Technical Architecture**

**System Overview**  
 An ESD-compliant workstation ecosystem combining guided instructions, automated tests, vision/ID capture, and grading workflows. The edge rule engine enforces steps and compiles a digital teardown record synced to MES/ERP.

**Architecture Components**

* **Layer Name**: Data Layer

  * **Components**: Vision camera, barcode/RFID, smart torque, electrical testers, scales

  * **Specifications**: Millisecond timestamps; test data streamed over MQTT/OPC-UA

* **Layer Name**: Application Layer

  * **Components**: Teardown DWI, rules engine, test sequencer, MES/ERP connector

  * **Specifications**: Step gating, automatic pass/fail, grading & labeling, RMA linkage

* **Layer Name**: Presentation Layer

  * **Components**: Operator UI, QA dashboard, salvage/return-to-stock reports

  * **Specifications**: Photo evidence storage, serial/lot traceability, analytics

**Security Measures**  
 Role-based access, encrypted data in transit/at rest, tamper-evident audit logs with image and test attachments.

**Scalability Design**  
 Additional benches via template cloning; modular fixtures for new SKUs; cloud archival for long-term defect analytics.

---

## **10\. Future Roadmap**

* **Timeline**: Q1 2027 — **Automated Defect Classification**  
   **Description**: Train ML models on teardown images \+ test traces to auto-suggest root causes.  
   **Expected Benefit**: 20% additional reduction in MTTD and faster triage.

* **Timeline**: Q3 2027 — **Closed-Loop CMMS Integration**  
   **Description**: Push failure modes to maintenance for design/process feedback and preventive actions.  
   **Expected Benefit**: Fewer repeats of systemic failures; higher first-time repair rate.

---

## **11\. Lessons Learned**

**Category**: Process  
 **Lesson Title**: Clear grading drives reuse  
 **Description**: Formal A/B/C criteria tied to objective tests removed debate and sped return-to-stock.  
 **Recommendation**: Publish visual rubrics and auto-link grading to test thresholds.

---

## **12\. Contact Information & Media**

**Contact Person**  
 Abdurrahman Bajabir

**Contact Title**  
 Production Engineer

**Images**

* ESD demanufacturing bench with fixtures and vision camera

* Diagnostic tester UI with pass/fail trace

* Graded parts with labels (A/B/C) ready for return-to-stock

* Scrap vs. reuse trend chart from the teardown dashboard

---

## **13\. Tags & Classification**

**Industry Tags**  
 Drone Manufacturing, Circular Economy, Electronics Assembly

**Technology Tags**  
 ESD Workbench, Functional Testing, Computer Vision, Traceability, Reverse Logistics

