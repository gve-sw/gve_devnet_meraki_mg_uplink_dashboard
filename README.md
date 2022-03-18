# gve_devnet_meraki_mg_uplink_dashboard

The purpose of this sample code is to show how the Meraki Dashboard APIs can be used to provide a comprehensive view of signal or uplink quality for all MGs/MXs with cellular interfaces of an organization. Therefore, a dashboard was created that shows the MGs/MXs, their signal quality and chosen other device details on a single page. The mentioned page includes a list and map view. Furthermore, it is possible to access a separate page with detailed device information and historical signal data for each device by clicking an element in the list. 

## Contacts
* Ramona Renner

## Solution Components
* Meraki Dashboard
* Meraki MG/MX
* Cloud Mongo DB

## Workflow
![/IMAGES/migration_workflow.png](/IMAGES/workflow.png)

## Installation

1. Make sure you have [Python 3.8.0](https://www.python.org/downloads/) and [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) installed

2.	(Optional) Create and activate a virtual environment 
    ```
    python3 -m venv [add name of virtual environment here] 
    source [add name of virtual environment here]/bin/activate
    ```
  * Access the created virtual environment folder
    ```
    cd [add name of virtual environment here] 
    ```

3. Clone this Github repository:  
  ```git clone [add github link here]```
  * For Github link: 
      In Github, click on the **Clone or download** button in the upper part of the page > click the **copy icon**  
      ![/IMAGES/giturl.png](/IMAGES/giturl.png)
  * Or simply download the repository as zip file using 'Download ZIP' button and extract it

4. Access the downloaded folder:  
    ```cd gve_devnet_meraki_mg_uplink_dashboard```

5. Install all dependencies:  
  ```pip install -r requirements.txt```

6. Reuse or set up a cloud **mongoDB account** and request the **connection string** for a later step. [Official Documentation](https://docs.atlas.mongodb.com/getting-started/) [YouTube Video](https://www.youtube.com/watch?v=VQnmcBnguPY)

7. Follow the instructions under https://developer.cisco.com/meraki/api/#!authorization/obtaining-your-meraki-api-key to obtain the **Meraki API Token**. Save the token for a later step.

8. Set up a bot and note the bot username and bot token for a later step. [How to Create a Bot](https://developer.webex.com/docs/bots)

9. Create a Webex Space and add the bot via the bot username to the space. Furthermore, add all people to notify to the space.

10. Retrieve and note the room ID of the created space (see step 9) via the [List Rooms API Call](https://developer.webex.com/docs/api/v1/rooms/list-rooms)

11. Fill in your variables in the **.env** file:      
      
  ```  
    MERAKI_API_TOKEN="[Add Meraki API key (see step 7)]"

    MONGODB_CON="[Add Mongo DB connection string (see step 6)]"

    SCHEDULER_INTERVAL_SEC = [Add interval length in seconds for retrieving and saving MG information in the database. Default: 3600] 

    WEBEX_TEAMS_ACCESS_TOKEN="[Add Webex Bot Token (see step 8)]"
    ROOM_ID="[Add room id here (see step 10)]"
    RSRP_MIN_ALERTING_THRESHOLD=[Add the minumum value for the RSRP value. A smaller value than the threshold will add the device to alert list. Default: -100]
    RSRQ_MIN_ALERTING_THRESHOLD=Add the minumum value for the RSRQ value. A smaller value than the threshold will add the device to alert list. Default: -20]
  ```

  > Note: Mac OS hides the .env file in the finder by default. View the demo folder for example with your preferred IDE to make the file visible.   

  > Note: An SCHEDULER_INTERVAL_SEC value under 60 second is not recommended, since the data transfer takes some time to complete.

9. Run the application   
  ```python3 app.py```


Assuming you kept the default parameters for starting the Flask application, the address to navigate to would be:
https://0.0.0.0:5001


## (Optional) Additional Steps to Demonstrate Access from an External Device

To access this application from an external device, it requires to be reachable over an internet accessible URL. Therefore, it can be deployed on different IaaS platform like Heroku, Amazon Web Services Lambda, Google Cloud Platform (GCP) and more. Alternatively, it is possible to use the tool ngrok for this reason. Please be aware that ngrok can be blocked in some corporate networks.


## Screenshots

![/IMAGES/step1.png](/IMAGES/screenshot4.png)
![/IMAGES/step2.png](/IMAGES/screenshot5.png)
![/IMAGES/step3.png](/IMAGES/screenshot6.png)
![/IMAGES/step4.png](/IMAGES/screenshot7.png)
![/IMAGES/step5.png](/IMAGES/screenshot8.png)


## More Useful Resources
 - Meraki Dashboard API documentation: https://developer.cisco.com/meraki/api-v1/#!get-device

   > This sample code uses predefined leaflet map markers from Vladimir Agafonkin, CloudMade and Thomas Pointhuber. License details, copyright notice etc. are available in the dashboard.html file. [Repository Link](https://github.com/pointhi/leaflet-color-markers).
    

### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.