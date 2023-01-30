import logging
from datetime import datetime

class Subject:
    """
    Subject class, providing an interface to interact with the subjects
    stored inside a Mint Labs project.

    :param project: an instantiated Project
    :type project: Project
    """

    def __init__(self, subject_name):
        assert subject_name != ""
        self._name = subject_name
        # project to which this subject belongs (instance of Project)
        # by default it's empty
        self.project = None
        # the subject has no id, as it doens't belong to a project yet
        self.subject_id = None

        # cache
        self._all_data = None

    @property
    def id(self):
        return self.subject_id

    @property
    def name(self):
        """
        The display name of the subject instanciated.

        :return: The name of the subject
        :rtype: String
        """
        return self._name

    @name.setter
    def name(self, new_subject_name):
        """
        Modify the subject name.

        :param subject_name: new name for the subject.

        :type subject_name: String

        :return: True if the modification was successful, False otherwise.
        :rtype: Bool
        """

        metadata = self.parameters

        post_data = {
                     'patient_id': int(metadata['_id']),
                     'secret_name': new_subject_name,
                     'tags': metadata['tags'] or ""
                    }
        for item in filter(lambda x: x.startswith('md_'), metadata):
            item_newname = item.replace('md_', 'last_vals.')
            post_data[item_newname] = metadata[item] or ""

        answer = self.project._account.send_request(
                                           "patient_manager/upsert_patient",
                                           req_parameters=post_data)

        if not answer.get("success", False):
            logging.error("Could not edit subject name: {}".format(
                                                            answer["error"]))
            return False
        else:
            logging.info("Name updated succesfully: {} is now {}".format(
                                self.name, new_subject_name))
            self._name = new_subject_name
            return True

    @property
    def all_data(self):
        """
        All the data in the platform about the instantiated subject. Including
        uploaded files, analysis etc ...

        :return: All the data
        :rtype: Dict[String] -> x
        """
        return self.get_all_data(cache=False)

    def get_all_data(self, cache=True):
        if not cache or not self._all_data:
            response = self.project._account.send_request(
                            "patient_manager/get_patient_profile_data",
                            req_parameters={
                                "patient_id": self.subject_id,
                                "patient_secret_name": self.name
                            })
            content = response["data"]
            self._all_data = content
        return self._all_data

    @property
    def parameters(self):
        """
        Retrieve all of the the users metadata.

        :return: dictionary of dictionaries:
                 { ssid1: {'parameter_name': 'value', ... }, ssid2: {}, ...}
        :rtype: Dict[String] -> Dict
        """
        return self.get_parameters(cache=False)

    def get_parameters(self, cache=True):
        """
        Retrieve all of the the users metadata.

        :return: dictionary of dictionaries:
                 { ssid1: {'parameter_name': 'value', ... }, ssid2: {}, ...}
        :rtype: Dict[String] -> Dict
        """
        return self.get_all_data(cache)["metadata"]

    def set_parameters(self, ssid, params_dict):
        """
        Set the value of one or more parameters for the current subject.


        :param ssid: an integer indicating which session parameters will be updated.
        :param params_dict: a dictionary with the names of the parameters to
                            set (param_id), and the corresponding values: {'param_id': 'value'}

        :type ssid: Int
        :type params_dict: Dict[String] -> Value

        :return: True if the request was successful, False otherwise.
        :rtype: Bool
        """

        data = self.all_data
        metadata = data["metadata"][str(ssid)]

        post_data = {
                     "ssid": ssid,
                     "patient_id": self.subject_id,
                     "secret_name": self.name,
                     "tags": metadata["tags"] or ""
                    }
        # fill dict with current values
        old_parameters = metadata["metadata"]
        for item in old_parameters:
            if item == "tags":
                continue
            item_newname = "last_vals." + item
            post_data[item_newname] = old_parameters[item] or ""

        # update values
        for param_id, param_value in params_dict.items():
            post_data['last_vals.' + param_id] = param_value

        # fix dates
        # dates are retrieved as: date -> { '$date': 'timestamp' }, but must
        # be sent as date -> 'day.month.year'
        for param_id, param_value in post_data.items():
            if type(param_value) == dict and '$date' in param_value:
                # accept timestamp in milliseconds...
                try:
                    timestamp = int(param_value['$date'])
                    readable_date = datetime.fromtimestamp(timestamp).strftime("%d.%m.%Y")
                # but also in seconds
                except ValueError:
                    timestamp = int(str(param_value['$date'])[:-3])
                    readable_date = datetime.fromtimestamp(timestamp).strftime("%d.%m.%Y")
                post_data[param_id] = readable_date

        answer = self.project._account.send_request(
                                           "patient_manager/upsert_patient",
                                           req_parameters=post_data)

        if not answer.get("success", False):
            logging.error("Could not edit subject parameters: {}".format(
                                                            answer["error"]))
            return False
        else:
            logging.info("Parameters updated succesfully")
            return True

    @property
    def input_containers(self):
        """
        Retrieves a list of conatiners with the reference to the data uploaded
        for that user.

        :return: List of dictionaries with the conatiners info.
        :rtype: List(Dict)
        """
        return self.all_data["containers"]
        # all_containers = self.project.list_input_containers(limit=10000000)
        # result = [a for a in all_containers if
        #                                a["patient_secret_name"] == self._name]
        # for r in result:
        #     del r['patient_secret_name']
        # return result

    @property
    def analysis(self):
        """
        Retrieve all analysis data.

        :return: List of dictionaries with the data of each analysis performed.
        :rtype: List
        """
        all_analysis = self.project.list_analysis(limit=10000000)
        return [a for a in all_analysis if
                                       a["patient_secret_name"] == self._name]

    def upload_mri(self, path):
        """
        Upload mri data to this subject.

        :param path: path to a zip containing the data.
        :type path: String

        :return: True if correctly uploaded, False otherwise.
        :rtype: Bool
        """

        return self.project.upload_mri(path, self.name)

    def upload_gametection(self, path):
        """
        Upload gametection data to this subject.

        :param path: path to a zip containing the data.
        :type path: String

        :return: True if correctly uploaded, False otherwise.
        :rtype: Bool
        """

        return self.project.upload_gametection(path, self.name)

    def upload_result(self, path):
        """
        Upload result data to this subject.

        :param path: path to a zip containing the data.
        :type path: String

        :return: True if correctly uploaded, False otherwise.
        :rtype: Bool
        """

        return self.project.upload_result(path, self.name)
