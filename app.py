from flask import Flask, render_template,request, flash, redirect, url_for
import urllib.request
import boto3
from botocore.exceptions import ClientError


app = Flask(__name__)
app.secret_key = '454retretrfgrtz'

name_list =['user list']

aws_access_key_id = 'id'

aws_secret_access_key = 'key'

GROUP_ID = 'group id'



@app.route('/rdp')
def update_to_rdp(user):
    NEW_IP = request.environ.get('HTTP_X_REAL_IP', request.remote_addr) + '/32'
    OLD_IP = ''


    ec2 = boto3.client('ec2', region_name='eu-west-2', aws_access_key_id=aws_access_key_id,
                       aws_secret_access_key=aws_secret_access_key)

    try:

        response = ec2.describe_security_groups(GroupIds=[GROUP_ID])

    except ClientError as e:

        flash(e, "warning")

    sg = response['SecurityGroups']


    for e in range(len(sg[0]['IpPermissions'][0]['IpRanges'])):

        if sg[0]['IpPermissions'][0]['IpRanges'][e]['Description'] == user:
            OLD_IP = sg[0]['IpPermissions'][0]['IpRanges'][e]['CidrIp']
            break

    if (OLD_IP != NEW_IP) & (OLD_IP != ''):

        try:
            d = ec2.revoke_security_group_ingress(GroupId=GROUP_ID, IpPermissions=[
                {'IpProtocol': 'tcp', 'FromPort': 3389, 'ToPort': 3389,
                 'IpRanges': [{'CidrIp': OLD_IP, 'Description': user}]}])

            # print('Ingress successfully removed %s' % d)

        except ClientError as e:

            flash(e, "warning")

        try:
            d = ec2.authorize_security_group_ingress(GroupId=GROUP_ID, IpPermissions=[
                {'IpProtocol': 'tcp', 'FromPort': 3389, 'ToPort': 3389,
                 'IpRanges': [{'CidrIp': NEW_IP, 'Description': user}]}])
            flash('ip updated', "success")

        except ClientError as e:

            flash(e, "warning")
    else:
        flash('IP already exists', "warning")



@app.route('/')
def home():

    a = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    return render_template('home.html',my_ip=a)


@app.route('/ip', methods=['GET','POST'])
def ip():
    if request.method == 'POST':
        if request.form['name'] not in name_list:
            flash("user doesn't exist","warning")
            return redirect(url_for('home'))
        else:
            update_to_rdp(request.form['name'])
            return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run()
