#!/usr/bin/env python

# Get a permission denied error when running the script in the shell? chmod 755 the script .py file

import sys
import os
import re
import subprocess


# COMIC_TAGGER_PATH = 'COMIC_TAGGER_PATH/Applications/ComicTagger.app/Contents/MacOS/ComicTagger'
COMIC_TAGGER_PATH = 'ComicTagger'  # a local alias that points to the full path above
HANDLED_EXTENSIONS = ['.cbr', '.cbz']


def escapeForShell(source):
    assert isinstance(source, str)
    return source.replace(' ', '\ ').replace('(', '\(').replace(')', '\)')


def escapeForComicTagger(source):
    assert isinstance(source, str)
    return source.replace(',', '^,').replace('=', '^=')


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


def processFile(file_path, send_notification):
    assert isinstance(file_path, str)
    assert isinstance(send_notification, bool)

    # check that file is a comic archive
    filename = os.path.split(file_path)[1]
    extension = os.path.splitext(file_path)[1]

    if extension not in HANDLED_EXTENSIONS:
        print "Skipping %s. Not a comic archive" % filename
        return

    print "Processing: %s" % filename

    # # look for the issue number and title
    # filename_volume = ""
    # filename_issue = ""
    # filename_title = ""

    # # look for volume and chapter match i.e. chiis.sweet.home.MangaHere.v005.c017.cbz
    # match = re.search('\.v(\d*)\.c(.*)\.cbz|cbr', filename)
    # if match:
    #     filename_volume = match.group(1)
    #     filename_issue = match.group(2)
    # else:
    #     match = re.search('\.(\d*)\.\.(.*)\.cbz|cbr', filename)
    #     if match:
    #         filename_issue = match.group(1)
    #         filename_title = match.group(2)
    #     else:
    #         match = re.search('\.c?(\d*)\.cbz|cbr', filename)
    #         if match:
    #             filename_issue = match.group(1)

    # if not match:
    #     print "Could not locate a title or issue number in: %s" % filename
    # else:
    #     if filename_volume != "":
    #         filename_volume = cleanFilenameIssue(filename_volume)
    #         print "Found Volume: %s" % filename_volume

    #     if filename_issue != "":
    #         filename_issue = cleanFilenameIssue(filename_issue)
    #         print "Found Issue: %s" % filename_issue

    #     if filename_title != "":
    #         filename_title = cleanFilenameTitle(filename_title)
    #         print "Found Title: %s" % filename_title

    #     process = subprocess.Popen('%s -p %s' % (COMIC_TAGGER_PATH, escapeForShell(file_path)), stdout=subprocess.PIPE, shell=True)
    #     existing_tags = parseExistingTags(process.stdout.read())

    #     needs_update = \
    #         (filename_issue != '' and (not 'issue' in existing_tags or (filename_issue != existing_tags['issue']))) or \
    #         (filename_title != '' and (not 'title' in existing_tags or (filename_title != existing_tags['title']))) or \
    #         (filename_volume != '' and (not 'volume' in existing_tags or (filename_volume != existing_tags['volume'])))

    #     if needs_update:
    #         do_update = auto_update or raw_input("Update tags for this file? (y/n): ") == "y"

    #         if do_update:
    #             metadata_statement = produceComicTaggerMetaDataStatement(filename_volume, filename_issue, filename_title)
    #             command = '%s -s -m "%s" -t cr %s' % (COMIC_TAGGER_PATH, metadata_statement, escapeForShell(file_path))

    #             return_code = subprocess.call(command, shell=True)
    #             if return_code != 0:
    #                 print "Return code: %s" % return_code
    #     else:
    #         print 'Tags already match found data. Skipping archive.'
    # print ""


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

    if archive_path == "":
        print "You must specify a comic archive file"
        quit()

    if os.path.isdir(archive_path):
        directory_list = os.listdir(archive_path)

        for filename in directory_list:
            file_path = os.path.join(archive_path, filename)

            if os.path.isfile(file_path):
                processFile(file_path, send_notification)

    elif os.path.isfile(archive_path):
        processFile(archive_path, send_notification)


# Start of execution
ComicArchiveFiler()
