# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import gettext
import glob
import os
import subprocess
import sys
import time

from setuptools import find_packages
from setuptools.command.sdist import sdist

# In order to run the i18n commands for compiling and
# installing message catalogs, we use DistUtilsExtra.
# Don't make this a hard requirement, but warn that
# i18n commands won't be available if DistUtilsExtra is
# not installed...
try:
    from DistUtilsExtra.auto import setup
except ImportError:
    from setuptools import setup
    print "Warning: DistUtilsExtra required to use i18n builders. "
    print "To build nova with support for message catalogs, you need "
    print "  https://launchpad.net/python-distutils-extra >= 2.18"

gettext.install('nova', unicode=1)

TOPDIR = os.path.abspath(os.path.dirname(__file__))
VFILE  = os.path.join(TOPDIR, 'nova', '__pistonversion__.py')

args = filter(lambda x: x[0] != '-', sys.argv)
command = args[1] if len(args) > 1 else ''

if command == 'sdist':
    PISTON_VERSION = os.environ['PISTON_VERSION']
    with file(VFILE, 'w') as f:
        f.write('''#!/usr/bin/env python\nVERSION = '%s'\n''' % PISTON_VERSION)
elif command == 'develop':
    PISTON_VERSION = time.strftime('9999.0.%Y%m%d%H%M%S', time.localtime())
    with file(VFILE, 'w') as f:
        f.write('''#!/usr/bin/env python\nVERSION = '%s'\n''' % PISTON_VERSION)
elif command is None:
    PISTON_VERSION = '9999999999-You_did_not_set_a_version'
else:
    assert os.path.exists(VFILE), 'version.py does not exist, please set PISTON_VERSION (or run make_version.py for dev purposes)'

from nova import version


nova_cmdclass = dict()

try:
    from sphinx.setup_command import BuildDoc

    class local_BuildDoc(BuildDoc):
        def run(self):
            for builder in ['html', 'man']:
                self.builder = builder
                self.finalize_options()
                BuildDoc.run(self)
    nova_cmdclass['build_sphinx'] = local_BuildDoc

except:
    pass


try:
    from babel.messages import frontend as babel
    nova_cmdclass['compile_catalog'] = babel.compile_catalog
    nova_cmdclass['extract_messages'] = babel.extract_messages
    nova_cmdclass['init_catalog'] = babel.init_catalog
    nova_cmdclass['update_catalog'] = babel.update_catalog
except:
    pass


def find_data_files(destdir, srcdir):
    package_data = []
    files = []
    for d in glob.glob('%s/*' % (srcdir, )):
        if os.path.isdir(d):
            package_data += find_data_files(
                os.path.join(destdir, os.path.basename(d)), d)
        else:
            files += [d]
    package_data += [(destdir, files)]
    return package_data

setup(name='nova',
      version=version.canonical_version_string(),
      description='cloud computing fabric controller',
      author='OpenStack',
      author_email='nova@lists.launchpad.net',
      url='http://www.openstack.org/',
      cmdclass=nova_cmdclass,
      packages=find_packages(exclude=['bin', 'smoketests']),
      include_package_data=True,
      test_suite='nose.collector',
      data_files=find_data_files('share/nova', 'tools'),
      scripts=['bin/clear_rabbit_queues',
               'bin/instance-usage-audit',
               'bin/nova-ajax-console-proxy',
               'bin/nova-api',
               'bin/nova-api-ec2',
               'bin/nova-api-os',
               'bin/nova-compute',
               'bin/nova-console',
               'bin/nova-dhcpbridge',
               'bin/nova-direct-api',
               'bin/nova-logspool',
               'bin/nova-manage',
               'bin/nova-network',
               'bin/nova-objectstore',
               'bin/nova-scheduler',
               'bin/nova-spoolsentry',
               'bin/nova-vncproxy',
               'bin/nova-volume',
               'bin/nova-vsa',
               'bin/stack',
               'tools/nova-debug'],
      py_modules=[])
