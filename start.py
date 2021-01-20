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

from flask import Flask, request, render_template

from env_var import *

from models import DNACenter, LocalDatabase, Github
from webex_notification import send_notification
from update_database import update_database, sync_templates, update_branch

app = Flask(__name__)

DNACenterLab = DNACenter(username=DNAC_USER, password=DNAC_PASS, base_url=DNAC_URL, name="Lab")
DNACenterProd = DNACenter(username=DNAC_USER_PROD, password=DNAC_PASS_PROD, base_url=DNAC_URL_PROD, name="Prod")
db = LocalDatabase(cluster=Cluster1, database=Database1, collection=Collection1)
github = Github(base_url=GITHUB_URL, token=GITHUB_TOKEN)


@app.route("/")
def main_page():
    templates = db.get_templates_from_database()
    all_templates = sorted(templates, key=lambda k: k['name'])
    return render_template("columnPage.html", content=all_templates)


@app.route("/selection", methods=['POST', 'GET'])
def main_page_selected():
    templates = db.get_templates_from_database()
    all_templates = sorted(templates, key=lambda k: k['name'])

    if request.method == 'POST':
        form_data = request.form
        button_pushed = form_data["submit_button"]

        if button_pushed == "Push Templates":
            try:
                push_to = form_data["input-type-push"]
                selected_templates = form_data.getlist("template")
                if push_to == "lab":
                    for template_name in selected_templates:
                        project_name = db.collection.find({"name": template_name})[0]["projectName"]
                        device_family = db.collection.find({"name": template_name})[0]["deviceFamily"]
                        software_type = db.collection.find({"name": template_name})[0]["softwareType"]

                        template_content = github.get_github_file_content(template_name=template_name,
                                                                          project_name=project_name)
                        dnac_prod_content = DNACenterLab.get_template_content_by_name(project_name, template_name)
                        if dnac_prod_content == 404:
                            print("Will Push Template to Github: \n")
                            DNACenterLab.create_template(template_name=template_name, template_content=template_content,
                                                          project_name=project_name, device_family=device_family,
                                                          software_type=software_type)
                            new_value = {"inLab": "*View on DNAC Lab*"}
                            db.update_db(template_name, new_value)
                        else:

                            print('Will Update Template: \n')
                            DNACenterLab.update_template(template_name=template_name, template_content="test content",
                                                          project_name=project_name, device_family=device_family, software_type=software_type)
                            new_value = {"inLab": "*View on DNAC Lab*"}
                            db.update_db(template_name, new_value)
                else:

                    for template_name in selected_templates:
                        project_name = db.collection.find({"name": template_name})[0]["projectName"]
                        device_family = db.collection.find({"name": template_name})[0]["deviceFamily"]
                        software_type = db.collection.find({"name": template_name})[0]["softwareType"]
                        template_content = github.get_github_file_content(template_name=template_name,
                                                                          project_name=project_name)
                        dnac_prod_content = DNACenterProd.get_template_content_by_name(project_name, template_name)
                        if dnac_prod_content == 404:
                            print("Will Push Template to Github: \n")
                            DNACenterProd.create_template(template_name=template_name, template_content=template_content,
                                                          project_name=project_name, device_family=device_family,
                                                          software_type=software_type)
                            new_value = {"inProd": "*View on DNAC Prod*"}
                            db.update_db(template_name, new_value)
                        else:

                            print('Will Update Template: \n')
                            DNACenterProd.update_template(template_name=template_name, template_content="test content",
                                                          project_name=project_name, device_family=device_family, software_type=software_type)
                            new_value = {"inProd": "*View on DNAC Lab*"}
                            db.update_db(template_name, new_value)

                message = "Pushed templates " + ', '.join(selected_templates) + " from Github to " + push_to
                result = True
                if len(selected_templates) == 0:
                    message = "Please select templates to update DNA Center"
                    result = False
            except:
                message = "Please contact IT team"
                result = False

        elif button_pushed == "Update Development Branch":
            try:
                selected_templates = form_data.getlist("template")

                # check all the templates if none of the templates has been selected
                if len(selected_templates) == 0:
                    message = update_branch(all_templates)
                else:
                    message = update_branch(selected_templates)
                send_notification(message)
                result = True
            except:
                message = "Please contact IT team"
                result = False

        elif button_pushed == "Sync":
            try:
                selected_templates = form_data.getlist("template")
                # check all the templates if none of the templates has been selected
                if len(selected_templates) == 0:
                    message = sync_templates(all_templates)
                else:
                    message = sync_templates(selected_templates)
                send_notification(message)
                result = True
            except:
                message = "Please contact IT team"
                result = False

        else:
            try:
                message = update_database()
                send_notification(message)
                result = True
            except:
                message = "Please contact IT team"
                result = False

        templates = db.get_templates_from_database()
        all_templates = sorted(templates, key=lambda k: k['name'])
        return render_template("columnPage.html", content=all_templates, success=result, message=message,
                               button=button_pushed)

    return render_template("columnPage.html", content=all_templates)


if __name__ == "__main__":
    app.run(debug=True)
