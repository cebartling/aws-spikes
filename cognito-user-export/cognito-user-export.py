import sys
import boto3
import csv
import logging

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)


def process_user_pool(client, user_pool):
    if 'Id' in user_pool:
        user_pool_id = user_pool['Id']
        response = client.list_users(UserPoolId=user_pool_id)
        if 'Users' in response:
            users = response['Users']
            file_name = 'cognito-users-{}.csv'.format(user_pool_id)
            logging.info('Writing CSV file: {}'.format(file_name))
            with open(file_name, 'w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                write_header(csv_writer)
                for user in users:
                    write_user_record(csv_writer=csv_writer, user=user)


def write_user_record(csv_writer, user):
    logging.info('User: {0}'.format(user))
    csv_writer.writerow([
        user['Username'],
        user['UserCreateDate'],
        user['UserLastModifiedDate'],
        user['Enabled'],
        user['UserStatus'],
        user.get('Foobar', None),
    ])


def write_header(csv_writer):
    # cognito:username,name,given_name,family_name,middle_name,nickname,preferred_username,profile,picture,website,email,email_verified,gender,birthdate,zoneinfo,locale,phone_number,phone_number_verified,address,updated_at,cognito:mfa_enabled
    csv_writer.writerow([
        'cognito:username',
        'name',
        'given_name',
        'family_name',
        'middle_name',
        'nickname',
        'preferred_username',
    ])


profile_name = 'default'
if len(sys.argv) > 1 and sys.argv[1] is not None:
    profile_name = sys.argv[1]

logging.info('Using profile: {}'.format(profile_name))

session = boto3.Session(profile_name=profile_name)
cognito_idp_client = session.client('cognito-idp')

response = cognito_idp_client.list_user_pools(MaxResults=5)
logging.info('User pool response: {}'.format(response))

if 'UserPools' in response:
    for user_pool in response['UserPools']:
        process_user_pool(client=cognito_idp_client, user_pool=user_pool)
