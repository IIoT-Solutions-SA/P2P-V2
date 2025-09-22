# **Use Case Submission – Vision-Assisted Packing Workstation**

---

## **1\. Basic Information Section**

**Title**  
 Vision-Assisted Packing Workstation

**Subtitle**  
 Camera-verified kitting with barcode and weight checks prevents packing errors and improves throughput

**Description/Executive Summary**  
 This use case implements a vision-assisted packing workstation that verifies every drone kit before sealing. An overhead camera with AI vision checks contents and orientation, barcode/RFID scanners validate item and variant, and an integrated weight scale confirms final kit mass. Pick-to-light guides the operator, while the workstation prints labels and logs traceability to MES/ERP. The solution eliminates missing/extra parts, reduces returns, and speeds up the packing process.

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
 Packing errors (missing accessories, wrong variant, duplicates) drive costly returns, rework, and customer dissatisfaction. Manual checklists are inconsistent under high takt and frequent SKU changes, especially when accessory bundles differ by customer/order.

**Specific Problems**

* Missing or extra components due to manual verification

* Wrong variant/label mix-ups across SKUs and customers

* No automated, final “go/no-go” validation before sealing

**Financial Loss/Impact**  
 Estimated SAR 520,000 annually from returns, rework, expedited reshipments, and customer penalties

---

## **4\. Solution Overview**

**Selection Criteria**

* Real-time camera verification against BOM/kit template

* Dual validation via barcode/RFID and final weight check

* Seamless MES/ERP/WMS integration with label and packing-slip printing

**Selected Vendor**  
 IIoT Solutions

**Technology Components**

* Overhead industrial camera with AI vision model for presence/orientation checks

* Barcode/RFID scanners for item/variant confirmation

* Calibrated bench weight scale for final mass verification

* Pick-to-light modules and operator HMI with step-by-step guidance

* Edge gateway with rules engine; ERP/MES/WMS connectors; label printer

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
 SAR 310,000

**Methodology**  
 Agile deployment with a pilot station, iterative model tuning, and phased rollout to all packing bays; weekly kaizen on UI/UX and lighting.

**Implementation Phases**

* **Phase Name**: Design & Data Collection

  * Duration: 3 weeks

  * Objectives: Define kit templates/BOMs; capture images of all SKUs and accessories

  * Key Activities: Golden-sample creation, lighting design, HMI workflows

  * Budget: SAR 70,000

* **Phase Name**: Pilot Station Deployment

  * Duration: 5 weeks

  * Objectives: Validate camera checks, barcode/weight interlocks, and labeling

  * Key Activities: Model training, threshold tuning, operator training, traceability tests

  * Budget: SAR 120,000

* **Phase Name**: Multi-Station Rollout

  * Duration: 4 weeks

  * Objectives: Replicate to all packing bays; integrate with ERP/WMS and shipping

  * Key Activities: Hardware install, label templates, KPI dashboards, SOP finalization

  * Budget: SAR 120,000

---

## **7\. Results & Impact**

**Quantitative Results**

* Packing Accuracy: 93% → 99.7% (96% reduction in errors)

* Returns Due to Packing Errors: 40 → 6 per month (85% reduction)

* Pack Cycle Time: 6.5 min → 5.0 min per kit (23% faster)

**Qualitative Impacts**  
 Higher customer satisfaction, consistent quality across shifts/SKUs, and improved operator confidence with guided steps.

**ROI Metrics**

* ROI Percentage: 185% 3-year ROI

* Annual Savings: SAR 310,000

* Total Investment: SAR 310,000

* Three-Year ROI: SAR 930,000

---

## **8\. Challenges & Solutions**

**Challenge Name**: Lighting Variability Affecting Vision Accuracy

* **Description**: Changing ambient light caused false fails/passes on reflective parts.

* **Solution**: Installed controlled diffused lighting and glare shields; retrained model with augmented images.

* **Outcome**: \>98% vision detection accuracy across SKUs.

**Challenge Name**: Operator Flow Disruption

* **Description**: Early UI required extra clicks and slowed packing.

* **Solution**: Introduced hands-free triggers (foot pedal/auto-scan), simplified screens, and pick-to-light sequences.

* **Outcome**: Pack time cut by 23% with 100% operator adoption in 4 weeks.

---

## **9\. Technical Architecture**

**System Overview**  
 A camera-enabled packing cell with edge inference and rule validation (vision \+ barcode/RFID \+ weight) that gates label printing and box sealing; events and images are logged to MES/ERP for full traceability.

**Architecture Components**

* **Layer Name**: Data Layer

  * **Components**: Industrial camera, barcode/RFID scanners, bench scale, pick-to-light

  * **Specifications**: Millisecond timestamping; scale resolution ≤1 g; camera ≥5 MP with controlled lighting

* **Layer Name**: Application Layer

  * **Components**: Vision inference service, rules engine, ERP/MES/WMS connectors, label service

  * **Specifications**: Real-time go/no-go, SKU template matching, image archival with lot/serial

* **Layer Name**: Presentation Layer

  * **Components**: Operator HMI, supervisor dashboard, audit/traceability reports

  * **Specifications**: Step-by-step UI, exception handling, photo proof on pass/fail

**Security Measures**  
 Encrypted device-to-edge-to-cloud traffic, role-based access, tamper-evident audit logs with image evidence.

**Scalability Design**  
 Template library for new SKUs, horizontal scaling of vision inference, multi-bay replication, model versioning with rollback.

---

## **10\. Future Roadmap**

* **Timeline**: Q1 2026 — **Automated Carton Suggestion**  
   **Description**: Add 3D bin-packing to propose optimal box and dunnage.  
   **Expected Benefit**: 12% packaging material savings and safer shipments.

* **Timeline**: Q3 2026 — **Closed-Loop Claim Analysis**  
   **Description**: Link customer returns to station photos and signals for root-cause analytics.  
   **Expected Benefit**: Additional 30% reduction in recurring packing issues.

---

## **11\. Lessons Learned**

**Category**: Technical  
 **Lesson Title**: Golden Samples and Weight Windows Matter  
 **Description**: Precise master images and tight weight tolerances were critical to prevent false accepts for look-alike accessories.  
 **Recommendation**: Maintain golden-sample images per SKU/revision and review weight windows whenever BOMs change.

---

## **12\. Contact Information & Media**

**Contact Person**  
 Abdurrahman Bajabir

**Contact Title**  
 Production Engineer

**Images**

* Packing bay with overhead camera and controlled lighting

* HMI screen showing vision pass/fail and weight confirmation

* Pick-to-light guidance during kitting

* Label printing and sealed-box photo proof

---

## **13\. Tags & Classification**

**Industry Tags**  
 Drone Manufacturing, Electronics Assembly, Fulfillment & Logistics

**Technology Tags**  
 Computer Vision, Barcode/RFID, Weight Verification, Pick-to-Light, MES/ERP Integration

