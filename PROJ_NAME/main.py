# =================================================================
# Script name: main.py
#
# Description: the main script for running PROJ_NAME
# =================================================================

import logging
import os
import sys
import time
import re

import arcpy

import util
from arcpy_logging import ArcpyLog


EMAIL_SENDER = 'orapipe@dnr.wa.gov' # use for Appworx
ADMIN_EMAIL = ['Hilary.Browning@dnr.wa.gov', 'Kristin.Jamison@dnr.wa.gov']
# ADMIN_EMAIL = ['Kristin.Jamison@dnr.wa.gov'] # kj testing
mail_server = os.getenv("MAILRELAY")


class SetUp(object):
    """
    Set up temp folders, log files, and global variables.

    The folder tree for this set up looks as follows (using attached
    attribute names rather than paths):

    .. code-block:: text

        |-- workspace
            |-- folder_name (all up to this point = work_folder)
                |-- proc_id (^= process_path)
                    |-- gdb_name.gdb (^= gdb_full_path)


    Using ``^=`` as short-hand for 'all up to this point, ``os.path.join()``'.

    Attributes
    ----------
    folder_name: str
        Hard-coded to 'PROJ_NAME'
    ropa_path: str
        Hard-coded ROPA base path
    workspace: str
        Hard-coded DNR TEMP folder
    work_folder: str
        Joined workspace and folder_name

    data_home: str
        System env variable 'DATAHOME'
    mail_server: str
        System env variable 'MAILRELAY'
    myenv: str
        System env variable 'MYENV'
    proc_drive: str
        System env variable 'PROCDRIVE'
    ropa_instance: str
        System env variable 'ROPA_SDE_INSTANCE'
    connect_home: str
        SDE connection home
    log_home: str
        Folder where logs written

    date_time_stamp: str
        Date & time string-formatted to: '%m-%d-%H%M'
    log: logging object
        Module level logging instance
    process_path: str
        Full path to the folder where processing occurs
    gdb_full_path: str
        Full path to geodatabase where outputs saved
    """

    def __init__(self, log_level, proc_id, email, gdb_name):
        """
        Parameters
        ----------
        log_level: str
            Logging severity conformant to standard logging
        proc_id: str
            Process ID from batch processer
        gdb_name: str
            Geodatabase name to create/write to
        """
        print("Setting system variables")

        # Hard-coded
        self.folder_name = "PROJ_NAME"
        # self.ropa_path = '\\\\dnr\\divisions\\FR_DATA\\forest_info_2\\gis\\tools\\sde_connections_read\\ropa_gis_layer_user_direct.sde'
        self.workspace = "\\\\DNR\\REGIONS\\TEMP"
        self.work_folder = os.path.join(self.workspace, self.folder_name)

        # System Vars
        # self.data_home = 'data_home'  # os.getenv("DATAHOME")
        # self.mail_server = 'mailrelay'  # os.getenv("MAILRELAY")
        # self.myenv = 'myenv'  # os.getenv("MYENV")
        # self.proc_drive = 'proc_drive'  # os.getenv("PROCDRIVE")
        # self.ropa_instance = 'ropa_sde_instance'  # os.getenv("ROPA_SDE_INSTANCE")
        # self.connect_home = os.path.join(self.proc_drive, "sde_connections")
        # self.log_home = 'logs' #os.path.join(self.data_home, "manage\\logs")

        # Inputs
        self.date_time_stamp = time.strftime('%m%d%Y_%H%M')
        self.gdb_name = gdb_name
        self.log_level = log_level
        self.recipient_id = self.parse_email_address(email_address=email)
        self.process_id = "{}_{}".format(self.recipient_id, proc_id)

        # Run set up methods
        self.log, self.log_path = self.create_logger(self.log_level)
        self.check_work_folder_exists()
        self.process_path = self.create_process_folder()
        self.gdb_full_path = self.create_gdb()

    def create_logger(self, log_level):
        """Create a logging instance at log home with date stamp.

        This logger is the parent of what is being passed around inside the rest of
        the module (including what is passed into, and then out of, ArcpyLog) and it is
        what is passed to getlogger in the sub-modules.

        Parameters
        ----------
        log_level: str
            Logging severity conformant to standard logging

        Returns
        -------
        logging object
            Module level logging instance
        log_path str
            Path to log file on disk

        """
        # kj - file_name = "log_{}.log".format(self.date_time_stamp)
        file_name = "PROJ_NAME_{}.log".format(self.date_time_stamp)
        log_path = os.path.join(self.log_home, file_name)
        level = log_level.upper()
        switcher = {"DEBUG": logging.DEBUG,
                    "INFO": logging.INFO,
                    "WARNING": logging.WARNING,
                    "ERROR": logging.ERROR,
                    "CRITICAL": logging.CRITICAL}
        logging.basicConfig(filename=log_path,
                            format="%(asctime)s | %(name)s [Line %(lineno)d] | %(levelname)s: %(message)s",
                            datefmt="%m/%d/%Y %H:%M:%S",
                            level=switcher[level])
        logger = logging.getLogger("root")
        return logger, os.path.abspath(log_path)

    def check_work_folder_exists(self):
        """Creates folder at :code:`//DNR/REGIONS/TEMP/PROJ_NAME` if it does not exist.

        Returns
        -------
        None
        """
        os.chdir(self.workspace)
        try:
            os.mkdir(self.folder_name)
            self.log.info("Made new work folder at: {}".format(self.work_folder))
            # Note: The syntax of 0o777 is for Python 2.6 and 3+.
            os.chmod(self.folder_name, 0o777)
        except WindowsError:
            self.log.info("Work folder exists at: {}".format(self.work_folder))

    def create_process_folder(self):
        """Creates folder for processing if it does not exist.

        Returns
        -------
        str
            Full path to the folder where processing occurs
        """
        os.chdir(self.work_folder)
        full_path = os.path.join(self.work_folder, self.process_id)
        if not os.path.exists(self.process_id):
            os.mkdir(self.process_id)
            self.log.info("Made new processing folder at: {}".format(full_path))
            # Note: The syntax of 0o777 is for Python 2.6 and 3+.
            os.chmod(self.process_id, 0o777)
        else:
            self.log.info("Pre-existing processing folder found at: {}".format(full_path))
        return full_path

    def create_gdb(self):
        """Creates geodatabase for processing if it does not exist.

        Returns
        -------
        str
            Full path to geodatabase where outputs will be saved

        """
        arcpy.env.workspace = self.work_folder
        checklist_gdb = os.path.join(self.process_path, self.gdb_name) + ".gdb"
        if arcpy.Exists(checklist_gdb):
            self.log.info("Pre-existing gdb folder found at: {}".format(checklist_gdb))
            return checklist_gdb
        else:
            arcpy.CreateFileGDB_management(self.process_path, self.gdb_name, "CURRENT")
            self.log.info("Created PROJ_NAME GDB at: {}".format(checklist_gdb))
            return checklist_gdb

    def parse_email_address(self, email_address):
        """
        Take in an email address and return a usable string ID.

        This function takes in the user-submitted email and address
        and attempts to turn it into an identifier that can be used
        in the process_id folder name.

        Notes
        -----
        The function assumes that the last instance of an '@' is the
        domain and that everything following it (like gmail, or dnr.wa.gov)
        should be dropped. Subsequently all other punctuation is
        dropped. If the email address is very poorly formed (no '@') the
        process folder will just use the AppWorx process ID like before -
        but of course the user will also not be emailed a finished
        checklist :)

        Parameters
        ----------
        email_address: str
            User-input email address

        Returns
        -------
        str

        """
        email = ''.join(email_address.split('@')[:-1])
        return re.sub('[\W_]+', '', email)


def arcpy_defaults(log=None):
    """Set standard arcpy environmental settings.

    This function sets all of the arcpy settings that are
    used most commonly in FRD. The optional logging parameter
    allows sending a message to the log file.

    Parameters
    ----------
    log: logging object, optional
        module-level logger

    Returns
    -------
    None
        Changes environmental settings (side effect)
    """
    arcpy.env.overwriteOutput = True
    arcpy.SetLogHistory(False)
    arcpy.env.pyramid = "None"
    arcpy.env.rasterStatistics = "STATISTICS"
    arcpy.env.XYResolution = "0.0005 METERS"
    arcpy.env.XYTolerance = "0.001 METERS"
    arcpy.env.outputCoordinateSystem = 2927  # WASPSNAD83HARNFEET
    if log:
        log.info("Arcpy defaults set")


def read_in_clip(in_fc, out_fc, ropa_path, where_clause="", intersect_lyr=None, clip_fc=None):
    """Read in ROPA data and constrain it by a clip, query, and/or intersection.

    Make a clipped ArcGIS feature class from ROPA based upon:

        1. an optional SQL query
        2. optional clip by layer, and
        3. optional select by location from spatial extent of another layer

    Defaults will simply copy in all features.

    Parameters
    ----------
    in_fc: str
        Feature class name in corporate (ROPA/SHARED_LM/SHARED_LRM).
        Example: :code:`'ROPA.ROADS'`
    out_fc: str
        Full path name where output should be saved
    ropa_path: str
        ROPA base path
    where_clause: str, optional
        SQL query
    intersect_lyr: str, optional
        Feature layer with which to intersect the input
    clip_fc: str, optional
        Feature class with which to clip the input

    Returns
    -------
    None
        Writes to disk (side effect)

    """
    in_fc = os.path.join(ropa_path, in_fc)
    arcpy.MakeFeatureLayer_management(in_fc, 'fl', where_clause)
    if intersect_lyr:
        arcpy.SelectLayerByLocation_management('fl', 'INTERSECT', intersect_lyr)

    if clip_fc:
        arcpy.Clip_analysis('fl', clip_fc, out_fc)
    else:
        arcpy.CopyFeatures_management('fl', out_fc)


def main(args):

    try:
        # debugging = args[5]  # 'False'
        debugging = 'False'

        # Set up folders and loggers

        # Check out standard arcpy things
        # arcpy_defaults(log=log)

        # After creating this 'arcpy logger' you can run alog.log() to
        # get any arcpy messages you want
        # alog = ArcpyLog(log, mem.log_level)

        # Set data sources here

        # Actually run the analyses..

    except Exception as e:
        logging.exception("Fatal error in main program: ")
        sys.exit("\n{}\nScript failed - exiting now.".format(e))
    finally:
        logging.shutdown()


if __name__ == '__main__':
    main(sys.argv[1:])
