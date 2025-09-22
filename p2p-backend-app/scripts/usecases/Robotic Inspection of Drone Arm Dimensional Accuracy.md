# **Use Case Submission: Robotic Inspection of Drone Arm Dimensional Accuracy**

## **1\. Basic Information Section**

* **Title**: Robotic Inspection Station for Drone Arm Dimensional Accuracy  
* **Subtitle**: An automated quality cell where a robotic arm picks parts from a conveyor, verifies dimensional accuracy with laser scanners, and dispatches approved parts to assembly via Autonomous Mobile Robots (AMRs).  
* **Description/Executive Summary**: The KACST Industry 4.0 Capability Center implemented a fully automated quality inspection station that serves as the critical link between manufacturing and assembly. The system's robotic arm picks a 3D-printed drone arm from an incoming conveyor belt and places it into a high-precision fixture. Laser sensors scan the component's geometry, which is compared against the source CAD file. If the part passes, the robot places it into a waiting AMR for transport to the assembly line; if it fails, it is discarded into a reject bin.  
* **Category**: Quality Control  
* **Factory Name**: KACST Industry 4.0 Capability Center

## **2\. Location Information**

* **City**: Riyadh  
* **Geographic Coordinates**:  
  * **Latitude**: 24.7136  
  * **Longitude**: 46.6753

## **3\. Business Challenge**

* **Industry Context**: For high-performance drones, the precise geometry of components is critical. Even minor warping from the 3D printing process can lead to assembly failures or stress fractures. A robust, automated, and integrated quality check is essential to guarantee the integrity of every component before it reaches the final assembly stage.  
* **Specific Problems**:  
  1. "Manual transfer of parts between manufacturing and QC created delays, bottlenecks, and risk of damage."  
  2. "Manual dimensional checks using calipers were too slow and inconsistent to keep up with the output of the automated printer farm."  
  3. "No automated way to sort passed and failed parts, leading to potential mix-ups."  
  4. "Inability to provide customers with quantitative quality assurance reports for component-level precision."  
* **Financial Loss/Impact**: "Estimated SAR 350,000 annually in scrapped materials, wasted assembly labor, and warranty claims resulting from part-fitment and performance issues."

## **4\. Solution Overview**

* **Selection Criteria**:  
  1. "The system must measure dimensional accuracy and concavity with a tolerance of ±0.05mm."  
  2. "The entire inspection cycle, including picking from a conveyor and placing into an AMR, must be under 30 seconds."  
  3. "Must integrate seamlessly with both the upstream conveyor system and the downstream AMR fleet."  
  4. "Must use a non-contact measurement method to avoid cosmetic damage to the parts."  
* **Selected Vendor**: IIoT Solutions  
* **Technology Components**:  
  1. "6-axis collaborative robotic arm for all part handling tasks."  
  2. "High-resolution 3D laser scanner for detailed surface geometry and concavity data capture."  
  3. "Conveyor tracking system with optical sensors to signal part arrival."  
  4. "AMR dispatch integration via Node-RED to call a robot and confirm part loading."  
  5. "Dual 270-degree safety laser scanners for creating a safe, fenceless collaborative workspace."  
* **Vendor Process**: IIoT Solutions conducted a proof-of-concept by first 3D scanning a "golden sample" (a perfect part) to establish a baseline CAD comparison model. They then developed the robotic handling and scanning sequence in a lab environment before integrating the full system into the production line.  
* **Vendor Selection Reasons**: IIoT Solutions' proven expertise in integrating robotics, machine vision, and IoT workflows (specifically using Node-RED) made them the ideal partner to build this complex, multi-system quality cell.

## **5\. Project Teams**

* **Internal Team Members**:  
  * **Role**: Project Lead, **Name**: Aadil Feroze, **Title**: CTO  
  * **Role**: Systems Integration Lead, **Name**: Amro Abouzied, **Title**: Solutions Architect  
  * **Role**: Automation Lead, **Name**: Abdurrahman Bajabir, **Title**: Production Engineer  
  * **Role**: Vision & Robotics Lead, **Name**: Hamza Feroze, **Title**: AI Developer

## **6\. Implementation Details**

* **Implementation Time**: "4 Months"  
* **Total Budget**: "SAR 250,000"  
* **Methodology**: A phased, systems engineering approach was used. Each core component (robot, vision, scanner) was developed and tested as a standalone module before being integrated. Node-RED served as the central messaging bus, allowing for parallel development and simplified final integration.  
* **Implementation Phases**:  
  * **Phase Name**: Hardware Procurement & Cell Layout, **Duration**: 4 weeks, **Objectives**: Procure robot and sensors, design and build the physical inspection fixture, and install and commission safety systems, **Key Activities**: Vendor negotiation, mechanical design, hardware installation, safety scanner configuration, **Budget**: "SAR 120,000"  
  * **Phase Name**: Robotics & Vision Programming, **Duration**: 5 weeks, **Objectives**: Program the robot's pick-and-place sequence, develop the vision system for part recognition, **Key Activities**: Robot path planning, vision model training, gripper calibration, **Budget**: "SAR 50,000"  
  * **Phase Name**: Scanner Integration & Data Analysis, **Duration**: 4 weeks, **Objectives**: Integrate the laser scanner, develop the algorithm for comparing scan data to the CAD model, define concavity tolerances, **Key Activities**: Driver development, 3D data processing, statistical analysis, **Budget**: "SAR 50,000"  
  * **Phase Name**: Final Integration & Commissioning, **Duration**: 3 weeks, **Objectives**: Link all systems via Node-RED, perform end-to-end testing, connect to MES for data logging, **Key Activities**: Workflow development in Node-RED, full-cycle testing, production handover, **Budget**: "SAR 30,000"

## **7\. Results & Impact**

* **Quantitative Results**:  
  * **Metric Name**: Dimensional Defect Escape Rate, **Baseline Value**: "8%", **Current Value**: "0.2%", **Improvement**: "97.5% reduction in defective parts reaching assembly"  
  * **Metric Name**: Inspection Throughput, **Baseline Value**: "10 parts/hour (manual)", **Current Value**: "120 parts/hour (automated)", **Improvement**: "1100% increase in inspection capacity"  
  * **Metric Name**: Assembly Failure Rate (due to part fit), **Baseline Value**: "4%", **Current Value**: "0%", **Improvement**: "100% elimination of fitment-related rework"  
* **Qualitative Impacts**:  
  * "Guaranteed 100% geometric compliance for every drone arm, significantly enhancing the final product's reliability and performance."  
  * "Enabled the creation of detailed Quality Certificates for each batch, providing a competitive advantage."  
  * "Vastly improved the engineering team's ability to trace defects back to specific 3D printers or material batches."  
* **ROI Metrics**:  
  * **ROI Percentage**: "40% ROI in first year"  
  * **Annual Savings**: "SAR 350,000 (from eliminating rework, scrap, and warranty claims)"  
  * **Total Investment**: "SAR 250,000"  
  * **Three-Year ROI**: "Projected 420% ROI over three years"

## **8\. Challenges & Solutions**

* **Implementation Challenges**:  
  * **Challenge Name**: Ensuring Operator Safety in a Fenceless Robotic Cell, **Description**: "Operating a robotic arm without traditional physical fencing requires a robust safety system to protect personnel who may need to approach the cell for maintenance or operational tasks.", **Solution**: "Two 270-degree safety laser scanners were installed at opposite corners of the cell. They create two safety zones: an outer 'warning' zone that slows the robot, and an inner 'stop' zone (at an arm's length) that immediately halts all robotic motion if breached by a person.", **Outcome**: "The cell is certified as a safe collaborative workspace, allowing operators to work near the robot confidently without the need for cumbersome physical barriers."  
  * **Challenge Name**: Robot-Scanner Occlusion, **Description**: "In certain positions, the robot's own gripper was blocking the laser scanner's line of sight to critical parts of the drone arm.", **Solution**: "The team programmed a two-stage scanning process. The robot first holds the part in one orientation for an initial scan, then re-grips it at a different point and re-presents it to the scanner to capture the previously occluded areas.", **Outcome**: "A complete 360-degree point cloud of the part is captured reliably on every cycle."  
  * **Challenge Name**: Production Line Handshake, **Description**: "Ensuring the upstream conveyor, the QC robot, and the downstream AMR were all perfectly synchronized was a major challenge.", **Solution**: "A centralized Node-RED workflow acts as a 'traffic controller'. An optical sensor on the conveyor sends an MQTT message when a part arrives, triggering the QC robot. Once the inspection is complete, Node-RED sends another MQTT message to call the AMR, and waits for a confirmation message before commanding the robot to place the part.", **Outcome**: "A seamless, fully autonomous, and event-driven flow from printing to assembly dispatch, with zero bottlenecks."

## **9\. Technical Architecture**

* **System Overview**: The system forms a bridge in the production line. A drone arm arrives on a conveyor belt, triggering a sensor. A 6-axis robot picks the part and places it in a scanning fixture. A 3D laser scanner captures the geometry. The Pass/Fail result is determined, and a Node-RED workflow commands the robot to either place the part in a reject bin or into a waiting AMR. The AMR is then dispatched to the manual assembly station. The entire cell is monitored by safety scanners to allow for safe, fenceless operation.  
* **Architecture Components**:  
  * **Layer Name**: Physical Automation Layer, **Components**: "6-axis Collaborative Robot, Custom Gripper, Inspection Fixture, Conveyor Belt, Dual Safety Laser Scanners", **Specifications**: "The cell is monitored by 270-degree safety scanners that trigger an immediate stop if an operator enters the work envelope."  
  * **Layer Name**: Perception Layer, **Components**: "3D Laser Scanner, Conveyor Part-Present Sensor", **Specifications**: "Scanner provides sub-millimeter accuracy."  
  * **Layer Name**: Edge Control Layer, **Components**: "Raspberry Pi, Node-RED, MQTT Broker", **Specifications**: "Orchestrates the sequence of operations and communicates with other line systems."  
  * **Layer Name**: Material Handling Layer, **Components**: "AMR Fleet Integration", **Specifications**: "Node-RED sends dispatch commands to the AMR fleet manager via REST API."  
* **Security Measures**: The control network for the cell is isolated from the main corporate network. Communication between the Raspberry Pi and the MES is encrypted and uses a dedicated service account.  
* **Scalability Design**: The modular design allows for easy replication. The Node-RED flow can be exported, and the robot/scanner programs can be copied to a new cell, allowing for rapid deployment of additional inspection stations.

## **10\. Future Roadmap**

* **Timeline**: "Q4 2026", **Initiative**: "Closed-Loop 3D Printer Feedback", **Description**: "Develop a system that analyzes trends in dimensional deviations and automatically adjusts the printing parameters (e.g., temperature, speed) on the 3D printers that are producing the parts.", **Expected Benefit**: "Move from defect detection to defect prevention, creating a self-correcting manufacturing process."  
* **Timeline**: "Q2 2027", **Initiative**: "AI-Powered Surface Defect Analysis", **Description**: "Incorporate an AI model that analyzes the camera images to detect and classify cosmetic surface defects (e.g., scratches, discoloration, layer shifts) in addition to dimensional checks.", **Expected Benefit**: "A single station that provides 100% inspection for both geometric and cosmetic quality."

## **11\. Lessons Learned**

* **Category**: "Safety", **Lesson Title**: "Integrate Safety Systems Early in the Design Phase", **Description**: "We initially planned for physical fencing, but operator feedback highlighted the need for easier access. Integrating laser scanners was decided later, which required some minor layout changes. Planning for fenceless safety from the start would have been more efficient.", **Recommendation**: "Treat safety systems as a core component of the cell's design from day one, not as an add-on. This ensures a more integrated, ergonomic, and efficient final layout."  
* **Category**: "Robotics", **Lesson Title**: "Fixture Design is as Critical as the Robot's Programming", **Description**: "Our initial fixture design did not hold the part rigidly enough, leading to tiny vibrations that caused inconsistent scan results. We had to redesign it with precision clamps to ensure absolute stability during the measurement process.", **Recommendation**: "Invest heavily in the design and engineering of the part-holding fixture. It is the foundation of measurement repeatability and accuracy in any automated inspection cell."  
* **Category**: "Process", **Lesson Title**: "Define Go/No-Go Tolerances with Manufacturing and Design Engineers", **Description**: "The software team could measure deviations down to the micron, but we didn't initially know what an 'acceptable' deviation was. We had to work closely with the original CAD designers and assembly line engineers to define meaningful, functional tolerances for the Pass/Fail criteria.", **Recommendation**: "Establish a cross-functional team to define quality standards before you start writing the analysis code. The definition of 'good' is an engineering decision, not just a programming one."

## **12\. Contact Information & Media**

* **Contact Person**: "Aadil Feroze"  
* **Contact Title**: "CTO"  
* Images:  
  1\.

## **13\. Tags & Classification**

* **Industry Tags**: "Drone Manufacturing", "3D Printing", "Additive Manufacturing", "Robotics"  
* **Technology Tags**: "Quality Control", "Robotic Automation", "3D Laser Scanning", "AMR", "Conveyor Systems", "Node-RED", "Raspberry Pi"