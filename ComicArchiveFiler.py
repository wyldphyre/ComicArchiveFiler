#!/usr/bin/env python

# Get a permission denied error when running the script in the shell? chmod 755 the script .py file

import sys
import os
import subprocess
import shutil
import httplib, urllib


# COMIC_TAGGER_PATH = 'COMIC_TAGGER_PATH/Applications/ComicTagger.app/Contents/MacOS/ComicTagger'
COMIC_TAGGER_PATH = 'ComicTagger'  # a local alias that points to the full path above
HANDLED_EXTENSIONS = ['.cbr', '.cbz']


class ArchiveRoute:
    """ Defines an archive metadata routing configuration """
    metadataElement = ""
    metadataContent = ""
    target = ""

    def __init__(self, element, content, target):
        self.metadataElement = element
        self.metadataContent = content
        self.target = target

    def display(self):
        return "Metadata: {0} = {1}, target: {2}".format(self.metadataElement, self.metadataContent, self.target)


class Configuration:
    """ Encapsulates the configuration options for ComicArchiveFiler """
    configuration_path = ""
    target_path = ""
    send_notifications = False
    errors = list()

    def __init__(self):
        arguments = sys.argv

        if len(arguments) != 3:  # the sys.argv[0] contains the script name, so there is always at least one argument
            self.errors.append("Incorrect parameters!")

        for param in arguments[1:]:
            if param.startswith('-'):
                if param == '-p':
                    self.send_notification = True
                else:
                    self.erros.append("Unknown options {0}".format(param))
            else:
                if self.configuration_path == "":
                    self.configuration_path = param
                else:
                    self.target_path = param

        if self.configuration_path == "":
            self.errors.append("You must specify a archive_path to a configuration file")
        else:
            if not os.path.exists(self.configuration_path):
                self.errors.append("Cannot locate configuration file path: {0}".format(self.configuration_path))

        if self.target_path == "":
            self.errors.append("You must specify a target comic archive file")
        else:
            if not os.path.exists(self.target_path):
                self.errors.append("Cannot locate archive file path: {0}".format(self.target_path))

    def valid(self):
        return len(self.errors) == 0


def escapeForShell(source):
    assert isinstance(source, str)
    return source.replace(' ', '\ ').replace('(', '\(').replace(')', '\)')


def outputHelp():
    print ''
    print 'Usage: ComicArchiveFiler [OPTIONS] [CONFIGURATIONFILE] [ARCHIVEFILE]'
    print ''
    print 'Looks at the series metadata for a comic archive and move the file if a matching rule is found in the specified rule configuration file'
    print ''
    print 'Options:'
    print '  No options yet'
    print ''


def parseExistingTags(data):
    assert isinstance(data, str)

    # validate
    start_index = data.find('------ComicRack tags--------')
    if start_index == -1:
        return []

    data = data[data.find('\n', start_index) + 1:]

    lines = data.splitlines()
    tags = {}

    for line in lines:
        if line == '':
            continue

        pieces = line.split(':', 1)

        if len(pieces) > 0 and pieces[1] != '':
            tags[pieces[0]] = pieces[1].strip(' ')

    return tags


def readRoutingConfiguration(configuration_path):
    routes = list()

    with open(configuration_path) as f:
        lines = [line.rstrip('\n') for line in f]

        for line in lines:
            # print line
            pieces  = line.split("->")

            if len(pieces) != 2:
                print "Routing configuration line must contain a '->': %s" % line
                quit()

            if ":" not in pieces[0]:
                print "Metadata specification must contain a ':' : %s" % pieces[0];

            target = pieces[1].strip()
            metadata = [data.strip() for data in pieces[0].split(":")]

            routes.append(ArchiveRoute(metadata[0], metadata[1], target))

    return routes


def PushNotification(message):
    # Pushover notification
    conn = httplib.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
      urllib.urlencode({
        "token": "a1kgcb7huvD9nxuuwZPj9jQqjtZ1Pz",
        "user": "uh8KJfSxGsz1riWvN7bo7pRraU6qnY",
        "message": message,
      }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()


def processFile(file_path, routes, send_notification):
    assert isinstance(file_path, str)
    assert isinstance(send_notification, bool)

    # check that file is a comic archive
    filename = os.path.split(file_path)[1]
    extension = os.path.splitext(file_path)[1]

    if extension not in HANDLED_EXTENSIONS:
        print "Skipping %s. Not a recognised comic archive" % filename
        return

    print "Processing: %s" % filename

    process = subprocess.Popen('%s -p %s' % (COMIC_TAGGER_PATH, escapeForShell(file_path)), stdout=subprocess.PIPE, shell=True)
    existing_tags = parseExistingTags(process.stdout.read())

    applicableRoutes = [route for route in routes if
                        route.metadataElement in existing_tags and existing_tags[route.metadataElement].lower() == route.metadataContent.lower()];

    if len(applicableRoutes) > 0:
        route = applicableRoutes[0]
        print "Found matching route {0} for file {1}".format(route.display(), file_path)

        # TODO: move file to route.target
        file_copied = False

        try:
            shutil.copy2(file_path, route.target)
            file_copied = True

            # TODO: handle notifications
            if send_notification:
                PushNotification("Filed: {0}".format(filename))

        except Exception:
            copy_error = "Error: Could not copy file {0} to {1}".format(file_path, route.target)
            print copy_error
            if send_notification:
                PushNotification(copy_error)
            pass

        if file_copied:
            try:
                os.remove(file_path)
            except Exception:
                delete_error = "Error: Could not delete file {0}".format(file_path)
                print delete_error
                if send_notification:
                    PushNotification(delete_error)
                pass


# Main program method
def ComicArchiveFiler():
    configuration = Configuration()

    if not configuration.valid():
        for error in configuration.errors:
            print error

        outputHelp()
        quit()

    routes = readRoutingConfiguration(configuration.configuration_path)

    if len(routes) < 1:
        print "Found no valid routing instructions in the configuration file"
        quit()

    if os.path.isdir(configuration.target_path):
        directory_list = os.listdir(configuration.target_path)

        for filename in directory_list:
            file_path = os.path.join(configuration.target_path, filename)

            if os.path.isfile(file_path):
                processFile(file_path, routes, configuration.send_notifications)

    elif os.path.isfile(configuration.target_path):
        processFile(configuration.target_path, routes, configuration.send_notifications)


# Start of execution
ComicArchiveFiler()
