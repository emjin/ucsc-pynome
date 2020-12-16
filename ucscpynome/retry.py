import requests
import time


class NetworkError(ValueError):
    pass

class Requests():
    """
        Constructs a new Requests instance 
        Client should not call this class!

        Methods here sets the timeout and retries for the Request object

        Raises:
            NetworkError: raised if a connection issue occurs during the API request
    """
    def __init__(self, timeout=600, retries = 2):
        """ 
            Creates an instance of a Request. Client should not call use this constructor!

            Args:
                timeout (int): timeout duration in seconds
                retries (int): number of retries
        """

        self.timeout = timeout
        self.retries = retries

    def get(self, url):
        """
            Sends a GET request to the specified url with self.retries number of
            retries and self.timeout duration

            Args:
                url (string): url to send a GET request to

            Raises:
                NetworkError
        """
        request_exceptions = (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError
        )
        for i in range(self.retries):
            try:
                result = requests.get(url, timeout=self.timeout)
            except request_exceptions:
                continue
            else:
                return result
        else:
            raise NetworkError("GET Request timed out at " + str(self.timeout) + " seconds") 

    
    def set_timeout(self, timeout):
        """
            Sets the timeout for the Request object

            Args:
                timeout (int): timeout duration in seconds
        """
        self.timeout = timeout

    def set_retries(self, retry):
        """
            Sets the number of retries for the Request object

            Args:
                retry (int): number of retries 
        """
        self.retries = retry



