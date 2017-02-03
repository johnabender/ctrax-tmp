#!/bin/bash

scp -i ~/.ssh/id_rsa_sourceforge_ctrdev *.html johnabender@web.sourceforge.net:/home/project-web/ctrax/htdocs/
scp -i ~/.ssh/id_rsa_sourceforge_ctrdev styles/* johnabender@web.sourceforge.net:/home/project-web/ctrax/htdocs/styles/

