# upgrade packages in the current environment
import pkg_resources
from subprocess import call
import pprint
packages = [dist.project_name for dist in pkg_resources.working_set]
packages.sort()
pprint.pprint(packages)
# call("pip install --upgrade " + ' '.join(packages), shell=True)
