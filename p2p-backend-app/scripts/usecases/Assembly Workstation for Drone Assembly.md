# **Use Case Submission \-Assembly Workstation**

---

## **1\. Basic Information Section**

**Title**  
 Assembly Workstation

**Subtitle**  
 Step-by-step digital work instructions with tool interlocks reduce errors and cycle time on the assembly line

**Description/Executive Summary**  
 This use case implements a guided assembly workstation that provides operators with step-by-step digital work instructions, integrated tool verification (e.g., smart torque wrenches), barcode/RFID checks for parts, and pick-to-light guidance. The system enforces process order, validates each critical step (poka-yoke), and logs traceability to MES. By standardizing assembly and preventing mistakes in real time, the workstation accelerates training, improves first-pass yield, and reduces rework and downtime.

**Category**  
 Process Optimization

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
 Drone assembly involves numerous precise steps, torque specs, variant BOMs, and quality checkpoints. Paper instructions and manual sign-offs lead to variability, longer training time, and higher rework risk—especially during product updates and shift handovers.

**Specific Problems**

* Inconsistent assembly quality due to manual instructions and human error

* Long operator training/onboarding time for complex builds

* Limited traceability of who did what step, with which part/tool, and when

**Financial Loss/Impact**  
 Estimated SAR 650,000 annually from rework, scrap, delayed orders, and extended changeover/training time.

---

## **4\. Solution Overview**

**Selection Criteria**

* Step-by-step digital work instructions with version control and e-signoff

* Tool interlocks/verification (smart torque, barcode/RFID checks, pick-to-light)

* Seamless MES/ERP integration for traceability and production reporting

**Selected Vendor**  
 IIoT Solutions

**Technology Components**

* Touchscreen workstation (industrial PC), barcode/RFID readers, pick-to-light modules

* Smart torque tools with programmatic torque/angle verification

* Edge gateway with rule engine; MES integration and electronic traveler

* Digital Work Instruction (DWI) software with media (images/video/3D) and e-signoff

---

## **5\. Project Teams**

**Internal Team Members**

* **Role**: Project Lead, **Name**: Aadil Feroze, **Title**: CTO  
* **Role**: Simulation Architect, **Name**: Amro Abouzied, **Title**: Solutions Architect  
* **Role**: Simulation Engineer, **Name**: Abdurrahman Bajabir, **Title**: Production Engineer

---

## **6\. Implementation Details**

**Implementation Time**  
 3 months

**Total Budget**  
 SAR 320,000

**Methodology**  
 Agile rollout across a pilot cell followed by phased expansion. Each sprint delivered validated instructions, tool integrations, operator feedback, and MES traceability checks.

**Implementation Phases**

* **Phase Name**: Process Mapping & Content Authoring

  * Duration: 3 weeks

  * Objectives: Map assembly steps, capture torque specs, author digital work instructions

  * Key Activities: SOP review, media capture, e-sign workflow setup

  * Budget: SAR 70,000

* **Phase Name**: Pilot Cell Deployment

  * Duration: 5 weeks

  * Objectives: Integrate tools and validation in one assembly cell

  * Key Activities: Pick-to-light setup, torque interlocks, barcode/RFID checks, operator training

  * Budget: SAR 120,000

* **Phase Name**: Line-Wide Rollout & Optimization

  * Duration: 4 weeks

  * Objectives: Scale to all stations; refine UI and takt alignment

  * Key Activities: Station replication, MES reports, KPI tuning (FPY, CT)

  * Budget: SAR 130,000

---

## **7\. Results & Impact**

**Quantitative Results**

* First-Pass Yield (FPY): 93% → 99% (6-pt improvement)

* Defects per Unit (DPU): 0.45 → 0.12 (73% reduction)

* Average Assembly Cycle Time: 18 min → 14.5 min (19% faster)

**Qualitative Impacts**  
 Standardized build quality across shifts, faster onboarding for new operators, improved confidence during engineering changes.

**ROI Metrics**

* ROI Percentage: 200% 3-year ROI

* Annual Savings: SAR 320,000

* Total Investment: SAR 320,000

* Three-Year ROI: SAR 960,000

---

## **8\. Challenges & Solutions**

**Challenge Name**: Instruction Version Control

* **Description**: Operators sometimes followed outdated paper SOPs during early transition.

* **Solution**: Enforced “single source of truth” with digital release workflow and QR access per station.

* **Outcome**: 100% adherence to latest instructions; paper eliminated.

**Challenge Name**: Tool Communication Reliability

* **Description**: Intermittent connectivity between smart torque tools and the workstation.

* **Solution**: Hardened industrial Wi-Fi, local edge cache, and automatic retry logic.

* **Outcome**: Verified torque data capture \>99.5% reliability.

---

## **9\. Technical Architecture**

**System Overview**  
 A DWI (Digital Work Instruction) platform running on industrial workstations with connected tools and sensors. The edge rule engine enforces step order and collects traceability, while MES integration logs production history and e-signoffs.

**Architecture Components**

* **Layer Name**: Data Layer

  * **Components**: Barcode/RFID readers, pick-to-light, smart torque tools, I/O modules

  * **Specifications**: Real-time I/O; torque/angle capture with millisecond timestamps

* **Layer Name**: Application Layer

  * **Components**: DWI engine, edge rule engine, MES/ERP connector

  * **Specifications**: Step gating, electronic traveler, API/webhook integrations

* **Layer Name**: Presentation Layer

  * **Components**: Operator UI (touchscreen), supervisor dashboards, e-sign portal

  * **Specifications**: Media-rich steps (images/video/3D), role-based views

**Security Measures**  
 Role-based access (operators/supervisors/engineers), encrypted data in transit and at rest, signed e-records for audits.

**Scalability Design**  
 Template-based instruction library for new variants, add-station replication, multi-line support, and centralized content governance.

---

## **10\. Future Roadmap**

* **Timeline**: Q4 2026  
   **Initiative**: AR Overlay for Critical Steps  
   **Description**: Add optional AR guidance for complex sub-assemblies and torque locations.  
   **Expected Benefit**: Additional 10% error reduction on high-risk steps.

* **Timeline**: Q2 2027  
   **Initiative**: AI-Assisted Instruction Optimization  
   **Description**: Analyze station history to recommend step reordering and media improvements.  
   **Expected Benefit**: 5–8% cycle-time reduction and faster onboarding.

---

## **11\. Lessons Learned**

**Category**: Process  
 **Lesson Title**: Pictures beat paragraphs  
 **Description**: Photo/diagram-heavy steps outperformed text-only instructions in speed and accuracy.  
 **Recommendation**: Prioritize visual content and short captions; reserve long text for reference links.

---

## **12\. Contact Information & Media**

**Contact Person**  
 Abdurrahman Bajabir

**Contact Title**  
 Production Engineer

**Images**

* Guided assembly workstation UI (step navigator)

* Pick-to-light bins and barcode scanning in use

* Smart torque tool verification screen (pass/fail)

* MES traceability report showing e-signoffs

---

## **13\. Tags & Classification**

**Industry Tags**  
 Drone Manufacturing, Electronics Assembly, Advanced Manufacturing

**Technology Tags**  
 Digital Work Instructions, Poka-Yoke, Pick-to-Light, MES Integration, Traceability

