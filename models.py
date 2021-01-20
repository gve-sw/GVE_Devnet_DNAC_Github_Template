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

import base64
import json
from datetime import datetime

import requests
import urllib3
from pymongo import MongoClient
from requests.auth import HTTPBasicAuth


class Github(object):

    def __init__(self, token, base_url):
        self.token = token
        self.base_url = base_url
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def __github_headers(self):
        return {'Authorization': 'Bearer {0}'.format(self.token), 'Content-Type': 'application/json'}

    def __create_file(self, url, data):
        r = requests.put(url, headers=self.__github_headers(),
                         json={"message": "Create file from flask app",
                               "content": base64.b64encode(data.encode()).decode(),
                               "branch": "development"})
        if r.status_code == 201:
            return r.json()
        else:
            raise Exception(r.status_code)

    def get_github_file_content(self, project_name, template_name):
        url = "{0}/contents/{1}/{2}".format(self.base_url, project_name, template_name)
        r = requests.get(url, headers=self.__github_headers())
        if r.status_code == 200:
            encoded_content = r.json()["content"]
            content = base64.b64decode(encoded_content).decode()
            return content
        else:
            raise Exception(r.status_code)

    def add_template_github(self, template_content, template_name, project_name):
        data = template_content
        url = "{0}/contents/{1}/{2}".format(self.base_url, project_name, template_name)
        r = requests.get(url, headers=self.__github_headers())
        if r.status_code == 200:
            print("Template already exists")
        else:
            print("Will create the file in github")
            self.__create_file(url, data)

    def create_new_branch(self, master_branch, new_branch):
        # Creates a new branch if the new_branch does not exist
        url = "{0}/git/refs/heads/{1}".format(self.base_url, master_branch)
        r = requests.get(url, headers=self.__github_headers())
        if r.status_code == 200:
            sha = r.json()["object"]["sha"]
            url = "{0}/git/refs".format(self.base_url, master_branch)
            r = requests.post(url, headers=self.__github_headers(),
                              json={"ref": "refs/heads/{0}".format(new_branch), "sha": sha})
            if r.status_code == 201:
                return r.json()
            else:
                return r.status_code
        else:
            raise Exception(r.status_code)

    def update_branch(self, template_content, template_name, project_name, branch):
        url = "{0}/contents/{1}/{2}?ref={3}".format(self.base_url, project_name, template_name, branch)
        r = requests.get(url, headers=self.__github_headers())
        try:
            sha = r.json()["sha"]

            url = "{0}/contents/{1}/{2}?ref={3}".format(self.base_url, project_name, template_name, branch)
            payload = {"message": "update from flask app",
                       "content": base64.b64encode(template_content.encode()).decode(),
                       "sha": sha, "branch": branch}
            r = requests.put(url, headers=self.__github_headers(), data=json.dumps(payload))
            if r.status_code == 200:
                return r.json()
            else:
                return r.status_code
        except:
            return r.status_code

    def create_pull_request(self, head, base):
        url = "{0}/pulls".format(self.base_url)
        data = {"head": head, "base": base, "title": "Pull request from flask app"}
        r = requests.post(url, headers=self.__github_headers(), json=data)
        if r.status_code == 201:
            return r.json()
        else:
            return r.status_code


class LocalDatabase(object):

    def __init__(self, cluster, database, collection):
        self.cluster = MongoClient(database)
        self.database = self.cluster[cluster]
        self.collection = self.database[collection]

    def __create_entry(self, template):
        template['inGitHub'] = False
        template['inLab'] = "NOT in Github"
        template['inProd'] = "NOT in Github"
        template['createDate'] = datetime.now().strftime('%H:%M %m-%d-%Y')
        self.collection.insert_one(template)

    def get_templates_from_database(self):
        templates = list(self.collection.find())
        return templates

    def update_db(self, name, new_value):
        self.collection.update_one({'name': name}, {"$set": new_value}, upsert=False)
        return 200, "Database has been updated"

    def update_database(self, template_name, project_name, device_family, software_type):
        template = {"name": template_name, "projectName": project_name,
                    "deviceFamily": device_family, "softwareType": software_type}
        if self.collection.count_documents({"name": template_name}) != 0:
            print("Already inside database")
            return {"update": False, "template": template_name}
        else:
            print("New entry will be created")
            self.__create_entry(template)
            return {"update": True, "template": template_name}


class DNACenter(object):

    def __init__(self, username, password, base_url, name):
        self.username = username
        self.password = password
        self.base_url = base_url
        self.name = name  # LAB OR PROD

        self.__auth_token = self.__get_auth_token()

    def __get_auth_token(self):
        url = '{0}/dna/system/api/v1/auth/token'.format(self.base_url)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        r = requests.post(url, auth=HTTPBasicAuth(self.username, self.password), verify=False)
        if r.status_code == 200:
            response = r.json()
            return response['Token']
        else:
            raise Exception(r.status_code)

    def __dna_headers(self):
        return {'Content-Type': 'application/json', 'x-auth-token': self.__auth_token}

    def __get_template_projects(self, project_name):
        url = '%s/dna/intent/api/v1/template-programmer/project' % (self.base_url)
        r = requests.get(url, headers=self.__dna_headers(), verify=False)
        if r.status_code == 200 or 202:
            for project in r.json():
                if project_name == project['name']:
                    return project['id']
        else:
            return False

    def __create_template_data_ip(self, template_name, content, project_name, device_family, software_type):
        data = {
            "author": "Automated Template",
            "description": "this template was automated",
            "failurePolicy": "ABORT_ON_ERROR",
            "name": template_name,
            "projectName": project_name,
            "templateContent": content,
            "softwareType": software_type,
            "deviceTypes": [
                {
                    "productFamily": device_family
                }
            ],
            "templateParams": [],
            'version': '1',
        }
        return data, "%s Automated Template" % template_name

    def __update_template_data_ip(self, template_name, content, project_name, device_family, software_type, project_id,
                                  template_id):
        data = {
            "author": "Automated Template",
            "description": "this template was updated from flask application",
            "failurePolicy": "ABORT_ON_ERROR",
            "name": template_name,
            "id": template_id,
            "projectName": project_name,
            "projectId": project_id,
            "templateContent": content,
            "softwareType": software_type,
            "deviceTypes": [
                {
                    "productFamily": device_family
                }
            ],
            "templateParams": [],
            'version': '1',
        }
        return data, "%s Automated Template" % template_name

    def __create_project_data(self, project_name):
        data = {
            "description": "this template was updated from flask application",
            "name": project_name,
            "tags": [],
        }
        return data, "%s Automated Project" % project_name

    def create_template(self, template_name, template_content, project_name, device_family, software_type):
        print("--Inside Create Template--")
        project_id = self.__get_template_projects(project_name=project_name)
        if project_id is None:
            # Create the project if it does not exists in the dna center prod
            url = '%s/dna/intent/api/v1/template-programmer/project' % self.base_url
            payload = self.__create_project_data(project_name)
            r = requests.post(url, headers=self.__dna_headers(), verify=False, data=json.dumps(payload[0]))
            project_id = self.__get_template_projects(project_name=project_name)

        device_family = device_family[0]["productFamily"]
        payload = self.__create_template_data_ip(template_name, template_content, project_name, device_family,
                                                 software_type)
        r = requests.post('%s/dna/intent/api/v1/template-programmer/project/%s/template' % (
            self.base_url, project_id), headers=self.__dna_headers(), verify=False, data=json.dumps(payload[0]))
        if r.status_code == 200 or 202:
            return r.json()
        else:
            return False

    def get_templates(self):
        url = "{0}/dna/intent/api/v1/template-programmer/template".format(self.base_url)
        r = requests.get(url, headers=self.__dna_headers(), auth=HTTPBasicAuth(self.username, self.password),
                         verify=False)
        if r.status_code == 200:
            return r.json()
        else:
            raise Exception(r.status_code)

    def get_template_details(self, template_id):
        url = "{0}/dna/intent/api/v1/template-programmer/template/{1}".format(self.base_url, template_id)
        r = requests.get(url, headers=self.__dna_headers(), verify=False)
        if r.status_code == 200 or 202:
            return r.json()
        else:
            raise Exception(r.status_code)

    def get_template_content_by_name(self, project_name, template_name):
        project_id = self.__get_template_projects(project_name=project_name)
        url = "{0}/dna/intent/api/v1/template-programmer/template?projectId={1}".format(self.base_url, project_id)
        r = requests.get(url, headers=self.__dna_headers(), auth=HTTPBasicAuth(self.username, self.password),
                         verify=False)
        if r.status_code == 200 or 202:
            projects = r.json()
            for p in projects:
                if p["name"] == template_name:
                    templateId = p["templateId"]
                    try:
                        content = self.get_template_details(templateId)["templateContent"]
                    except:
                        content = ""
                    return content
            return 404
        else:
            return 404

    def update_template(self, template_name, template_content, project_name, device_family, software_type):
        project_id = self.__get_template_projects(project_name=project_name)
        device_family = device_family[0]["productFamily"]
        url = "{0}/dna/intent/api/v1/template-programmer/template?projectId={1}".format(self.base_url, project_id)
        r = requests.get(url, headers=self.__dna_headers(), auth=HTTPBasicAuth(self.username, self.password),
                         verify=False)
        if r.status_code == 200 or 202:
            projects = r.json()
            for p in projects:
                if p["name"] == template_name:
                    template_id = p["templateId"]
                    payload = self.__update_template_data_ip(template_name, template_content, project_name,
                                                             device_family, software_type, project_id, template_id)
        r = requests.request("PUT", '%s/dna/intent/api/v1/template-programmer/template' % (
            self.base_url), headers=self.__dna_headers(), verify=False, data=json.dumps(payload[0]))
        if r.status_code == 200 or 202:
            return r.json()
        else:
            return False
