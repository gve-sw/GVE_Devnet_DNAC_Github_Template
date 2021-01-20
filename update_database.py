"""
Copyright (c) 2021 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

from datetime import datetime

from env_var import *

from models import DNACenter, LocalDatabase, Github

DNACenterLab = DNACenter(username=DNAC_USER, password=DNAC_PASS, base_url=DNAC_URL, name="Lab")
DNACenterProd = DNACenter(username=DNAC_USER_PROD, password=DNAC_PASS_PROD, base_url=DNAC_URL_PROD, name="Prod")
db = LocalDatabase(cluster=Cluster1, database=Database1, collection=Collection1)
github = Github(base_url=GITHUB_URL, token=GITHUB_TOKEN)


def sync_templates(templates):
    """
    The template content is compared between: Github, DNA Center Lab and DNA Center Prod
    The sync status is updated in the database
    """
    for template_name in templates:
        print(template_name)
        try:
            project_name = db.collection.find({"name": template_name})[0]["projectName"]
        except:
            project_name = template_name["projectName"]
            template_name = template_name["name"]

        # Check if the template is in github
        try:
            github_content = github.get_github_file_content(project_name, template_name)
            dnac_lab_content = DNACenterLab.get_template_content_by_name(project_name, template_name)
            dnac_prod_content = DNACenterProd.get_template_content_by_name(project_name, template_name)

            # Update the DNA Center Status
            if dnac_lab_content == 404:
                new_value = {"inLab": "Not Found"}
            elif dnac_lab_content == github_content:
                new_value = {"inLab": "In Sync"}
            else:
                new_value = {"inLab": "NOT In Sync"}
            db.update_db(template_name, new_value)

            # Update the DNA Prod Status
            if dnac_prod_content == 404:
                new_value = {"inProd": "Not Found"}
            elif dnac_prod_content == github_content:
                new_value = {"inProd": "In Sync"}
            else:
                new_value = {"inProd": "NOT In Sync"}
            db.update_db(template_name, new_value)

            # Update the Last Update time in database
            today = datetime.now().strftime('%H:%M %m-%d-%Y')
            new_value = {"updateDate": today}
            db.update_db(template_name, new_value)

        except:
            new_value = {"inLab": "NOT in Github"}
            db.update_db(template_name, new_value)
            new_value = {"inProd": "NOT in Github"}
            db.update_db(template_name, new_value)

    message = "Template status sync update has been completed"
    return message


def update_database():
    """
    Create or update a database entry for the templates in DNA Center
    """
    labTemplates = DNACenterLab.get_templates()
    addedTemplates = []

    for temp in labTemplates:
        temp_details = DNACenterLab.get_template_details(temp["templateId"])
        template_name = temp_details["name"]
        project_name = temp_details["projectName"]
        device_family = temp_details["deviceTypes"]

        software_type = temp_details["softwareType"]
        updated = db.update_database(template_name, project_name, device_family, software_type)
        if updated["update"]:
            addedTemplates.append(updated["template"])

    if len(addedTemplates) > 0:
        message = "Added Templates to Database: " + ', '.join(addedTemplates)
    else:
        message = "Database has all the templates from DNA Center. No entry has been added."
    return message


def update_branch(templates):
    """
    Pushes the selected templates to Github development branch (the branch will be created if it does not exists)
    Creates a pull request if a template is changed/created
    """
    same_templates = []
    changed_templates = []
    added_templates = []

    for template_name in templates:
        try:
            project_name = db.collection.find({"name": template_name})[0]["projectName"]
        except:
            project_name = template_name["projectName"]
            template_name = template_name["name"]

        dnac_lab_content = DNACenterLab.get_template_content_by_name(project_name, template_name)

        try:
            github_content = github.get_github_file_content(project_name, template_name)

            if dnac_lab_content == github_content:
                print("The content is the same, no need to update the branch")
                same_templates.append(template_name)
            else:
                # a new branch will be created with the updated content
                github.create_new_branch(master_branch="main", new_branch="development")
                github.update_branch(dnac_lab_content, template_name, project_name, branch="development")
                changed_templates.append(template_name)

        except:
            # initial github entry will be created on github
            github.create_new_branch(master_branch="main", new_branch="development")
            github.add_template_github(dnac_lab_content, template_name, project_name)
            added_templates.append(template_name)
            print("Pushed template to github")

    if len(changed_templates) > 0 or len(added_templates) > 0:
        github.create_pull_request(base="main", head="development")
        message = "Pull Request has been created on Github. Please review the changes."
    else:
        message = "Github is upto date."
    return message
