# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json

import tornado
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join

from .job_data import JobDataLoader
from .vdk_options.vdk_options import VdkOption
from .vdk_ui import VdkUI


class LoadJobDataHandler(APIHandler):
    """
    Class responsible for handling POST request for retrieving data(full path, job's name and team)
     about job of directory
     Response: return a json formatted str providing the data about the job
    """

    @tornado.web.authenticated
    def post(self):
        working_directory = json.loads(self.get_json_body())[VdkOption.PATH.value]
        data = JobDataLoader(working_directory)
        self.finish(
            json.dumps(
                {
                    VdkOption.PATH.value: data.get_job_path(),
                    VdkOption.NAME.value: data.get_job_name(),
                    VdkOption.TEAM.value: data.get_team_name(),
                }
            )
        )


class RunJobHandler(APIHandler):
    """
    Class responsible for handling POST request for running a Data Job given its path and arguments to run with
    Response: return a json formatted str including:
     ::error field with error message if an error exists
     ::message field with status of the VDK operation
    """

    @tornado.web.authenticated
    def post(self):
        input_data = self.get_json_body()
        run_result = VdkUI.run_job(
            input_data[VdkOption.PATH.value],
            input_data[VdkOption.ARGUMENTS.value],
        )
        self.finish(json.dumps(run_result))


class DeleteJobHandler(APIHandler):
    """
    Class responsible for handling POST request for deleting a Data Job given its name, team and Rest API URL
    Response: return a json formatted str including:
        ::error field with error message if an error exists
        ::message field with status of the Vdk operation
    """

    @tornado.web.authenticated
    def post(self):
        input_data = self.get_json_body()
        try:
            status = VdkUI.delete_job(
                input_data[VdkOption.NAME.value],
                input_data[VdkOption.TEAM.value],
                input_data[VdkOption.REST_API_URL.value],
            )
            self.finish(json.dumps({"message": f"{status}", "error": ""}))
        except Exception as e:
            self.finish(json.dumps({"message": f"{e}", "error": "true"}))


class DownloadJobHandler(APIHandler):
    """
    Class responsible for handling POST request for downloading a Data Job given its name, team,
    Rest API URL, and the path to where the job will be downloaded
    Response: return a json formatted str including:
        ::error field with error message if an error exists
        ::message field with status of the Vdk operation
    """

    @tornado.web.authenticated
    def post(self):
        input_data = self.get_json_body()
        try:
            status = VdkUI.download_job(
                input_data[VdkOption.NAME.value],
                input_data[VdkOption.TEAM.value],
                input_data[VdkOption.REST_API_URL.value],
                input_data[VdkOption.PATH.value],
            )
            self.finish(json.dumps({"message": f"{status}", "error": ""}))
        except Exception as e:
            self.finish(json.dumps({"message": f"{e}", "error": "true"}))


class CreateJobHandler(APIHandler):
    """
    Class responsible for handling POST request for creating a Data Job given its name, team,
    flags whether it will be created locally or in the cloud, path to where job will be created (if local),
    Rest API URL (if cloud)
    Response: return a json formatted str including:
        ::error field with error message if an error exists
        ::message field with status of the Vdk operation
    """

    @tornado.web.authenticated
    def post(self):
        input_data = self.get_json_body()
        try:
            status = VdkUI.create_job(
                input_data[VdkOption.NAME.value],
                input_data[VdkOption.TEAM.value],
                input_data[VdkOption.REST_API_URL.value],
                input_data[VdkOption.PATH.value],
                bool(input_data[VdkOption.LOCAL.value]),
                bool(input_data[VdkOption.CLOUD.value]),
            )
            self.finish(json.dumps({"message": f"{status}", "error": ""}))
        except Exception as e:
            self.finish(json.dumps({"message": f"{e}", "error": "true"}))


class CreateDeploymentHandler(APIHandler):
    """
    Class responsible for handling POST request for creating a deployment of  Data Job given its name, team, path,
    Rest API URL, deployment reason and flag whether it is enabled (that will basically un-pause the job)
    Response: return a json formatted str including:
        ::error field with error message if an error exists
        ::message field with status of the Vdk operation
    """

    @tornado.web.authenticated
    def post(self):
        input_data = self.get_json_body()
        try:
            status = VdkUI.create_deployment(
                input_data[VdkOption.NAME.value],
                input_data[VdkOption.TEAM.value],
                input_data[VdkOption.REST_API_URL.value],
                input_data[VdkOption.PATH.value],
                input_data[VdkOption.DEPLOYMENT_REASON.value],
                input_data[VdkOption.DEPLOY_ENABLE.value],
            )
            self.finish(json.dumps({"message": f"{status}", "error": ""}))
        except Exception as e:
            self.finish(json.dumps({"message": f"{e}", "error": "true"}))


def setup_handlers(web_app):
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]

    def add_handler(handler, endpoint):
        job_route_pattern = url_path_join(
            base_url, "vdk-jupyterlab-extension", endpoint
        )
        job_handlers = [(job_route_pattern, handler)]
        web_app.add_handlers(host_pattern, job_handlers)

    add_handler(RunJobHandler, "run")
    add_handler(DeleteJobHandler, "delete")
    add_handler(DownloadJobHandler, "download")
    add_handler(CreateJobHandler, "create")
    add_handler(LoadJobDataHandler, "job")
    add_handler(CreateDeploymentHandler, "deploy")
