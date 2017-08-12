#!/bin/bash -x

# upload script for Ctrax PPA
# JAB 2/14/12

# Ubuntu must have extra packages installed:
# ubuntu-dev-tools
# (maybe also dput, if not included)

# Launchpad must have a GPG key and an SSH key for user.
# See their instructions.
# https://launchpad.net/~ctrax/+editpgpkeys
# https://launchpad.net/~ctrax/+editsshkeys
# The GPG key's passphrase might be needed several times
# during build/sign/upload.

keyname='E56DDCF5' # Ctrax key!

##### these lines go in ~/.dput.cf to configure dput #####
#[ctrax]
#fqdn = ppa.launchpad.net
#method = sftp
#incoming = ~ctrax/ppa/ubuntu/
#login = ctrax
#allow_unsigned_uploads = 0
##########################


##### This sequence of commands builds and uploads to Launchpad. #####
rm -rf deb_dist

# requires stdeb package, from PyPI (same command as makedeb.sh)
python setup.py --command-packages=stdeb.command \
  sdist_dsc --extend-diff-ignore '(SOURCES\.txt$)|(^tmp\/tmp.*\.o$)|(version\.txt$)|(kcluster.*?\.c$)|(tracking_funcs\.c$)' \
  bdist_deb

# get $version from version.txt
version="`cat version.txt`"

cd deb_dist/

last_distro='unstable'
last_revision=1
revision=1

for distro in 'artful' 'zesty' 'xenial' 'trusty'
do
   cd ctrax-$version/

   # build and sign .deb files
   # get key ID (-k) from the output of  gpg --list-keys
   # (must be the same key that Launchpad has registered)
   debuild -S -sa -k$keyname || exit 1

   # change version name "unstable" to an Ubuntu version in changelog
   perl -pi -e s/$last_distro/$distro/ debian/changelog
   perl -pi -e s/$version-$last_revision/$version-$revision/ debian/changelog

   # append Matplotlib and Cython as dependencies...
   # this is a total hack, since what packages are already listed varies unexplainably
   # I believe this is resolved by adding cython,python-matplotlib to stdeb.cfg.
   #perl -pi -e "s/python-imaging/python-imaging, cython, python-matplotlib/" debian/control

   # Remove python-support dependency, since it doesn't exist as of Ubuntu Xenial.
   # This seems to break installation of the resulting .deb on systems that don't
   # have python-support already installed (i.e., clean installs).
   # It seems to have been resolved by removing python-support from stdeb.cfg.
   #perl -pi -e "s/python-support(\\s?(.*?\))//" debian/control

   # build again (first build created debian/changelog from setup.py config)
   debuild -S -sa -k$keyname || exit 1

   cd ..
   dput ctrax ctrax_$version-"$revision"_source.changes || exit 1

   # Subsequent builds will use the first .orig.tar.gz uploaded.
   # Not deleting this file will cause subsequent builds to be rejected.
   #rm -f ctrax_$version.orig.tar.gz
   # This seems to have changed sometime around 2016.

   last_revision=$revision
   last_distro=$distro

   let revision++
done


##### This sequence of commands builds and uploads to PyPI. #####
#cd ..
#python setup.py bdist upload
#python setup.py sdist upload

