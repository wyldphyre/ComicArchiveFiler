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


def escapeForShell(source):
    assert isinstance(source, str)
    return source.replace(' ', '\ ').replace('(', '\(').replace(')', '\)')


class NotificationConfiguration:
    def __init__(self):
        self.app_token = ""
        self.user_key = ""


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
    pushover_configuration = NotificationConfiguration()
    routes = list()

    def __init__(self):
        arguments = sys.argv

        print arguments

        if len(arguments) < 3:  # the sys.argv[0] contains the script name, so there is always at least one argument
            self.errors.append("Incorrect parameters!")

        for param in arguments[1:]:
            if param.startswith('-'):
                if param == '-n':
                    self.send_notifications = True
                elif param.startswith("-pushover:"):
                    pieces = param.split(":")
                    self.pushover_configuration.app_token = pieces[1]
                    self.pushover_configuration.user_key = pieces[2]
                else:
                    self.errors.append("Unknown options {0}".format(param))
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

        self.routes = self.readRoutingConfiguration(self.configuration_path)

    def valid(self):
        return len(self.errors) == 0

    def readRoutingConfiguration(self, configuration_path):
        routes = list()

        with open(configuration_path) as f:
            lines = [line.rstrip('\n') for line in f if line != '' and line != '\n']

            for line in lines:
                # print line
                pieces = line.split("->")

                if len(pieces) != 2:
                    print "Routing configuration line must contain a '->': {0}".format(line)
                    quit()

                if ":" not in pieces[0]:
                    print "Metadata specification must contain a ':' : {0}".format(pieces[0]);

                target = pieces[1].strip()
                metadata = [data.strip() for data in pieces[0].split(":", 1)]

                routes.append(ArchiveRoute(metadata[0], metadata[1], target))

        return routes


class ComicArchiveFiler:
    """ This class encapsulates the behaviour of the ComicArchiveFiler script """

    def __init__(self):
        self.configuration = Configuration()

        if not self.configuration.valid():
            for error in self.configuration.errors:
                print error

            self.outputHelp()
            return

    @staticmethod
    def outputHelp():
        print ''
        print 'Usage: ComicArchiveFiler [OPTIONS] <CONFIGURATIONFILE> <ARCHIVEFILE>'
        print ''
        print 'Looks at the series metadata for a comic archive and move the file if a matching rule is found in the specified rule configuration file'
        print ''
        print 'Options:'
        print ' -n : Send notifications'
        print ' -pushover:APP_TOKEN:USER_KEY'
        print ''

    @staticmethod
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
            if ':' not in line:
                continue

            pieces = line.split(':', 1)

            if len(pieces) > 1 and pieces[1] != '':
                tags[pieces[0]] = pieces[1].strip(' ')

        return tags

    @staticmethod
    def pushNotification(pushover_configuration, message, priority = 0):
        # Pushover notification
        conn = httplib.HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json",
                     urllib.urlencode({
                         "token": pushover_configuration.app_token,
                         "user": pushover_configuration.user_key,
                         "message": message,
                         "priority": priority
                     }), {"Content-type": "application/x-www-form-urlencoded"})
        conn.getresponse()

    def processFile(self, file_path):
        assert isinstance(file_path, str)
        assert isinstance(self.configuration.send_notifications, bool)

        # check that file is a comic archive
        filename = os.path.split(file_path)[1]
        extension = os.path.splitext(file_path)[1]

        if extension not in HANDLED_EXTENSIONS:
            print "Skipping {0}. Not a recognised comic archive".format(filename)
            return

        print "Processing: {0}".format(filename)

        process = subprocess.Popen('%s -p %s' % (COMIC_TAGGER_PATH, escapeForShell(file_path)), stdout=subprocess.PIPE,
                                   shell=True)
        existing_tags = self.parseExistingTags(process.stdout.read())

        applicable_routes = [route for route in self.configuration.routes if
                            route.metadataElement in existing_tags and existing_tags[
                                route.metadataElement].lower() == route.metadataContent.lower()];

        if len(applicable_routes) > 0:
            route = applicable_routes[0]
            print "Found matching route {0} for file {1}".format(route.display(), file_path)

            # TODO: move file to route.target
            file_copied = False

            try:
                shutil.copy2(file_path, route.target)
                file_copied = True

                # send low priority notification that filing is complete
                if self.configuration.send_notifications:
                    self.pushNotification(self.configuration.pushover_configuration, "Filed: {0}".format(filename), -1)

            except Exception:
                copy_error = "Error: Could not copy file {0} to {1}".format(file_path, route.target)
                print copy_error
                if self.configuration.send_notifications:
                    self.pushNotification(self.configuration.pushover_configuration, copy_error, 1)
                pass

            if file_copied:
                try:
                    os.remove(file_path)
                except Exception:
                    delete_error = "Error: Could not delete file {0}".format(file_path)
                    print delete_error
                    if self.configuration.send_notifications:
                        self.pushNotification(self.configuration.pushover_configuration, delete_error, 1)
                    pass
        else:
            self.pushNotification(self.configuration.pushover_configuration, "Could not file {0}. No matching route found".format(filename))

    def execute(self):
        if len(self.configuration.routes) < 1:
            print "Found no valid routing instructions in the configuration file"
            return

        if os.path.isdir(self.configuration.target_path):
            directory_list = os.listdir(self.configuration.target_path)

            for filename in directory_list:
                file_path = os.path.join(self.configuration.target_path, filename)

                if os.path.isfile(file_path):
                    self.processFile(file_path, self.configuration)

        elif os.path.isfile(self.configuration.target_path):
            self.processFile(self.configuration.target_path)

# Start of execution
filer = ComicArchiveFiler()
filer.execute()
