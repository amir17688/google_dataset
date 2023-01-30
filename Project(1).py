from .Subject import *
import logging
import hashlib
import time
import os
import json
import sys

def show_progress(done, total, finish=False):
    bytes_in_mb = 1024 * 1024
    progress_message = ' [{:.2f} %] Uploaded {:.2f} of {:.2f} Mb'.format(done/float(total)*100, done/(bytes_in_mb), total/(bytes_in_mb))
    sys.stdout.write(progress_message)
    sys.stdout.flush()
    if not finish:
        sys.stdout.write('\b'*len(progress_message))
        sys.stdout.flush()
    else:
        sys.stdout.write('\n')


def get_session_id(file_path):
    m = hashlib.md5()
    m.update(file_path.encode("utf-8"))
    return str(time.time()).replace(".", "") + "_" + m.hexdigest()


def check_upload_file(file_path):
    """
    Check whether a file has the correct extension to upload.

    :param file_path: path to the file
    :type file_path: String

    :return: True if correct extension, False othersise.
    :rtype: Bool
    """

    # TODO: Add a file zipper here so zips files in a folder

    file_parts = file_path.split(".")
    extension = file_parts[-1]

    if extension != "zip":
        logging.error("You must upload a zip.")
        return False
    else:
        return True


class Project:
    """
    This class is used to work with Mint-Labs projects. The class is instantiated passing as argument a Connection
    object and the id

    :param account: A Mint Labs Account instance
    :type account: mintlabs.Account.Account

    :param project_id: The ID (or name) of the project you want to work with
    :type project_id: Int or string

    """
    def __init__(self, account, project_id):

        # if project_id is a string (the name of the project), get the
        # project id (int)
        if type(project_id) == str:
            project_id = next(filter(lambda proj: proj['name'] == project_id, account.projects))['id']

        self._account = account
        self._project_id = project_id

        # Set the passed project ID as the Active one
        self._set_active(project_id)

        # Cache
        self._subjects_metadata = None

    def _set_active(self, project_id):
        """
        Set the active project.

        :param project_id: Project identifier.
        :rtype project_id: String

        :return: True if the project was correctly set, False otherwise.
        :rtype: Bool
        """

        content = self._account.send_request(
            "projectset_manager/activate_project",
            req_parameters={"project_id": int(project_id)})
        if content.get("success", False):
            logging.info("Successfully changed project")
            self._project_id = project_id
            return True
        else:
            logging.error("Unable to activate the project.")
            return False

    @property
    def subjects_metadata(self):
        """
        List all subject data from the selected project.

        :return: a list of dictionary of {'metadata_name': 'metadata_value'}
        :rtype: Dict
        """
        return self.get_subjects_metadata(cache=False)

    def get_subjects_metadata(self, cache=True):
        """
        List all subject data from the selected project.

        :return: a list of dictionary of {'metadata_name': 'metadata_value'}
        :rtype: Dict
        """

        if not cache or not self._subjects_metadata:
            content = self._account.send_request(
                "patient_manager/get_patient_list",
                req_headers={"X-Range": "items=0-9999"})
            self._subjects_metadata = content
        else:
            content = self._subjects_metadata
        return content

    @property
    def subjects(self):
        """
        Return the list of subject names from the selected projet.

        :return: a list of subject names
        :rtype: List(Strings)
        """

        subjects = self.subjects_metadata
        names = [s["patient_secret_name"] for s in subjects]
        return list(set(names))

    def check_subject_name(self, subject_name):
        """
        Check if a given subject name exists in the selected project.

        :param subject_name: name of the subject to check
        :type subject_name: String

        :return: True if subject name exists in project, False otherwise
        :rtype: Bool
        """

        return subject_name in self.subjects

    @property
    def metadata_parameters(self):
        """
        List all the parameters in the subject metadata.

        Each project has a set of parameters that define the subjects metadata.
        This function returns all this parameters and its properties.

        :return: dictionary {'param_name':
                 { 'order': Int,
                 'tags': [tag1, tag2, ..., ],
                 'title: "Title",
                 'type': "integer|string|date|list|decimal",
                 'visible': 0|1
                 }}

        :rtype: Dict["String"] -> Dict["String"] -> x
        """

        content = self._account.send_request("patient_manager/module_config")

        if not content.get("success", False) or not content.get("data", False):
            logging.error("Could not retrieve metadata parameters.")
            return None
        else:
            return content["data"]["fields"]

    def add_metadata_parameter(self, title, param_id=None, param_type="string", visible=False):
        """
        Add a metadata parameer to the project.

        :param title: identificator of this new parameter
        :param param_id: title of this new parameter
        :param param_type: type of the parameter. One of:
                           "integer", "date", "string", "list", "decimal"
        :param visible: whether the parameter will be visible in the table
                        of patients.

        :type title: String
        :type param_id: String
        :type param_type: String
        :type visible: Bool

        :return: True if parameter was correctly added, False otherwise.
        :rtype: Bool.
        """
        # use param_id equal to title if param_id is not provided
        param_id = param_id or title

        param_properties = [title, param_id, param_type, str(int(visible))]

        post_data = {"add": "|".join(param_properties),
                     "edit": "",
                     "delete": ""
                    }

        answer = self._account.send_request(
                                        "patient_manager/save_metadata_changes",
                                        req_parameters=post_data)
        if not answer.get("success", False) or not title in answer.get("data", {}):
            logging.error("Could not add new parameter: {}".format(title))
            return False
        else:
            logging.info("New parameter added:", title, param_properties)
            return True

    def list_analysis(self, limit=10000000):
        """
        List the analysis available to the user.

        :param limit: max number of results
        :type limit: Int

        :return: List of analysis, each a dictionary
        :rtype: Dict
        """
        req_headers = {"X-Range":"items=0-" + str(limit - 1)}
        return self._account.send_request("analysis_manager/get_analysis_list",
                                            req_headers=req_headers)

    def list_input_containers(self, search_condition="*", limit=1000):
        """
        List the containers available to the user.

        :param search_condition: search string
        :param limit: max number of results

        :type search_condition: String
        :type limit: Int

        :return: List of containers, each a dictionary
                 {"name": "container-name", "id": "container_id"}
        :rtype: Dict
        """

        req_headers = {"X-Range": "items=0-" + str(limit - 1)}
        content = self._account.send_request("file_manager/get_container_list",
                                               req_parameters=search_condition,
                                               req_headers=req_headers)
        containers = [{"patient_secret_name": c["patient_secret_name"], "container_name": c["name"], "container_id": c["_id"]} for c in content]
        return containers

    def list_result_containers(self, limit=1000):
        """
        List the result containers available to the user.

        :param search_condition: search string
        :param limit: max number of results

        :type search_condition: String
        :type limit: Int

        :return: List of containers, each a dictionary
                 {"name": "container-name", "id": "container_id"}
        :rtype: Dict
        """
        analysis = self.list_analysis(limit)
        return [{"name": a["name"], "id": a["out_container_id"]} for a in analysis]

    def list_container_files(self, container_id):
        """
        List the name of the files available inside a given container.

        :param container_id: Container identifier.
        :type container_id: String

        :return: List of file names (strings)
        :rtype: List(Strings)
        """

        content = self._account.send_request("file_manager/get_container_files",
                                    req_parameters={"container_id": container_id})

        if not content.get("success", False) or not content.get("data", False):
            return False
        elif content["data"].get("files", False):
            return content["data"]["files"]
        else:
            logging.error("Could not get files")
            return False

    def list_container_files_metadata(self, container_id):
        """
        List all the metadata of the files available inside a given container.

        :param container_id: Container identifier.
        :type container_id: String

        :return: Dictionary of {'metadata_name': 'metadata_value'}
        :rtype: Dict
        """

        content = self._account.send_request(
                                  "file_manager/get_container_files",
                                  req_parameters={"container_id": container_id})

        if content.get("success", False):
            return content["data"]["meta"]
        else:
            error = content["error"]
            logging.error(error)
            return False

    def get_file_metadata(self, container_id, filename):
        """
        Retrieve the metadata from a particular file in a particular container.

        :param container_id: Container identifier.
        :type container_id: String
        :param filename: Name of the file.
        :type filename: String

        :return: Dictionary with the metadata.
        :rtype: Dict
        """
        all_metadata = self.list_container_files_metadata(container_id)
        for file_meta in all_metadata:
            if file_meta["name"] == filename:
                return file_meta

    def download_file(self, container_id, file_name, local_filename=False,
                      overwrite=False):
        """
        Download a single file from a  specific container.

        :param container_id: id of the container inside which the file is.
        :param file_name: name of the file in the container.
        :param local_filename: name of the file to be created. By default, the
                               same as file_name.
        :param overwrite: whether or not to overwrite the file if existing.

        :type container_id: Int
        :type file_name: String
        :type local_filename: String
        :type overwrite: Bool
        """

        local_filename = local_filename or file_name

        if os.path.exists(local_filename) and not overwrite:
            msg = "File '{}' already exists".format(local_filename)
            logging.error(msg)
            return False

        params = {"container_id":container_id, "files":file_name}
        content = self._account.send_request("file_manager/download_file",
                                               params, stream=True,
                                               return_raw_response=True)

        with open(local_filename, 'wb') as f:
            for chunk in content.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
        logging.info("File {} from container {} saved to {}".format(file_name,
                                                container_id, local_filename))
        return True

    def download_files(self, container_id, filenames, zip_name="files.zip",
                       overwrite=False):
        """
        Download a set of files from a given container.

        :param container_id: id of the container inside which the file is.
        :param filenames: list of files to download.
        :param overwrite: whether or not to overwrite the file if existing.
        :param local_filenames: list of filenames to save the files locally.

        :type container_id: Int
        :type filenames: List (Strings)
        :type overwrite: Bool
        :type local_filenames: List (Strings)
        """

        return self.download_file(container_id, ";".join(filenames),
                                  zip_name, overwrite)

    def get_subject_id(self, subject_name, cache=False):
        """
        Given a subject name, return its id in the project.
        :param subject_name: name of the subject in the project.
        :type subject_name: String

        :return: the id of the subject in the project, or False if
                 the subject is not found.
        :rtype: Int or Bool (on failure)
        """

        for user in self.get_subjects_metadata(cache):
            if user["patient_secret_name"] == subject_name:
                return int(user["_id"])
        return False

    def get_subject(self, subject_name, cache=True):
        """
        Return a subject object, representing a subject from the project.

        :param subject_name: name of the subject.
        :type subject_name: String

        :return: a Subject instance representing the desired subject, or
                 False if the subject wasn't found
        :rtype: Subject or Bool
        """
        subject_id = self.get_subject_id(subject_name, cache=cache)
        if subject_id is False:
            return False
        subj = Subject(subject_name)
        subj.subject_id = subject_id
        subj.project = self
        return subj

    def add_subject(self, subject):
        """
        Add a subject to the project.

        :param subject: instance of Subject representing the subject to add.
        :type subject: Subject

        :return: True if correctly added, False otherwise
        :rtype: Bool
        """
        if self.check_subject_name(subject.name):
            logging.error("Subject with name {} already exists in project!".format(subject.name))
            return False

        content = self._account.send_request("patient_manager/upsert_patient",
                                   req_parameters={"secret_name": subject.name})
        if content.get("success", False):
            subject.subject_id = self.get_subject_id(subject.name)
            subject.project = self
            logging.info("Subject {0} was successfully created".format(subject.name))
            return True
        else:
            logging.error("Subject {} could not be created.".format(subject.name))
            return False

    def delete_subject(self, subject_name):
        """
        Delete a subject from the project.

        :param subject_name: name of the subject to be deleted.
        :type subject_name: String

        :return: True if correctly delted, False otherwise.
        :rtype: Bool
        """
        if not self.check_subject_name(subject_name):
            logging.error("Attempt to delete an inexisting subject: '{}'.".format(subject_name))
            return False
        subject_id = self.get_subject_id(subject_name)
        content = self._account.send_request("patient_manager/delete_patient",
                                              req_parameters={"patient_id": subject_id})
        if content.get("success", False):
            logging.info("Subject '{}' successfully deleted.".format(subject_name))
            return True
        else:
            logging.error("Subject '{}' could not be deleted.".format(subject_name))
            return False


    def upload_file(self, file_path, subject_name, date_of_scan="", description="",
                     result=False, name="", input_data_type="mri_brain_data",
                     container_id=0, add_to_container_id=0):
        """
        Upload a file to the platform, associated with the current user.

        :param file_path: path to the file to upload.
        :param subject_name: subject to which this file will belong
        :param date_of_scan: date of scan/creation of the file
        :param description: description of the file
        :param result: is this file a result? ie, the product of a previous
                       analysis?
        :param name: name of the file in the platform
        :param input_data_type: mri_brain_data or GAMETECTION
        :param container_id: ??
        :param add_to_container_id: id of the container to which this file
                                    should be added (if id > 0)

        :type file_path: String
        :type subject_name: String
        :type date_of_scan: String
        :type description: String
        :type result: String
        :type name: String
        :type input_data_type: String
        :type container_id: Int
        :type add_to_container_id: Int

        :return: True if correctly uploaded, False otherwise
        :rtype: Bool
        """

        chunk_size = 256 * 1024
        max_retries = 10

        file_name = os.path.split(file_path)[1]
        name = name or os.path.split(file_path)[1]

        total_bytes = os.path.getsize(file_path)

        # making chunks of the file and sending one by one
        with open(file_path, 'rb') as file_object:

            file_size = os.path.getsize(file_path)
            uploaded = 0
            session_id = get_session_id(file_path)
            chunk_num = 0
            retries_count = 0
            error_message = ""
            uploaded_bytes = 0
            response = None

            while True:
                data = file_object.read(chunk_size)
                if not data:
                    break

                start_position = chunk_num * chunk_size
                end_position = start_position + chunk_size - 1
                bytes_to_send = chunk_size

                if end_position >= total_bytes:
                    end_position = total_bytes - 1
                    bytes_to_send = total_bytes - uploaded_bytes

                bytes_range = "bytes " + str(start_position) + "-" + str(end_position) + "/" + str(total_bytes)

                request_headers = {}

                request_headers["Content-Type"] = "application/zip"
                request_headers["Content-Range"] = bytes_range
                request_headers["Session-ID"] = session_id
                request_headers["Content-Length"] = bytes_to_send
                request_headers["Content-Disposition"] = 'attachment; filename="' + file_name + '"'

                # if it is the last chunk, define more header fields
                if uploaded_bytes + bytes_to_send == total_bytes:
                    request_headers["X-Mint-Name"] = name
                    request_headers["X-Mint-Date"] = date_of_scan
                    request_headers["X-Mint-Description"] = description
                    request_headers["X-Mint-Patient-Secret"] =subject_name

                    if input_data_type:
                        request_headers["X-Mint-Type"] = input_data_type

                    if result:
                        request_headers["X-Mint-In-Out"] = "result"
                        if container_id > 0:
                            request_headers["X-Mint-Container-Id"] = container_id
                    else:
                        request_headers["X-Mint-In-Out"] = "in"

                    if add_to_container_id > 0:
                        request_headers["X-Mint-Add-To"] = add_to_container_id

                    request_headers["X-Requested-With"] = "XMLHttpRequest"

                # print req_headers
                # prepare all the needed data in the request
                response = self._account.send_request("upload",
                                         req_parameters=data,
                                         req_headers=request_headers,
                                         return_raw_response=True)

                if response is None:
                    retries_count += 1
                    time.sleep(retries_count * 5)
                    if retries_count > max_retries:
                        error_message = "HTTP Connection Problem"
                        break
                elif int(response.status_code) == 201:
                    chunk_num += 1
                    retries_count = 0
                    uploaded_bytes += chunk_size
                elif int(response.status_code) == 200:
                    retries_count = 0
                    show_progress(file_size, file_size, finish=True)
                    break
                elif int(response.status_code) == 416:
                    retries_count += 1
                    time.sleep(retries_count * 5)
                    if retries_count > self.max_retries:
                        error_message = "Error Code: 416; Requested Range Not Satisfiable (NGINX)"
                        break
                else:
                    retries_count += 1
                    time.sleep(retries_count * 5)
                    if retries_count > max_retries:
                        error_message = "Number of retries has been reached. Upload process stops here !"
                        break

                uploaded += chunk_size
                show_progress(uploaded, file_size)

        if len(error_message) == 0:

            if not result:
                # send back what is needed

                response = json.loads(response.text)

                if response["success"] == 1 and response["need_confirmation"] == 0:
                    return True

                mappings = response["data"]
                container_id = response["container_id"]
                mappings_to_send = []

                for m in mappings:
                    mappings_to_send.append(m[0] + "," + m[1] + "," + m[2] + ",")

                if len(mappings_to_send) > 0:
                    txt_mappings = ";".join(mappings_to_send)
                    logging.info("Confirming upload. This might take some time, depending on file size...")
                    response_2 = self._account.send_request(
                            "file_manager/confirm_uploaded_files",
                            req_parameters={"container_id":container_id,
                                            "mappings":txt_mappings})

                    if response_2["success"] == 1:
                        logging.info("Your data was successfully uploaded.")
                        return True
                    else:
                        logging.error("Error: {0}".format(response_2["error"]))
                        return False
                else:
                    logging.error("Unrecognized sets.")
                    return False
            else:
                return True
        else:
            logging.error(error_message)
            return False

    def upload_mri(self, file_path, subject_name):
        """
        Upload new MRI data to the subject.

        :param file_path: Path to the file to upload
        :type file_path: String

        :return: True if upload was correctly done, False otherwise.
        :rtype: bool
        """

        if check_upload_file(file_path):
            return self.upload_file(file_path, subject_name)

    def upload_gametection(self, file_path, subject_name):
        """
        Upload new Gametection data to the subject.

        :param file_path: Path to the file to upload
        :type file_path: String

        :return: True if upload was correctly done, False otherwise.
        :rtype: bool
        """

        if check_upload_file(file_path):
            return self.upload_file(file_path, subject_name, input_data_type="parkinson_gametection")
        return False

    def upload_result(self, file_path, subject_name):
        """
        Upload new result data to the subject.

        :param file_path: Path to the file to upload
        :type file_path: String

        :return: True if upload was correctly done, False otherwise.
        :rtype: bool
        """

        if check_upload_file(file_path):
            return self.upload_file(file_path, subject_name, result=True)
        return False

    def copy_container_to_project(self, container_id, project_id):
        """
        Copy a container to another project.

        :param container_id: id of the container to copy.
        :type container_id: Int

        :param project_id: id of the project to retireve, either the numeric
                           id or the name
        :type project_id: Int | String

        :return: True on success, False on fail
        :rtype: Bool
        """

        if type(project_id) == int or type(project_id) == float:
            p_id = int(project_id)
        elif type(project_id) == str:
            projects = self._account.projects
            projects_match = [proj for proj in projects if proj['name'] == project_id]
            if not projects_match:
                raise Exception("Project {} does not exist or is not available for this user.".format(project_id))
            p_id = int(projects_match[0]["id"])
        data = {
                "container_id": container_id,
                "project_id": p_id
                }
        content = self._account.send_request("file_manager/copy_container_to_another_project", req_parameters=data)
        if content.get("success", False):
            return True
        else:
            logging.error(content.get("error", "Error: couldn't copy container."))
            return False

    def start_analysis(self, script_name, in_container_id, analysis_name=None,
                       analysis_description=None):
        """
        Starts an analysis on a subject.

        :param script_name: name of the script to be run. One of: 'volumetry',
                            'parkinson_gametection', 'morphology',
                            'morphology_new', '3d_wires', 'dti_fa_files',
                            '2d_wires' or 'morphology_infant'.
        :type script_name: String

        :param in_container_id: The id of the container to get the data from.
        :type in_container_id: Int

        :param analysis_name: name of the analysis (optional)
        :type analysis_name: String

        :param analysis_description: description of the analysis (optional)
        :type analysis_description: String

        :return: True if correctly started, False otherwise.
        :rtype: Bool
        """

        post_data = {
            "script_name": script_name,
            "in_container_id": in_container_id,
        }
        # name and description are optional
        if analysis_name:
            post_data["name"] = analysis_name
        if analysis_description:
            post_data["description"] = analysis_description
        post_data["input_type"] = script_name
        response = self._account.send_request(
                     "analysis_manager/analysis_registration",
                     req_parameters=post_data)
        if not response.get("success", False):
            logging.error("Unable to start the analysis.")
            return False
        if "has_to_ask" in response:
            proj_id = response["project_id"]
            files = response["files"]
            modalities = self.__get_modalities(files)
            files_info = []
            # choose the largest file for each modality
            for modality in modalities:
                files_mod = [f for f in files if f["metadata"]["modality"] == modality]
                # sort files by size (sort in python > 2.2 is stable)
                files_mod = sorted(files_mod, key=lambda f: f["size"], reverse=True)
                file_ = files_mod[0]
                filename = file_["name"]
                files_info.append("{};{}".format(modality, filename))
            post_data["c_files"] = "|".join(files_info)
            post_data["project_id"] = proj_id
            response = self._account.send_request(
                        "analysis_manager/analysis_registration",
                        req_parameters=post_data)
            if not response.get("success", False):
                logging.error("Unable to start the analysis.")
                return False
            else:
                return True

    def __get_modalities(self, files):
        modalities = []
        for file_ in files:
            modality = file_["metadata"]["modality"]
            if modality not in modalities:
                modalities.append(modality)
        return modalities
