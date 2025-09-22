# **Use Case Submission: AI-Powered Drone Arm Color Verification Station**

## **1\. Basic Information Section**

* **Title**: AI-Powered Drone Arm Color Verification Station  
* **Subtitle**: An intelligent quality control system that uses computer vision and AMR integration to automatically verify drone arm colors against production orders, eliminating sorting errors and ensuring accuracy.  
* **Description/Executive Summary**: The KACST Industry 4.0 Capability Center deployed an automated quality control station that integrates with Autonomous Mobile Robots (AMRs). The system uses a custom-trained YOLOv8 computer vision model to detect and count colored drone arms delivered by an AMR, compares the count to the active production order, and automatically dispatches the AMR upon successful verification. This eliminates manual sorting errors, increases throughput, and provides real-time quality assurance.  
* **Category**: Quality Control  
* **Factory Name**: KACST Industry 4.0 Capability Center

## **2\. Location Information**

* **City**: Riyadh  
* **Geographic Coordinates**:  
  * **Latitude**: 24.7136  
  * **Longitude**: 46.6753

## **3\. Business Challenge**

* **Industry Context**: In a fast-paced drone assembly line, ensuring that the correct components are routed to the correct assembly station is critical. Manual verification of parts like colored drone arms is prone to human error, especially during high-volume production or when multiple similar orders are processed sequentially. A single misplaced part can lead to incorrect assemblies, causing rework, wasted materials, and significant production delays.  
* **Specific Problems**:  
  1. "Frequent mix-ups of drone arm colors, leading to incorrect kits being sent to the final assembly station."  
  2. "Significant labor time spent on manually counting and verifying components, creating a bottleneck in the workflow."  
  3. "Lack of an automated audit trail to confirm which parts were verified for a specific production order."  
  4. "Delays in dispatching AMRs from the QC station as operators had to manually trigger the next step."  
* **Financial Loss/Impact**: "Estimated SAR 220,000 annually from rework costs, wasted operator time, and production line stoppages caused by incorrect part sorting."

## **4\. Solution Overview**

* **Selection Criteria**:  
  1. "Must achieve \>99% accuracy in identifying and counting multi-class colored drone arms (red, blue, black, etc.)."  
  2. "Must seamlessly integrate with the existing AMR fleet via REST API for automatic status polling and dispatch."  
  3. "Must provide a real-time dashboard for monitoring the verification process and results."  
  4. "The system must be capable of running on low-power edge devices like a Raspberry Pi to minimize footprint."  
* **Selected Vendor**: IIoT Solutions  
* **Technology Components**:  
  1. "Custom-trained YOLOv8 object detection model for multi-class drone arm color detection."  
  2. "Streamlit-based web dashboard for real-time visualization, controls, and status updates."  
  3. "An AMR integration module using Python requests to poll status and dispatch robots via REST API."  
  4. "Edge computing hardware (Raspberry Pi 4\) connected to a USB webcam for image capture and processing."  
* **Vendor Process**: The project was developed internally by IIoT Solutions as a targeted solution to a known production bottleneck. The process involved rapid prototyping, including a data collection phase where over 150 images were captured and annotated to train the initial computer vision model. The solution was then tested and validated directly on the production floor.  
* **Vendor Selection Reasons**: As an internal development, IIoT Solutions leveraged its in-house expertise in computer vision, IoT integration, and factory automation to build a custom solution perfectly tailored to the specific operational need, ensuring a perfect fit with existing infrastructure.

## **5\. Project Teams**

* **Internal Team Members**:  
  * **Role**: Project Lead, **Name**: Aadil Feroze, **Title**: CTO  
  * **Role**: Systems Integration Lead, **Name**: Amro Abouzied, **Title**: Solutions Architect  
  * **Role**: Vision & AI Lead, **Name**: Hamza Feroze, **Title**: AI Developer

## **6\. Implementation Details**

* **Implementation Time**: "2 Months"  
* **Total Budget**: "SAR 150,000"  
* **Methodology**: The project followed an agile methodology, starting with the core challenge of model development. Once the model achieved the desired accuracy, the team built the surrounding components, including the Streamlit dashboard and AMR integration, deploying each feature iteratively for rapid feedback and testing.  
* **Implementation Phases**:  
  * **Phase Name**: Data Collection & Model Training, **Duration**: 3 weeks, **Objectives**: Collect and annotate training images, train and validate the YOLOv8 model to \>99% accuracy, **Key Activities**: Image capture, data labeling, model training, hyperparameter tuning, **Budget**: "SAR 50,000"  
  * **Phase Name**: Application & Dashboard Development, **Duration**: 2 weeks, **Objectives**: Build the Streamlit web interface, develop order verification logic, create visualization components, **Key Activities**: UI/UX design, front-end development, logic implementation, **Budget**: "SAR 40,000"  
  * **Phase Name**: AMR Integration & Hardware Setup, **Duration**: 2 weeks, **Objectives**: Set up the Raspberry Pi station, connect the camera, develop and test AMR API communication, **Key Activities**: Hardware installation, network configuration, API scripting, end-to-end testing, **Budget**: "SAR 40,000"  
  * **Phase Name**: Deployment & User Training, **Duration**: 1 week, **Objectives**: Deploy the Docker container to production, train line operators, monitor initial performance, **Key Activities**: Docker deployment, user training sessions, system handover, **Budget**: "SAR 20,000"

## **7\. Results & Impact**

* **Quantitative Results**:  
  * **Metric Name**: Part Sorting Error Rate, **Baseline Value**: "5%", **Current Value**: "0.1%", **Improvement**: "98% reduction in sorting errors"  
  * **Metric Name**: Average QC Cycle Time, **Baseline Value**: "120 seconds", **Current Value**: "15 seconds", **Improvement**: "87.5% reduction in verification time"  
  * **Metric Name**: AMR Dwell Time at QC Station, **Baseline Value**: "180 seconds", **Current Value**: "20 seconds", **Improvement**: "89% reduction"  
* **Qualitative Impacts**:  
  * "Dramatically increased operator confidence and trust in the production process, as they no longer have to second-guess if the right parts are being used."  
  * "Created a fully automated, hands-off verification point in the production line, freeing up personnel for more complex tasks."  
  * "Provided a digital audit trail for every batch, improving traceability and accountability."  
* **ROI Metrics**:  
  * **ROI Percentage**: "47% ROI in first year"  
  * **Annual Savings**: "SAR 220,000 (from eliminating rework and reducing labor)"  
  * **Total Investment**: "SAR 150,000"  
  * **Three-Year ROI**: "Projected 350% ROI over three years"

## **8\. Challenges & Solutions**

* **Implementation Challenges**:  
  * **Challenge Name**: Variable Lighting Conditions, **Description**: "Changes in ambient factory lighting throughout the day and between shifts affected the camera's perception of colors, leading to inconsistent model performance.", **Solution**: "We implemented data augmentation techniques during training, including random brightness, contrast, and saturation adjustments. We also installed a small, dedicated LED light source at the QC station to ensure consistent illumination.", **Outcome**: "The model is now robust and performs reliably regardless of external lighting conditions, achieving consistent accuracy."  
  * **Challenge Name**: AMR API Instability, **Description**: "The AMR's REST API endpoint would occasionally become unresponsive, causing the QC station to hang while waiting for a status update.", **Solution**: "We implemented robust error handling with timeouts in our API polling script. If the API fails to respond after a set number of retries, the system logs an error and alerts an operator via the dashboard.", **Outcome**: "The system is now resilient to network hiccups and can gracefully handle temporary AMR connectivity issues without crashing."

## **9\. Technical Architecture**

* **System Overview**: The solution uses a Dockerized Streamlit application running on a Raspberry Pi 4 at the edge. A USB camera provides a live video feed, which is processed locally by a YOLOv8 model. The application communicates with the factory's AMR fleet over the network via REST API calls to check status and dispatch units.  
* **Architecture Components**:  
  * **Layer Name**: Edge Hardware Layer, **Components**: "Raspberry Pi 4, USB Webcam, LED Lighting", **Specifications**: "Device is mounted at the QC station overlooking the AMR's drop-off point."  
  * **Layer Name**: Application Layer, **Components**: "Python 3.11, Streamlit, YOLOv8, OpenCV", **Specifications**: "Contained within a Docker image for portability and consistent deployment."  
  * **Layer Name**: Integration Layer, **Components**: "REST API Client (Python Requests)", **Specifications**: "Handles GET requests for AMR status and POST requests for dispatch commands."  
  * **Layer Name**: Presentation Layer, **Components**: "Streamlit Web UI", **Specifications**: "Provides a real-time dashboard accessible from any browser on the factory network."  
* **Security Measures**: The QC station is on an isolated IoT network VLAN, with access restricted to the AMR control server and authorized management stations. The Streamlit application itself has no inbound external access.  
* **Scalability Design**: The entire system is self-contained in a Docker image. To scale, a new QC station can be deployed by simply flashing a new Raspberry Pi, connecting a camera, and running the container, allowing for rapid rollout to other production lines.

## **10\. Future Roadmap**

* **Timeline**: "Q3 2026", **Initiative**: "Defect Detection Module", **Description**: "Expand the computer vision model to not only detect color but also identify common physical defects on the drone arms, such as cracks, scratches, or print artifacts.", **Expected Benefit**: "Create a single, consolidated QC station that checks for both correctness and quality, further increasing product reliability."  
* **Timeline**: "Q1 2027", **Initiative**: "MES Integration for Dynamic Orders", **Description**: "Integrate the QC station with the main factory MES to pull production orders dynamically instead of using a pre-configured list. This would allow for real-time order changes.", **Expected Benefit**: "Increased production agility and the ability to handle custom, on-the-fly drone configurations."

## **11\. Lessons Learned**

* **Category**: "Technical", **Lesson Title**: "Good Data is More Important Than a Complex Model", **Description**: "We spent significant time ensuring our training data was high-quality and captured under realistic factory conditions. A relatively lightweight model like YOLOv8 performed exceptionally well with good data, which was crucial for running on a Raspberry Pi.", **Recommendation**: "Invest 80% of your effort in data collection, cleaning, and augmentation. This will yield far better results than trying to optimize a complex model fed with poor-quality data."  
* **Category**: "Process", **Lesson Title**: "Involve Operators from Day One", **Description**: "We initially designed the dashboard with purely technical metrics. Feedback from the line operators led us to simplify the interface, add larger status indicators (Pass/Fail), and include a manual override, which made them trust and adopt the system much faster.", **Recommendation**: "Treat the end-users as key stakeholders throughout the entire development process. Their practical insights are invaluable for building a tool that actually gets used effectively."

## **12\. Contact Information & Media**

* **Contact Person**: "Aadil Feroze"  
* **Contact Title**: "CTO"  
* **Images**:  
  1.   
  2.   
  3. 

## **13\. Tags & Classification**

* **Industry Tags**: "Drone Manufacturing", "Aerospace", "Automated Quality Control"  
* **Technology Tags**: "Computer Vision", "YOLOv8", "Machine Learning", "Edge Computing