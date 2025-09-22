# **Use Case Submission: ROS2-Based Autonomous Mobile Robot (AMR) Fleet**

## **1\. Basic Information Section**

* **Title**: ROS2-Based Autonomous Mobile Robot (AMR) Fleet for Factory Logistics  
* **Subtitle**: An intelligent, driverless transport system built on ROS2, using SLAM navigation and a centralized communication hub to autonomously move parts between manufacturing, quality control, and assembly stations.  
* **Description/Executive Summary**: The KACST Industry 4.0 Capability Center deployed a fleet of Autonomous Mobile Robots (AMRs) to eliminate manual material handling. The AMRs are built on a ROS2 (Robot Operating System 2\) base for robust navigation and control, with a high-level Android system for task management. They navigate using SLAM technology powered by 360° LiDAR and obstacle avoidance sensors. A central Raspberry Pi running Node-RED communicates with the AMRs' REST APIs, allowing any station on the line to request transport, creating a truly integrated and efficient workflow.  
* **Category**: Supply Chain  
* **Factory Name**: KACST Industry 4.0 Capability Center

## **2\. Location Information**

* **City**: Riyadh  
* **Geographic Coordinates**:  
  * **Latitude**: 24.7136  
  * **Longitude**: 46.6753

## **3\. Business Challenge**

* **Industry Context**: In modern manufacturing, the time parts spend being manually moved between stations is non-value-added waste. This manual transport is often inefficient, prone to errors (delivering the wrong parts), a potential safety hazard, and a major source of production bottlenecks, preventing a smooth, continuous flow.  
* **Specific Problems**:  
  1. "Significant operator time was wasted walking parts between the 3D printing farm, the two quality control stations, and the final assembly area."  
  2. "Production would often halt at one station while it waited for parts to be manually delivered from the previous one."  
  3. "Risk of damage to sensitive components during manual transport."  
  4. "No digital traceability of material flow between workstations."  
* **Financial Loss/Impact**: "Estimated SAR 450,000 annually in lost productivity due to operator transit time and line stoppages waiting for materials."

## **4\. Solution Overview**

* **Selection Criteria**:  
  1. "The system must navigate a dynamic factory environment safely and autonomously, avoiding people and equipment."  
  2. "Must provide a simple, accessible API to allow for integration with other automated cells and systems."  
  3. "The navigation system must be based on a robust, industry-standard platform like ROS2."  
  4. "The fleet must be centrally managed but capable of decentralized, independent task execution."  
* **Selected Vendor**: IIoT Solutions  
* **Technology Components**:  
  1. "AMR chassis with a ROS2-based control system."  
  2. "High-level Android OS for task management and diagnostics."  
  3. "360° LiDAR sensor for primary navigation and SLAM (Simultaneous Localization and Mapping)."  
  4. "Bottom-mounted proximity sensors for low-level obstacle and cliff detection."  
  5. "A central Raspberry Pi running Node-RED, acting as a dispatch hub by communicating with the AMRs' REST APIs."  
* **Vendor Process**: The vendor first mapped the entire factory floor using the AMR's SLAM capabilities to create a master digital map. They then developed standardized Node-RED workflows for common tasks (e.g., "Go to QC Station," "Wait for Load," "Go to Assembly") that could be easily triggered by other systems.  
* **Vendor** Selection **Reasons**: The vendor was chosen for their deep expertise in ROS2 and their ability to provide a solution with an easily accessible REST API, which was critical for integrating the AMRs into the existing Node-RED-based factory control ecosystem.

## **5\. Project Teams**

* **Internal Team Members**:  
  * **Role**: Project Lead, **Name**: Aadil Feroze, **Title**: CTO  
  * **Role**: Systems Integration Lead, **Name**: Amro Abouzied, **Title**: Solutions Architect  
  * **Role**: Automation Lead, **Name**: Abdurrahman Bajabir, **Title**: Production Engineer  
  * **Role**: AI Developer & Robotics Lead, **Name**: Hamza Feroze, **Title**: AI Developer

## **6\. Implementation Details**

* **Implementation Time**: "3 Months"  
* **Total Budget**: "SAR 300,000"  
* **Methodology**: The implementation focused on an integration-first approach. The core AMR functionality was proven first. Then, the team focused exclusively on developing the API communication layer in Node-RED, ensuring that any station could reliably call and dispatch an AMR before the fleet was put into full production service.  
* **Implementation Phases**:  
  * **Phase Name**: Factory Mapping & Path Planning, **Duration**: 2 weeks, **Objectives**: Scan the entire facility, create the master SLAM map, define primary and alternative routes, identify pickup/drop-off points, **Key Activities**: AMR-led site survey, map annotation, virtual path validation, **Budget**: "SAR 50,000"  
  * **Phase Name**: Integration & API Development, **Duration**: 6 weeks, **Objectives**: Develop the Node-RED workflows for calling AMRs, integrate API calls into the QC stations and packing station, test communication protocols, **Key Activities**: Node-RED flow design, REST API testing, MQTT integration, **Budget**: "SAR 150,000"  
  * **Phase Name**: Fleet Deployment & Stress Testing, **Duration**: 4 weeks, **Objectives**: Deploy the full fleet, run high-volume transport scenarios to test traffic management and battery charging cycles, **Key Activities**: Live production simulation, multi-AMR congestion testing, auto-charging validation, **Budget**: "SAR 100,000"

## **7\. Results & Impact**

* **Quantitative Results**:  
  * **Metric Name**: Material Transit Time (QC to Assembly), **Baseline Value**: "15 minutes (manual)", **Current Value**: "3 minutes (AMR)", **Improvement**: "80% reduction in transit time"  
  * **Metric Name**: Operator Walking Distance, **Baseline Value**: "5 km/day", **Current Value**: "0.5 km/day", **Improvement**: "90% reduction"  
  * **Metric Name**: Workstation Idle Time (waiting for parts), **Baseline Value**: "45 minutes/day", **Current Value**: "5 minutes/day", **Improvement**: "89% reduction"  
* **Qualitative Impacts**:  
  * "Transformed the factory logistics from a chaotic, manual process into a predictable, automated, and on-demand system."  
  * "Significantly improved operator safety by removing the need to manually push heavy carts through busy walkways." \* "Created a fully traceable digital record of every material movement in the factory."  
* **ROI Metrics**:  
  * **ROI Percentage**: "50% ROI in first year"  
  * **Annual Savings**: "SAR 450,000 (from recovered productivity)"  
  * **Total Investment**: "SAR 300,000"  
  * **Three-Year ROI**: "Projected 450% ROI over three years"

## **8\. Challenges & Solutions**

* **Implementation Challenges**:  
  * **Challenge Name**: Wi-Fi Coverage Blackouts, **Description**: "During initial testing, the AMRs would occasionally stop in certain areas of the factory due to weak Wi-Fi signals, causing them to lose connection with the central Node-RED dispatcher.", **Solution**: "A Wi-Fi site survey was conducted, and three industrial-grade wireless access points were added to eliminate the dead zones. The AMR's software was also updated to have a more robust reconnection protocol.", **Outcome**: "The AMRs now have 100% reliable network connectivity throughout the entire operational area."  
  * **Challenge Name**: Standardizing the "Docking" Handshake, **Description**: "Defining the precise location and signal for the AMR to successfully receive a part from the robotic QC station required very tight integration.", **Solution**: "The team used a physical docking guide on the floor for alignment and an MQTT-based digital handshake. The QC station's Node-RED instance publishes a 'Ready\_to\_Load' message. The AMR moves into position, and upon successful docking, its onboard system publishes a 'Ready\_to\_Receive' message, which then triggers the QC robot.", **Outcome**: "A highly reliable and repeatable automated transfer process between the fixed robotic cell and the mobile robot."

## **9\. Technical Architecture**

* **System Overview**: The AMR fleet operates on a two-layer software stack: a foundational ROS2 layer for core navigation, mapping (SLAM), and sensor fusion (LiDAR, proximity), and a top-level Android system that manages tasks and exposes a REST API. A central Raspberry Pi running Node-RED acts as the fleet manager and dispatcher. When a station (e.g., QC or Packing) needs a part moved, its local Node-RED instance sends an API call to the central dispatcher, which then assigns and dispatches the nearest available AMR.  
* **Architecture Components**:  
  * **Layer Name**: AMR Hardware, **Components**: "Mobile Chassis, 360° LiDAR, Proximity Sensors, Battery, Drive Motors", **Specifications**: "Includes auto-charging capability."  
  * **Layer Name**: AMR Software, **Components**: "ROS2 (Navigation & Control), Android OS (Task Management), REST API Server", **Specifications**: "SLAM algorithm is used for localization within the pre-generated map."  
  * **Layer Name**: Central Dispatch & Integration, **Components**: "Raspberry Pi, Node-RED, MQTT Broker", **Specifications**: "Acts as the central communication hub between the factory stations and the AMR fleet's API."  
* **Security Measures**: The AMR control network is on a dedicated, encrypted Wi-Fi network. API calls between Node-RED and the AMRs use token-based authentication.  
* **Scalability Design**: Adding more AMRs to the fleet is straightforward. A new robot is simply registered with the central dispatcher. New pickup/drop-off points can be added to the SLAM map without reprogramming the entire system.

## **10\. Future Roadmap**

* **Timeline**: "Q2 2027", **Initiative**: "Integration with Automated Doors & Lifts", **Description**: "Enable the AMRs to communicate with building infrastructure, allowing them to automatically open doors or call elevators to navigate between different floors or fire-rated zones.", **Expected Benefit**: "A fully autonomous factory-wide logistics network, capable of multi-floor operation."

## **11\. Lessons Learned**

* **Category**: "Networking", **Lesson Title**: "Industrial Wi-Fi is Non-Negotiable", **Description**: "We initially thought consumer-grade Wi-Fi would be sufficient. We quickly learned that the signal reflections and interference in a factory environment require industrial-grade access points for the reliable connectivity that mobile robots depend on.", **Recommendation**: "For any mobile robotics project, invest in a professional wireless site survey and deploy robust networking hardware from the start. It is the foundation of the entire system."  
* **Category**: "Integration", **Lesson Title**: "Standardize Your API Calls Early", **Description**: "We initially had different stations sending slightly different commands. We created a standardized library of commands in Node-RED (e.g., 'GOTO\_QC1', 'FETCH\_FROM\_PACKING') that all systems now use. This made adding new stations much faster and reduced integration errors.", **Recommendation**: "Treat your internal factory communication as a formal API. Define a clear, consistent set of commands and statuses that all systems will use. Document it and stick to it."

## **12\. Contact Information & Media**

* **Contact Person**: "Aadil Feroze"  
* **Contact Title**: "CTO"  
* **Images**:  
  1.  2\.      3\.  

## **13\. Tags & Classification**

* **Industry Tags**: "Factory Logistics", "Material Handling", "Intralogistics"  
* **Technology Tags**: "AMR", "ROS2", "SLAM", "LIDAR", "Node-RED", "REST