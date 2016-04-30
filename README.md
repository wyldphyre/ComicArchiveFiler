# ComicArchiveFiler
Examines comic archive files (.cbz and .cbz) and moves them to a new location based on configured rules.

The goal is a to provide an easy to use script that will look at the series metadata contained within a comic archive file and then file the archive by moving it to a new location, as specified by a simple rule configuration file.

# Requirements
- [ComicTagger](https://github.com/tomdelise/comictagger) (or [here, originally](https://code.google.com/p/comictagger/)) for reading the metadata from archive files

# Current Status
- Basic implementation is done. The script can move files and send notifications via Pushover.

# Usage
    ComicArchiveFiler [OPTIONS] <CONFIGURATIONFILE> <ARCHIVEFILE>

    Looks at the series metadata for a comic archive and move the file if a matching rule is found in the specified rule configuration file

    Options:
     -n : Send notifications
     -pushover:APP_TOKEN:USER_KEY


# Roadmap:
- [Done] Get the script to the going to the point of being able to examine an individual file and read the series information. Initial target is reading of ComicRack metadata only.
- [Done] Read the configuration file that determines where an archive should be moved to
- [Done] Move file based on routing configuration
- [Done] Send (optional) notification when a file is matched (maybe when no match made as well?). Pushover will be the initial target notification service.
- [Planned] Document usage and parameters in README.md
- [Done] Send notification if no routing match is found
- [Done] Log activity
- [Eventually] Support reading of Comic Book Lover metadata.
- [Maybe] Handle folders and subfolders in addition to individual files (the code is actually there, I just haven't tested it)
- [Maybe] Investigate using [ComicAPI](https://github.com/davide-romanini/comicapi) instead of requiring ComicTagger to be installed
