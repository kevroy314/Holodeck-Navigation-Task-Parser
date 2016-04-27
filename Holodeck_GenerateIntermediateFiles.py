import os
import logging
import argparse
import datetime
import Holodeck_HelperFunctions

# Parse inputs
parser = argparse.ArgumentParser(
    description='This script will take a folder containing subject data for the Holodeck Navigation Task and ' +
                'generate CSV files containing the meta-data of interest as requested by the script options. The ' +
                'default is for all data to be generated in a folder adjacent to this script tagged with the current ' +
                'data and time. To speed processing, this can be restricted to particular subsets of the meta-data. ' +
                'If any one option is given to specify a subset of processing, the script will, by default, exclude ' +
                'subsets of data not included as options.')
parser.add_argument('path', help='The full input path to the folder containing the data to be parsed.')
parser.add_argument('--full_study_path', dest='full_study_path', action='store_true',
                    help='Generates study_path.csv containing relevant study path variables.')
parser.set_defaults(full_study_path=False)
parser.add_argument('--full_study_look', dest='full_study_look', action='store_true',
                    help='Generates study_look.csv containing relevant study look variables.')
parser.set_defaults(full_study_look=False)
parser.add_argument('--full_test_path', dest='full_test_path', action='store_true',
                    help='Generates test_path.csv containing relevant test path variables.')
parser.set_defaults(full_test_path=False)
parser.add_argument('--full_test_look', dest='full_test_look', action='store_true',
                    help='Generates test_look.csv containing relevant test look variables.')
parser.set_defaults(full_test_look=False)
parser.add_argument('--full_practice_path', dest='full_practice_path', action='store_true',
                    help='Generates practice_path.csv containing relevant practice path variables.')
parser.set_defaults(full_practice_path=False)
parser.add_argument('--full_practice_look', dest='full_practice_look', action='store_true',
                    help='Generates practice_look.csv containing relevant practice look variables.')
parser.set_defaults(full_practice_look=False)
parser.add_argument('--full_test_2d', dest='full_test_2d', action='store_true',
                    help='Generates 2d_test.csv containing relevant 2D test results.')
parser.set_defaults(full_test_2d=False)
parser.add_argument('--full_test_vr', dest='full_test_vr', action='store_true',
                    help='Generates vr_test.csv containing relevant 2D test results.')
parser.set_defaults(full_test_vr=False)

parser.add_argument('--exclude_incomplete_trials', dest='exclude_incomplete_trials', action='store_true',
                    help='Exclude any trials that don\'t have all expected files in a trial (default=True).')
parser.set_defaults(exclude_incomplete_trials=True)

parser.add_argument('--min_num_trials', default=4, type=int,
                    help='Minimum number of valid, complete trials necessary to include subject in output (default=1).')

parser.add_argument('--log_level', default=20, type=int,
                    help='Logging level of the application (default=20/INFO). ' +
                         'See https://docs.python.org/2/library/logging.html#levels for more info.')
parser.set_defaults(log_level=20)

args = parser.parse_args()

# Configure the output logger
logging.basicConfig(format="%(levelname)s (%(asctime)s): %(message)s", level=args.log_level)

# Handle case where no optional arguments excluding processing are provided in which case all optional
# args are assumed to be true (for convenience)
if not (args.full_study_path or args.full_study_look or args.full_test_path or
        args.full_test_look or args.full_practice_path or args.full_practice_look or
        args.full_test_2d or args.full_test_vr):
    args.full_study_path = True
    args.full_study_look = True
    args.full_test_path = True
    args.full_test_look = True
    args.full_practice_path = True
    args.full_practice_look = True
    args.full_test_2d = True
    args.full_test_vr = True
    logging.info("No command line arguments found. Defaulting all true.")

logging.info("Done parsing command line arguments.")

# Populate list of files, recursively
files = []
for walk_root, walk_dirs, walk_files in os.walk(args.path):
    for f in walk_files:
        files.append(os.path.join(walk_root, f))

# Check if there aren't any files and early stop if there aren't
if not files:
    logging.error("No files found in directory. Closing without creation of output files.")
    exit()

logging.info("Found %d files. Attempting to catalog filenames by Individual, Trial, and Phase" % len(files))

# Stores filenames for individuals in a data structure for easy handling
individuals, excluded, non_matching = Holodeck_HelperFunctions.catalog_files(files,
                                                                             args.min_num_trials,
                                                                             args.exclude_incomplete_trials)

logging.info(("Done cataloging files. %d individuals found which conform to the trial minimum (%d). " +
              "%d files not matching any expected filename format. %d files excluded on input criteria.")
             % (len(individuals), args.min_num_trials, len(non_matching), len(excluded)))

# In debug mode, print excluded files
for filename in excluded:
    logging.debug("%s was excluded." % filename)

# Create the output directory
output_directory = os.path.join(os.getcwd(), datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
try:
    os.mkdir(output_directory)
    logging.info("Output directory (%s) created." % output_directory)
except OSError, e:
    if e.errno != 17:
        raise
    else:
        logging.info("Output directory (%s) already exists. Continuing..." % output_directory)

logging.info("Creating output files.")

# Generate variable references for the csv writers
full_study_path_writer = None
full_study_look_writer = None
full_test_path_writer = None
full_test_look_writer = None
full_practice_path_writer = None
full_practice_look_writer = None
full_test_2d_writer = None
full_test_vr_writer = None

output_file_pointers = []
output_file_pointer = None

# Create the appropriate output files for the options requested and write their headers
if args.full_study_path:
    full_study_path_writer, output_file_pointer = \
        Holodeck_HelperFunctions.make_output_file(output_directory,
                                                  "study_path.csv",
                                                  ["subject_id",
                                                   "trial_number", "time",
                                                   "x", "y",
                                                   "z", "room_by_order",
                                                   "room_by_color",
                                                   "items_clicked",
                                                   "distance_from_last_point",
                                                   "time_since_last_point"])
output_file_pointers.append(output_file_pointer)
if args.full_study_look:
    full_study_look_writer, output_file_pointer = \
        Holodeck_HelperFunctions.make_output_file(output_directory,
                                                  "study_look.csv",
                                                  ["subject_id",
                                                   "trial_number", "time",
                                                   "x", "y",
                                                   "z", "w", "euler_x",
                                                   "euler_y", "euler_z",
                                                   "room_by_order",
                                                   "room_by_color",
                                                   "items_clicked",
                                                   "distance_from_last_point",
                                                   "time_since_last_point"])
output_file_pointers.append(output_file_pointer)
if args.full_test_path:
    full_test_path_writer, output_file_pointer = \
        Holodeck_HelperFunctions.make_output_file(output_directory,
                                                  "test_path.csv",
                                                  ["subject_id",
                                                   "trial_number", "time", "x",
                                                   "y",
                                                   "z", "room_by_order",
                                                   "room_by_color",
                                                   "items_clicked",
                                                   "distance_from_last_point",
                                                   "time_since_last_point"])
output_file_pointers.append(output_file_pointer)
if args.full_test_look:
    full_test_look_writer, output_file_pointer = \
        Holodeck_HelperFunctions.make_output_file(output_directory,
                                                  "test_look.csv",
                                                  ["subject_id",
                                                   "trial_number", "time", "x",
                                                   "y",
                                                   "z", "w", "euler_x",
                                                   "euler_y", "euler_z",
                                                   "room_by_order",
                                                   "room_by_color",
                                                   "items_clicked",
                                                   "distance_from_last_point",
                                                   "time_since_last_point"])
output_file_pointers.append(output_file_pointer)
if args.full_practice_path:
    full_practice_path_writer, output_file_pointer = \
        Holodeck_HelperFunctions.make_output_file(output_directory,
                                                  "practice_path.csv",
                                                  ["subject_id",
                                                   "trial_number", "time",
                                                   "x",
                                                   "y",
                                                   "z", "room_by_order",
                                                   "room_by_color",
                                                   "items_clicked",
                                                   "distance_from_last_point",
                                                   "time_since_last_point"])
output_file_pointers.append(output_file_pointer)
if args.full_practice_look:
    full_practice_look_writer, output_file_pointer = \
        Holodeck_HelperFunctions.make_output_file(output_directory,
                                                  "practice_look.csv",
                                                  ["subject_id",
                                                   "trial_number", "time",
                                                   "x",
                                                   "y",
                                                   "z", "w", "euler_x",
                                                   "euler_y", "euler_z",
                                                   "room_by_order",
                                                   "room_by_color",
                                                   "items_clicked",
                                                   "distance_from_last_point",
                                                   "time_since_last_point"])
output_file_pointers.append(output_file_pointer)
if args.full_test_2d:
    full_test_2d_writer, output_file_pointer = \
        Holodeck_HelperFunctions.make_output_file(output_directory,
                                                  "2d_test.csv",
                                                  ["subject_id", "trial_number",
                                                   "item_id",
                                                   "x_placed", "y_placed",
                                                   "x_expected", "y_expected",
                                                   "order_clicked_study",
                                                   "expected_room_by_order",
                                                   "expected_room_by_color",
                                                   "actual_room_by_order",
                                                   "actual_room_by_color"])
output_file_pointers.append(output_file_pointer)
if args.full_test_vr:
    full_test_vr_writer, output_file_pointer = \
        Holodeck_HelperFunctions.make_output_file(output_directory,
                                                  "vr_test.csv",
                                                  ["subject_id", "trial_number",
                                                   "item_id",
                                                   "x_placed", "y_placed",
                                                   "x_expected", "y_expected",
                                                   "order_clicked_study",
                                                   "expected_room_by_order",
                                                   "expected_room_by_color",
                                                   "actual_room_by_order",
                                                   "actual_room_by_color",
                                                   "number_of_replacements",
                                                   "time_placed"])
output_file_pointers.append(output_file_pointer)

logging.info("Parsing input files.")

# Parse each individual and contribute their data to the appropriate file if possible
count = 1
for individual in individuals:
    logging.info("Parsing Individual %s (%d/%d)." % (individual.subject_id, count, len(individuals)))
    count += 1
    trial_count = 1
    for trial in individual.trials:
        logging.info("Parsing Trial %d (%d/%d)." % (trial.num, trial_count, len(individual.trials)))
        trial_count += 1
        if args.full_study_path:
            Holodeck_HelperFunctions.parse_file_and_write(trial.study_path, individual.subject_id, trial.num,
                                                          Holodeck_HelperFunctions.FileType.path_file,
                                                          full_study_path_writer,
                                                          trial.study_summary)
        if args.full_study_look:
            Holodeck_HelperFunctions.parse_file_and_write(trial.study_look, individual.subject_id, trial.num,
                                                          Holodeck_HelperFunctions.FileType.look_file,
                                                          full_study_look_writer,
                                                          trial.study_summary)
        if args.full_test_path:
            Holodeck_HelperFunctions.parse_file_and_write(trial.test_path, individual.subject_id, trial.num,
                                                          Holodeck_HelperFunctions.FileType.path_file,
                                                          full_test_path_writer,
                                                          trial.test_summary)
        if args.full_test_look:
            Holodeck_HelperFunctions.parse_file_and_write(trial.test_look, individual.subject_id, trial.num,
                                                          Holodeck_HelperFunctions.FileType.look_file,
                                                          full_test_look_writer,
                                                          trial.test_summary)
        if args.full_practice_path:
            Holodeck_HelperFunctions.parse_file_and_write(trial.practice_path, individual.subject_id, trial.num,
                                                          Holodeck_HelperFunctions.FileType.path_file,
                                                          full_practice_path_writer,
                                                          trial.practice_summary)
        if args.full_practice_look:
            Holodeck_HelperFunctions.parse_file_and_write(trial.practice_look, individual.subject_id, trial.num,
                                                          Holodeck_HelperFunctions.FileType.look_file,
                                                          full_practice_look_writer,
                                                          trial.practice_summary)
        if args.full_test_2d:
            Holodeck_HelperFunctions.parse_file_and_write(trial.test_2d, individual.subject_id, trial.num,
                                                          Holodeck_HelperFunctions.FileType.test_file_2d,
                                                          full_test_2d_writer,
                                                          trial.study_summary)
        if args.full_test_vr:
            Holodeck_HelperFunctions.parse_file_and_write(trial.test_vr, individual.subject_id, trial.num,
                                                          Holodeck_HelperFunctions.FileType.test_file_vr,
                                                          full_test_vr_writer,
                                                          trial.study_summary)

logging.info("Done parsing input files.")

logging.info("Closing output files.")

# Close all writers if they were opened
for pointer in output_file_pointers:
    Holodeck_HelperFunctions.close_writer(pointer)

logging.info('Parsing complete.')
