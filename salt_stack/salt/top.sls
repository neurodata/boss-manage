base:
    'vault':
        - vault.server
        - boss-tools.bossutils

    'endpoint':
        - boss-tools.bossutils
        - boss.django

    'jenkins*':
        - git
        - python.python35
# Install 2.7.x pip so Salt's pip module can run.
        - python.pip
        - jenkins
        - jenkins.plugins
        - jenkins.slack
        - jenkins.jobs
# tox is probably unnecessary if we only target a single Python version.
# - python.tox
        - python.nose2-3
        - python.nose2-cov-3
        - vault.client
        - aws.boto3

    'proofreader-web':
        - proofreader-web
