# GVE Devnet: DNA Center & Github Configuration Template Manager

## Contacts
* Eda Akturk 
* Charles Llewellyn

## Solution Components
*  Python 3.8
*  Cisco DNA Center 
    - [API Documentation](https://developer.cisco.com/docs/dna-center/#!cisco-dna-2-1-2-x-api-overview)
*  Github
    - [API Documentation](https://docs.github.com/en/free-pro-team@latest/rest/reference/actions)
*  Cisco Webex
*  MongoDB


## Solution Overview
The solution creates a flask application that allows to manage configuration templates between DNA Center Lab, 
DNA Center Prod and Github. 
- Templates can be created on Github in the format of project_name/file_name with the template content from DNA Center Configuration Templates
- Template status can be tracked between the different mediums and the sync status can 
be viewed on the GUI. 
- Templates can be pushed/updated in DNA Center Prod from Github Content. 

For details please view "Usage" below. 

## Installation/Configuration

#### Clone the repo :
```$ git clone (link)```

#### *(Optional) Create Virtual Environment :*
Initialize a virtual environment 

```virtualenv venv```

Activate the virtual env

*Windows*   ``` venv\Scripts\activate```

*Linux* ``` source venv/bin/activate```

#### Install the libraries :

```$ pip install -r requirements.txt```


## Setup: 

*DNA Center*
1. Add the DNA Center Lab credentials in env_var.py
```
DNAC_URL = " "
DNAC_USER = " "
DNAC_PASS = " "
```

2. Add the DNA Center Prod credentials in env_var.py
```
DNAC_URL_PROD = " "
DNAC_USER_PROD = " "
DNAC_PASS_PROD = " "
```


*Database*

3. Download and install MongoDB. 

4. Add the database credentials to env_var.py 
```
Database = " "
Cluster = " "
Collection = " "
```


*Github*

5. In your Github account go to Settings --> Developer Settings --> Personal Access Tokens (https://github.com/settings/tokens). 

6. Here you will see your access tokens which allow to use the github api. You can use an existing access token or generate a new one from "Generate access token." 

7. Add your github credentials to the env_var.py. The Github Url format should be as: "https://api.github.com/repos/:username/:repo"
```
GITHUB_TOKEN = " "
GITHUB_URL = " "
```


*Cisco Webex*

8. Create a Webex Chatbot from [here.](https://developer.webex.com/my-apps/new/bot)

9. Add your Bot Token to env_var.py.
```
WEBEX_ACCESS_TOKEN= " "
```
10. Add the email of Webex account to receive the notifications to webex_notification.py. 
```
to = " "
```

## Usage
From the GUI the users can:

1. Update database with configuration template metadata from DNA Center Lab
2. Compares configuration template content data with Github content, DNA Center Lab Content and DNA Center Prod content 
3. Creates development branch in GitHub with configuration templates 
4. Creates/updates templates in DNA Center Lab or Prod

### GUI
![/IMAGES/gui.png](/IMAGES/gui.png)

# Screenshots
![/IMAGES/0image.png](/IMAGES/updatedb.jpg)
![/IMAGES/0image.png](/IMAGES/branch.jpg)
![/IMAGES/0image.png](/IMAGES/synctemplates.jpg)
![/IMAGES/0image.png](/IMAGES/pushtemplates.jpg)

### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.
