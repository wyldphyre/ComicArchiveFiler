#!/usr/bin/env python

# Get a permission denied error when running the script in the shell? chmod 755 the script .py file

import sys
import os
import subprocess


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

        # TODO: handle notifications


# Main program method
def ComicArchiveFiler():
    arguments = sys.argv

    if len(arguments) != 3:  # the sys.argv[0] contains the script name, so there is always at least one argument
        print "Incorrect parameters!"
        outputHelp()
        quit()

    configuration_path = ""
    archive_path = ""
    send_notification = False

    for param in arguments[1:]:
        if param.startswith('-'):
            if param == '-p':
                send_notification = True
            else:
                print "Unknown options %s" % param
                quit()
        else:
            if configuration_path == "":
                configuration_path = param
            else:
                archive_path = param

    if configuration_path == "":
        print "You must specify a archive_path to a configuration file"
        quit()
    else:
        if not os.path.exists(configuration_path):
            print "Cannot locate configuration file path: %s" % configuration_path
            quit()

    if archive_path == "":
        print "You must specify a comic archive file"
        quit()
    else:
        if not os.path.exists(archive_path):
            print "Cannot locate archive file path: %s" % archive_path

    routes = readRoutingConfiguration(configuration_path)

    if len(routes) < 1:
        print "Found no valid routing instructions in the configuration file"
        quit()

    if os.path.isdir(archive_path):
        directory_list = os.listdir(archive_path)

        for filename in directory_list:
            file_path = os.path.join(archive_path, filename)

            if os.path.isfile(file_path):
                processFile(file_path, routes, send_notification)

    elif os.path.isfile(archive_path):
        processFile(archive_path, routes, send_notification)


# Start of execution
ComicArchiveFiler()
