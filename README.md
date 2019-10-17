# Greendrive
This is a python based project that uses chargepoint API to provides valuable insights and slack alerts to EV drivers

## Prerequisites
Compatible with Python 2.7+

### Zeep
We use [zeep](A modern/fast python SOAP client based on lxml / requests) a python SOAP client:
```
pip install zeep
```

### Slackclient
We use a slack client to automatically post notifications to a Slack channel, so please install the following:
```
pip3 install slackclient
```

## Usage
```python greendrive.py <username> <password> <slack_token>```

## Team
Shivram
Lav
Kate
Ashuka
