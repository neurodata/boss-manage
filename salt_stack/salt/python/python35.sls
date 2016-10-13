# Build Python 3.5.x from source and install to /usr/local/bin.
# pip3.5.x is also installed during the build process.
#
# The JUSTVERSION variable in the install script specifies the specific Python
# version installed.
#
# Redirecting output to /dev/null is essential.  Salt hung when run
# w/o redirecting output.

# Need python-pip for Salt to be able to to pip installs
python35:
  pkg.installed:
        - pkgs:
            - python-pip
            - python3-pip
  cmd.run:
    - name: |
        echo nothing to do
        #cd /usr/local/bin
        #ln -s /usr/bin/python3 python3
        #ln -s /usr/bin/python3.5 python3.5
        #ln -s /usr/bin/pip3 pip3

        #cd /usr/local/lib
        #ln -s python3.5 python3
        #cd python3.5
        #ln -s dist-packages site-packages
    - cwd: /tmp
    - shell: /bin/bash
    - timeout: 600
    - unless: test -x /usr/local/bin/python3.5 && test -x /usr/local/bin/pip3.5
