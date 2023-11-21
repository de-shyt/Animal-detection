import multiprocessing
import time

from sources import video_sources
from process_image import check_something_unexpected, print_unexpected_objects_info


# Maps animal type to a daemon process where each frame of the video stream is checked for something unexpected
# Keys are the same as in the `video_sources` dictionary.
# Initially, each value is equal to `None`.
daemon_processes = {animal_type: None for animal_type in video_sources.keys()}


def start_daemon_process(animal_type, opened_stream, chat_id):
    """
    Creates and starts a daemon process. Inside the process, frames from a live stream are taken and processed in order to find unexpected objects.

    Args:
        animal_type: Type of animal which corresponding daemon process should be started.
        opened_stream: A stream of type `CamGear` where animals of the specified type can be found.
        chat_id: ID of the Telegram chat where the resulting image should be sent to.
    """
    global daemon_processes

    # Check that the given animal type is valid
    if animal_type not in daemon_processes.keys():
        raise Exception(f"Unknown animal type '{animal_type}'. Cannot start a daemon process.")

    # Check that the daemon process has not been started yet
    if daemon_processes[animal_type] is not None:
        return

    # If `opened_stream` is None, it means the user does not monitor the animal of the specified type.
    if opened_stream is None:
        return

    # Create a daemon process and start it
    print(f"Staring daemon process for '{animal_type}'...\n")
    new_daemon_process = multiprocessing.Process(
        target=find_unexpected_objects_in_daemon(opened_stream, animal_type, chat_id))
    daemon_processes[animal_type] = new_daemon_process
    new_daemon_process.start()


def terminate_daemon_process(animal_type):
    """
    Terminates a daemon process.
    :param animal_type: Type of animal which corresponding daemon process should be terminated.
    """
    global daemon_processes

    # Check that the given animal type is valid
    if animal_type not in daemon_processes.keys():
        raise Exception(f"Unknown animal of type '{animal_type}'. Cannot start a daemon process.")

    if daemon_processes[animal_type] is not None:
        # Terminate the process
        print(f"Terminating daemon process for '{animal_type}'...\n")
        daemon_processes[animal_type].terminate()
        daemon_processes[animal_type] = None


def find_unexpected_objects_in_daemon(video_stream, animal_type, chat_id):
    """
    Processes the frames, which are extracted from the video stream, and checks if there are objects unexpected for the given stream.

    Args:
        video_stream: An instance of `CamGear` -- an opened stream source.
        animal_type: Type of animals which are expected to be seen on the video.
        chat_id: ID of the Telegram chat where the resulting image should be sent to.
    """
    if animal_type is None:
        raise Exception("Animal type should not be None.")

    while video_stream is not None:
        time.sleep(10)

        # Process frame
        frame = video_stream.read()
        if frame is None:
            break

        file_name, unexpected_objects = check_something_unexpected(frame, animal_type)
        print_unexpected_objects_info(animal_type, unexpected_objects)

        # Send photo to the bot if something unexpected was found
        if len(unexpected_objects) > 0:
            photo = open(file_name, 'rb')
            bot.send_photo(chat_id, photo,
                           f"Ого, у {get_genitive(animal_type)} "
                           f"неожиданно обнаружен(ы) объект(ы) типа {', '.join(map(repr, unexpected_objects))}!")
