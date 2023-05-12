import sys
import getpass
import xmltodict
import argparse
import requests
import json

def my_quit(exit_code: int, error_message: str = None):
    if error_message is not None:
        print(error_message)
    sys.exit(exit_code)


def get_asset_groups(session: requests.Session, baseurl: str, debug: bool = False):
    # Get the asset groups
    url = '%s/api/2.0/fo/asset/group?action=list&show_attributes=BUSINESS_IMPACT,TITLE' % baseurl
    response = session.request(method='GET', url=url, allow_redirects=False)
    if response.status_code == 200:
        if debug:
            print('Response Code : %d' % response.status_code)
            print('Response Headers : \n%s' % response.headers)
            print('Response Text : \n%s' % response.text)
        # Convert the resulting XML into a dictionary for easier processing and return it to the caller
        return xmltodict.parse(response.text)

    redirect_url = session.get_redirect_target(response)
    if redirect_url is None or redirect_url == '':
        my_quit(2, 'FATAL: Could not make API call to get Asset Group data')

    response = session.request(method='GET', url=redirect_url, allow_redirects=False)
    if response.status_code == 200:
        if debug:
            print('Response Code : %d' % response.status_code)
            print('Response Headers : \n%s' % response.headers)
            print('Response Text : \n%s' % response.text)
        return xmltodict.parse(response.text)
    else:
        my_quit(3, 'FATAL: Could not make API call to get Asset Group data following redirect')


def update_asset_group(session: requests.Session, asset_group_id: str, baseurl: str, debug: bool = False):
    # Send the edit to the subscription
    url = '%s/api/2.0/fo/asset/group?action=edit&id=%s&set_business_impact=Minor' % (baseurl, asset_group_id)
    response = session.request(method='POST', url=url, allow_redirects=False)
    if response.status_code == 200:
        if debug:
            print('Response Code : %d' % response.status_code)
            print('Response Headers : \n%s' % response.headers)
            print('Response Text : \n%s' % response.text)
        return xmltodict.parse(response.text)

    redirect_url = session.get_redirect_target(response)
    if redirect_url is None or redirect_url == '':
        my_quit(2, 'FATAL: Could not make API call to update Asset Group')

    response = session.request(method='POST', url=redirect_url, allow_redirects=False)
    if response.status_code == 200:
        if debug:
            print('Response Code : %d' % response.status_code)
            print('Response Headers : \n%s' % response.headers)
            print('Response Text : \n%s' % response.text)
        return xmltodict.parse(response.text)
    else:
        if debug:
            print('Response Code : %d' % response.status_code)
            print('Response Headers : \n%s' % response.headers)
            print('Response Text : \n%s' % response.text)
        my_quit(3, 'FATAL: Could not make API call to update Asset Group following redirect')


# Script entry point
if __name__ == "__main__":
    # argparse is the command line argument parser, we create one here then add arguments to it
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user', help='Qualys Username')
    parser.add_argument('-p', '--password', help='Qualys Password (use - for interactive input')
    parser.add_argument('-a', '--api_url', help='Qualys API URL (e.g. https://qualysapi.qualys.eu)')
    parser.add_argument('-P', '--proxy_enable', action='store_true', help='Enable HTTPS proxy for outgoing connection')
    parser.add_argument('-U', '--proxy_url', help='HTTPS Proxy address')
    parser.add_argument('-s', '--simulate', action='store_true', help='Simulation mode, do not make changes')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug output for API calls')

    # Process the added arguments
    args = parser.parse_args()

    # Validate the passed arguments
    if args.user is None or args.user == '':
        my_quit(1, 'ERROR: User Not Specified')

    if args.password is None or args.user == '':
        my_quit(1, 'ERROR: Password Not Specified')

    if args.api_url is None or args.api_url == '':
        my_quit(1, 'ERROR: API URL Not Specified')

    if args.proxy_enable and (args.proxy_url is None or args.proxy_url == ''):
        my_quit(1, 'ERROR: Proxy enabled but no proxy address specified')

    # If the user passes '-' as the password, get it interactively using the getpass library
    password = ''
    if args.password == '-':
        password = getpass.getpass(prompt='Enter password for user %s : ' % args.user)
    else:
        password = args.password

    # Create a requests.Session object which will store the username, password, proxy url and headers for the requests
    session = requests.Session()
    session.auth = (args.user, password)
    session.headers['X-Requested-With'] = 'python3/requests'

    if args.proxy_enable:
        session.proxies['https'] = args.proxy_url

    # Now we're into the guts of the script

    # First we get the list of asset groups from the subscription
    print('Getting Asset Groups ...', end='')
    asset_groups = get_asset_groups(baseurl=args.api_url, session=session, debug=args.debug)
    print('Done')
    if args.debug:
        print(json.dumps(asset_groups, indent=2))

    # asset_groups now contains a dictionary object which looks like this
    # {'ASSET_GROUP_LIST_OUTPUT': {'RESPONSE': {'DATETIME': '<date>', 'ASSET_GROUP_LIST': {'ASSET_GROUP': [
    #   {'ID': '123456789', 'BUSINESS_IMPACT': 'High'}, <...>}]}}}}

    # the good stuff lives in that ASSET_GROUP list, so iterate through that
    for asset_group in asset_groups['ASSET_GROUP_LIST_OUTPUT']['RESPONSE']['ASSET_GROUP_LIST']['ASSET_GROUP']:
        # Update the asset group
        print('Updating %s ... ' % asset_group['TITLE'], end='')
        if asset_group['BUSINESS_IMPACT'] == 'Minor':
            print('Skipped (already set to "Minor"')
            continue
        else:
            resp = update_asset_group(baseurl=args.api_url, session=session, asset_group_id=asset_group['ID'],
                                      debug=args.debug)
            print('Done')
