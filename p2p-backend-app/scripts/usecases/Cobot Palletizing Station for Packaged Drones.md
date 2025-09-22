# **Use Case Submission: Cobot Palletizing Station for Packaged Drones**

## **1\. Basic Information Section**

* **Title**: Cobot Palletizing Station for Packaged Drones  
* **Subtitle**: A collaborative robot (Cobot) with suction grippers automates the final end-of-line task, picking finished drone packages and stacking them onto a pallet for shipment.  
* **Description/Executive Summary**: The KACST Industry 4.0 Capability Center automated its final packaging step with a collaborative robot. After a drone is boxed and taped, it is placed on a pickup surface. A photoelectric sensor detects the box's presence and sends a signal to a Raspberry Pi. A Node-RED workflow then commands the Cobot, which uses a vacuum-powered suction gripper to pick up the box and place it in a pre-defined pattern on a shipping pallet, making it ready for logistics.  
* **Category**: Factory Automation  
* **Factory Name**: KACST Industry 4.0 Capability Center

## **2\. Location Information**

* **City**: Riyadh  
* **Geographic Coordinates**:  
  * **Latitude**: 24.7136  
  * **Longitude**: 46.6753

## **3\. Business Challenge**

* **Industry Context**: The final stage of packaging and palletizing is a classic bottleneck in many production lines. This task is highly repetitive, physically demanding, and ergonomically hazardous for human operators, often leading to repetitive strain injuries and inconsistent stacking quality.  
* **Specific Problems**:  
  1. "High risk of musculoskeletal injuries for operators performing repetitive lifting and twisting motions to stack boxes."  
  2. "The manual palletizing speed was the primary constraint on the entire production line's throughput."  
  3. "Inconsistent and unstable stacking of boxes on the pallet, leading to potential product damage during transit."  
  4. "High labor costs associated with a low-skill, physically demanding end-of-line task."  
* **Financial Loss/Impact**: "Estimated SAR 280,000 annually in costs related to operator injuries, production bottlenecks, and damaged goods from unstable pallets."

## **4\. Solution Overview**

* **Selection Criteria**:  
  1. "The solution must be safe for operators to work alongside without requiring a large safety fence (a collaborative robot)."  
  2. "The robot's end-of-arm-tool must be able to reliably grip cardboard boxes without causing damage."  
  3. "The system must be triggered automatically by the presence of a new box."  
  4. "Must integrate seamlessly into the existing factory control system built on Node-RED and Raspberry Pi."  
* **Selected Vendor**: IIoT Solutions  
* **Technology Components**:  
  1. "6-axis Collaborative Robot (Cobot) with built-in force-torque sensors for safety."  
  2. "Vacuum-powered end-of-arm-tool with multiple bellows suction cups."  
  3. "Retro-reflective photoelectric sensor to detect box presence."  
  4. "A Raspberry Pi running a Node-RED workflow to orchestrate the sensor and the Cobot."  
* **Vendor Process**: The vendor first performed a reach and payload study to select the appropriate Cobot model. They then prototyped several suction gripper configurations to find the most reliable design for the specific cardboard boxes being used before installing and commissioning the full work cell.  
* **Vendor** Selection **Reasons**: IIoT Solutions was selected due to their expertise in integrating collaborative robotics with lightweight, event-driven IoT control systems like Node-RED, which was a perfect fit for the factory's existing architecture.

## **5\. Project Teams**

* **Internal Team Members**:  
  * **Role**: Project Lead, **Name**: Aadil Feroze, **Title**: CTO  
  * **Role**: Systems Integration Lead, **Name**: Amro Abouzied, **Title**: Solutions Architect  
  * **Role**: Robotics & Automation Lead, **Name**: Abdurrahman Bajabir, **Title**: Production Engineer  
  * **Role**: AI Developer, **Name**: Hamza Feroze, **Title**: AI Developer

## **6\. Implementation Details**

* **Implementation Time**: "3 Months"  
* **Total Budget**: "SAR 200,000"  
* **Methodology**: The project followed a "safety-first" agile approach. The core robotic pick-and-place task was programmed first. Then, the sensor integration and safety systems were layered on and rigorously tested before the system was allowed to run at full speed in production.  
* **Implementation Phases**:  
  * **Phase Name**: Gripper Design & Hardware Installation, **Duration**: 4 weeks, **Objectives**: Procure the Cobot, design and test the suction gripper, install the physical cell, **Key Activities**: Cobot installation, gripper prototyping, mounting the photoelectric sensor, **Budget**: "SAR 110,000"  
  * **Phase Name**: Robot Programming & Logic Development, **Duration**: 5 weeks, **Objectives**: Program the Cobot's palletizing pattern, develop the Node-RED workflow to link the sensor to the robot, **Key Activities**: Robot path teaching, Node-RED flow creation, I/O testing, **Budget**: "SAR 60,000"  
  * **Phase Name**: Commissioning & Safety Validation, **Duration**: 3 weeks, **Objectives**: Perform end-to-end testing, validate the Cobot's collaborative safety features, optimize the cycle time, **Key Activities**: Full-cycle testing, safety risk assessment, performance tuning, **Budget**: "SAR 30,000"

## **7\. Results & Impact**

* **Quantitative Results**:  
  * **Metric Name**: Manual Lifting Actions (per shift), **Baseline Value**: "800+", **Current Value**: "0", **Improvement**: "100% elimination of manual palletizing labor"  
  * **Metric Name**: End-of-Line Cycle Time, **Baseline Value**: "25 seconds/box", **Current Value**: "10 seconds/box", **Improvement**: "60% reduction in cycle time"  
  * **Metric Name**: Pallet Stability Failure Rate, **Baseline Value**: "3%", **Current Value**: "0.1%", **Improvement**: "97% reduction in stacking errors"  
* **Qualitative Impacts**:  
  * "Vastly improved workplace ergonomics and eliminated the primary source of back and shoulder injuries on the line."  
  * "Created a stable, predictable, and paced end to the production line, allowing the upstream processes to run at a consistently higher speed."  
  * "Operators were upskilled from manual labor to robot supervision and exception handling."  
* **ROI Metrics**:  
  * **ROI Percentage**: "40% ROI in first year"  
  * **Annual Savings**: "SAR 280,000 (from reduced labor, injury claims, and damaged goods)"  
  * **Total Investment**: "SAR 200,000"  
  * **Three-Year ROI**: "Projected 380% ROI over three years"

## **8\. Challenges & Solutions**

* **Implementation Challenges**:  
  * **Challenge Name**: Suction Reliability on Cardboard, **Description**: "Cardboard dust and minor surface imperfections on the boxes occasionally caused the suction cups to fail to achieve a secure vacuum seal, leading to dropped boxes.", **Solution**: "We switched to multi-bellows suction cups, which are more compliant to surface variations. We also programmed the robot to perform a 'vacuum check' immediately after picking; if the vacuum sensor reports a weak seal, the robot places the box back and retries the pick.", **Outcome**: "The pick-and-place success rate is now greater than 99.9%, with the robot able to self-correct on the rare occasion of a failed grip."  
  * **Challenge Name**: Precise Box Positioning for Pickup, **Description**: "The robot requires the box to be in a consistent position every time, but boxes sometimes shifted slightly after being taped.", **Solution**: "Simple physical guides were added to the pickup surface to create a V-shaped 'nest'. This ensures that every box settles into the exact same final position and orientation, ready for the robot to pick.", **Outcome**: "The need for a more complex and expensive vision-guidance system was eliminated, providing a simple and robust solution."

## **9\. Technical Architecture**

* **System Overview**: The workflow is triggered when a finished drone package slides into a pickup nest, breaking the beam of a photoelectric sensor. The sensor sends a digital high signal to the GPIO pins of a Raspberry Pi. A Node-RED flow detects this input and sends a "start cycle" command to the Cobot's controller via a TCP/IP socket. The Cobot, equipped with suction grippers, executes its pre-programmed routine to pick the box and place it on the pallet.  
* **Architecture Components**:  
  * **Layer Name**: Physical Automation Layer, **Components**: "6-axis Collaborative Robot, Suction Cup End-of-Arm Tooling, Pickup Nest", **Specifications**: "Cobot operates without a safety fence due to its inherent force-limiting safety features."  
  * **Layer Name**: Perception Layer, **Components**: "Photoelectric 'Box-Present' Sensor", **Specifications**: "Provides a simple binary signal to trigger the automation."  
  * **Layer Name**: Edge Control Layer, **Components**: "Raspberry Pi, Node-RED", **Specifications**: "Acts as the simple, low-cost brain of the work cell, translating the sensor input into a robot command."  
* **Security Measures**: The Cobot and Raspberry Pi are on an isolated control network, inaccessible from the main corporate LAN, to prevent unauthorized commands.  
* **Scalability Design**: The Node-RED flow and the robot's palletizing program can be easily modified with a graphical interface to accommodate different box sizes or stacking patterns.

## **10\. Future Roadmap**

* **Timeline**: "Q3 2027", **Initiative**: "Automated Pallet Management", **Description**: "Integrate the cell with the AMR fleet. An AMR will be tasked with automatically delivering empty pallets to the station and removing full pallets for transport to the shipping area.", **Expected Benefit**: "Create a fully autonomous end-to-end process from final assembly to the shipping dock."

## **11\. Lessons Learned**

* **Category**: "Robotics", **Lesson Title**: "For Simple Tasks, Simple Triggers are Best", **Description**: "We initially considered using a vision system to find the box. However, the combination of a simple mechanical nest and a cheap photoelectric sensor proved to be faster, more reliable, and a fraction of the cost for this specific task.", **Recommendation**: "Don't over-engineer the solution. Always evaluate the simplest possible sensor and control strategy first; it's often the most robust."  
* **Category**: "Safety", **Lesson Title**: "Collaborative Safety Requires a Risk Assessment", **Description**: "While Cobots are inherently safer, they are not inherently safe. A formal risk assessment was still required to validate speeds, payload, and potential pinch points to ensure it was truly safe for operators to work alongside.", **Recommendation**: "Always perform a thorough risk assessment when deploying any robot, even a collaborative one. Safety is a system property, not just a product feature."

## **12\. Contact Information & Media**

* **Contact Person**: "Aadil Feroze"  
* **Contact Title**: "CTO"  
* **Images**:  
  1.   
  2.   
  3. 

## **13\. Tags & Classification**

* **Industry Tags**: "Packaging", "Palletizing", "End-of-Line Automation", "Logistics"  
* **Technology Tags**: "Collaborative Robot", "Cobot", "Su